import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean

from jackpot_engine import simulate_session, fmt_money

st.set_page_config(page_title="Jackpot Simulator Simple", layout="wide")
st.title("🎰 Jackpot Simulator — Simple Version")

# =====================
# SIDEBAR CONFIG
# =====================
st.sidebar.header("⚙️ Simulation Config")

months = st.sidebar.number_input("Số tháng mô phỏng", 1, 36, 6)
sessions_month = st.sidebar.number_input("Số trận mỗi tháng", 1000, 100000, 25500)
initial_pool = st.sidebar.number_input("Giá trị hủ ban đầu (VND)", 1_000_000, 50_000_000, 10_000_000)

contribute_percent = st.sidebar.number_input(
    "% Contribute theo TO trận",
    0.000001, 100.0, 0.5
) / 100

to_per_session = st.sidebar.number_input("TO / trận", 1_000_000, 50_000_000, 10_000_000)
growth_rate = st.sidebar.number_input("% tăng trưởng / tháng", 0.0, 100.0, 15.0) / 100

# =====================
# Pool Ranges
# =====================
st.sidebar.subheader("🎲 Pool Ranges & Win Probability (%)")

default_ranges = [
    (0, 15_000_000, 0.001),
    (15_000_000, 40_000_000, 0.005),
    (40_000_000, 80_000_000, 0.02),
    (80_000_000, 150_000_000, 0.05),
    (150_000_000, float('inf'), 0.3)
]

pool_ranges = []
for i in range(5):
    st.sidebar.write(f"Range {i+1}")
    min_v = st.sidebar.number_input(f"Min {i+1}", 0, 5_000_000_000, default_ranges[i][0])
    max_raw = st.sidebar.text_input(
        f"Max {i+1}",
        value="inf" if default_ranges[i][1] == float('inf') else str(default_ranges[i][1]),
        key=f"max_{i}"
    )
    max_v = float('inf') if max_raw == "inf" else int(max_raw)
    winp = st.sidebar.number_input(
        f"Win% {i+1}",
        0.000001, 100.0,
        default_ranges[i][2],
        step=0.000001
    )
    pool_ranges.append((min_v, max_v, winp))

# =====================
# RUN SIM
# =====================
if st.sidebar.button("▶️ RUN"):
    st.header("📊 Simulation Output")

    pool = initial_pool
    total_to = 0
    total_payout = 0
    hits = []
    hit_detail = []
    hit_id = 1
    since_reset = 0

    monthly_stats = []

    for m in range(1, months + 1):
        growth = (1 + growth_rate) ** (m - 1)
        to_session_g = to_per_session * growth
        contrib = to_session_g * contribute_percent

        payout_month = 0
        hit_count_month = 0
        month_to = to_session_g * sessions_month

        for s in range(1, sessions_month + 1):
            total_to += to_session_g
            since_reset += 1

            is_win, pool, wp = simulate_session(pool, contrib, pool_ranges)

            if is_win:
                hits.append((m, since_reset, pool, wp))
                hit_detail.append({
                    "STT": hit_id,
                    "Tháng": m,
                    "Số Match": since_reset,
                    "Tiền Hủ": fmt_money(pool)
                })
                hit_id += 1

                payout_month += pool
                total_payout += pool
                hit_count_month += 1

                pool = initial_pool
                since_reset = 0

        pl_before = month_to * 0.01
        pl_after = pl_before - payout_month

        monthly_stats.append({
            "Tháng": m,
            "TO": month_to,
            "Payout": payout_month,
            "PL_before": pl_before,
            "PL_after": pl_after,
            "%PL": pl_after / month_to * 100,
            "Hits": hit_count_month
        })

    # =====================
    # SUMMARY METRICS
    # =====================
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total TO", fmt_money(total_to))
    with c2:
        st.metric("Total Payout", fmt_money(total_payout))
    with c3:
        st.metric("P/L (1% TO)", fmt_money(total_to * 0.01))
    with c4:
        st.metric("Net P/L", fmt_money(total_to * 0.01 - total_payout))

    # =====================
    # Detailed hit table
    # =====================
    st.subheader("📋 Detailed Hits (First 30)")
    st.dataframe(pd.DataFrame(hit_detail[:30]), hide_index=True)

    # =====================
    # Monthly summary
    # =====================
    st.subheader("📅 Monthly Summary")

    df = []
    for row in monthly_stats:
        df.append({
            "Tháng": row["Tháng"],
            "TO (B)": f"{row['TO']/1e9:.2f}",
            "Payout (B)": f"{row['Payout']/1e9:.3f}",
            "PL Before (B)": f"{row['PL_before']/1e9:.3f}",
            "PL After (B)": f"{row['PL_after']/1e9:.3f}",
            "% P/L": f"{row['%PL']:.2f}%",
            "Hits": row["Hits"]
        })
    st.dataframe(pd.DataFrame(df), hide_index=True)

    # =====================
    # Statistics
    # =====================
    st.subheader("📈 Statistics")

    if hits:
        cycles = [h[1] for h in hits]
        values = [h[2] for h in hits]

        st.write(f"**Total Hits:** {len(hits)}")
        st.write(f"**Avg Cycle:** {mean(cycles):.1f} sessions")
        st.write(f"**Avg Jackpot:** {fmt_money(mean(values))}")

    # =====================
    # Charts
    # =====================
    st.subheader("📉 Charts")

    if hits:
        cycles = [h[1] for h in hits]
        values = [h[2] / 1e6 for h in hits]

        fig, axs = plt.subplots(1, 2, figsize=(14, 5))

        # 1 — Cycle histogram
        axs[0].hist(cycles, bins=20, color="steelblue")
        axs[0].set_title("Cycle Distribution")
        axs[0].set_xlabel("Sessions")

        # 2 — Value over time
        axs[1].plot(values, marker="o")
        axs[1].set_title("Jackpot Value Over Time")
        axs[1].set_ylabel("M VND")

        st.pyplot(fig)

st.sidebar.write("---")
st.sidebar.write("Jackpot Simulator Simple v1.0")
