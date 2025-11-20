import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean

from jackpot_engine import simulate_session, fmt_money

# ====================================
# UI THEME (BINANCE PREMIUM DARK MODE)
# ====================================
st.set_page_config(page_title="Volta MD5 Jackpot Simulator PRO", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0D1117;
    color: #E6EDF3;
}
.block-container {
    padding-top: 2rem;
}
.sidebar .sidebar-content {
    background-color: #111826;
}
.css-1d391kg { color: #E6EDF3 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎰 **Volta MD5 Jackpot Simulator PRO — Binance Dark Premium**")

# ====================================
# SIDEBAR CONFIG
# ====================================
st.sidebar.header("⚙️ Configuration")

months = st.sidebar.number_input("Số tháng mô phỏng", 1, 36, 6)
sessions_month = st.sidebar.number_input("Số trận mỗi tháng", 1000, 100000, 25500)
initial_pool = st.sidebar.number_input("Giá trị hủ ban đầu (VND)", 1_000_000, 50_000_000, 10_000_000)

contribute_percent = st.sidebar.number_input(
    "% Contribute hủ theo TO trận",
    min_value=0.000001,
    max_value=1.0,
    value=0.5,
    step=0.000001
) / 100

to_per_session = st.sidebar.number_input("TO / trận (VND)", 1_000_000, 50_000_000, 10_000_000)

growth_rate = st.sidebar.number_input(
    "% tăng trưởng TO mỗi tháng",
    min_value=0.0,
    max_value=100.0,
    value=15.0
) / 100

# ================================
# POOL RANGES — Premium UI
# ================================
st.sidebar.subheader("🎲 Pool Ranges & Win Probability (%)")

default_ranges = [
    (0, 15_000_000, 0.001),
    (15_000_000, 40_000_000, 0.005),
    (40_000_000, 80_000_000, 0.020),
    (80_000_000, 150_000_000, 0.050),
    (150_000_000, float('inf'), 0.300)
]

pool_ranges = []

for i in range(5):
    st.sidebar.write(f"**Range {i+1}**")
    c1, c2, c3 = st.sidebar.columns(3)

    with c1:
        min_v = st.number_input(
            f"Min {i+1} (VND)",
            min_value=0,
            value=default_ranges[i][0]
        )
    with c2:
        max_raw = st.text_input(
            f"Max {i+1}",
            value="inf" if default_ranges[i][1] == float('inf') else f"{default_ranges[i][1]}"
        )
        max_v = float('inf') if max_raw == "inf" else int(max_raw)
    with c3:
        win_pct = st.number_input(
            f"Win% {i+1}",
            min_value=0.000001, max_value=100.0,
            step=0.000001,
            value=default_ranges[i][2]
        )

    pool_ranges.append((min_v, max_v, win_pct))

# ====================================
# RUN SIMULATION
# ====================================
if st.sidebar.button("▶️ RUN SIMULATION", type="primary"):
    st.header("📊 Simulation Results")

    # Core trackers
    pool = initial_pool
    total_to = 0
    total_payout = 0
    hits = []
    detailed = []
    hit_index = 1
    since_reset = 0

    monthly_summary = []

    for m in range(1, months + 1):
        growth = (1 + growth_rate) ** (m - 1)
        to_session_g = to_per_session * growth
        contrib = to_session_g * contribute_percent

        payout_month = 0
        month_hits = 0
        monthly_to = to_session_g * sessions_month

        for s in range(1, sessions_month + 1):
            total_to += to_session_g
            since_reset += 1

            is_win, pool, wp = simulate_session(pool, contrib, pool_ranges)

            if is_win:
                hits.append((m, since_reset, pool, wp))
                detailed.append({
                    "STT": hit_index,
                    "Tháng": m,
                    "Số Match": since_reset,
                    "Tiền Hủ": fmt_money(pool)
                })
                hit_index += 1

                payout_month += pool
                total_payout += pool
                month_hits += 1

                pool = initial_pool
                since_reset = 0

        pl_before = monthly_to * 0.01
        pl_after = pl_before - payout_month
        pl_percent_after = pl_after / monthly_to * 100

        monthly_summary.append({
            "Tháng": m,
            "TO": monthly_to,
            "Payout": payout_month,
            "PL_before": pl_before,
            "PL_after": pl_after,
            "PL_percent_after": pl_percent_after,
            "Hits": month_hits
        })

    # =============================
    # KEY METRICS
    # =============================
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total TO", fmt_money(total_to))
    with c2:
        st.metric("Total Payout", fmt_money(total_payout))
    with c3:
        st.metric("P/L (1% TO)", fmt_money(total_to * 0.01))
    with c4:
        st.metric("Net P/L", fmt_money(total_to * 0.01 - total_payout))

    # =============================
    # Detailed Hits Table
    # =============================
    st.subheader("📋 Detailed Hit Records")
    st.dataframe(pd.DataFrame(detailed), hide_index=True)

    # =============================
    # Monthly Summary
    # =============================
    st.subheader("📅 Monthly Summary")

    df = []
    for row in monthly_summary:
        df.append({
            "Tháng": row["Tháng"],
            "TO (B)": f"{row['TO']/1e9:.2f}",
            "Payout (B)": f"{row['Payout']/1e9:.3f}",
            "PL Before (B)": f"{row['PL_before']/1e9:.3f}",
            "PL After (B)": f"{row['PL_after']/1e9:.3f}",
            "% P/L After": f"{row['PL_percent_after']:.2f}%",
            "Hits": row["Hits"]
        })

    st.dataframe(pd.DataFrame(df), hide_index=True)

    # =============================
    # Statistics
    # =============================
    st.subheader("📈 Statistics")

    if len(hits) > 0:
        cycles = [h[1] for h in hits]
        values = [h[2] for h in hits]

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Total Hits:** {len(hits)}")
            st.write(f"**Avg Cycle:** {mean(cycles):.1f} sessions")
        with c2:
            st.write(f"**Avg Jackpot:** {fmt_money(mean(values))}")

    # =============================
    # Charts — Binance Style
    # =============================
    st.subheader("📉 Charts")

    if len(hits):
        cycles = [h[1] for h in hits]
        values = [h[2]/1e6 for h in hits]

        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        fig.patch.set_facecolor("#0D1117")

        # Chart styling
        for ax in axs.flatten():
            ax.set_facecolor("#111826")
            ax.tick_params(colors="white")
            ax.title.set_color("white")
            ax.xaxis.label.set_color("white")
            ax.yaxis.label.set_color("white")

        # 1 — Cycle histogram
        axs[0, 0].hist(cycles, bins=30, color="#F0B90B")
        axs[0, 0].set_title("Cycle Distribution (Sessions)")

        # 2 — Jackpot Timeline
        axs[0, 1].plot(cycles, values, color="#F0B90B")
        axs[0, 1].set_title("Jackpot Timeline (Sessions vs Value)")

        # 3 — Jackpot Value
        axs[1, 0].scatter(range(len(values)), values, color="#F0B90B")
        axs[1, 0].set_title("Jackpot Value Over Time (M VND)")

        # 4 — Hits per month
        mm = [h[0] for h in hits]
        axs[1, 1].bar(range(1, months+1), [mm.count(m) for m in range(1, months+1)], color="#F0B90B")
        axs[1, 1].set_title("Hit Count per Month")

        st.pyplot(fig)

st.sidebar.markdown("---")
st.sidebar.write("**Volta MD5 Jackpot Simulator PRO — Binance Edition**")
