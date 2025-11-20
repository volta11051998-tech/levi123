import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go

# ============================
# CONFIG PAGE
# ============================
st.set_page_config(
    page_title="Volta MD5 Jackpot Simulator PRO",
    layout="wide"
)

# ============================
# CSS THEME (Dark Premium)
# ============================
st.markdown("""
<style>
    body {
        background-color: #0d0d0d !important;
    }
    .main {
        background-color: #0d0d0d !important;
        color: #FFFFFF !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff930f, #ff3d00);
        color: white;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        border: none;
    }
    .stNumberInput>div>div>input {
        background-color: #1c1c1c !important;
        color: white !important;
        border-radius: 6px;
        border: 1px solid #444;
    }
    .stTextInput>div>div>input {
        background-color: #1c1c1c !important;
        color: white !important;
        border-radius: 6px;
        border: 1px solid #333;
    }
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# FORMAT FUNCTION
# ============================
def fmt(v):
    return f"{v:,.0f}"

def fmt_float(v):
    return f"{v:,.2f}"

# ============================
# SIMULATION CORE
# ============================
def simulate(full_months,
             sessions_per_day,
             initial_pool,
             contribute_percent,
             to_per_session,
             growth_per_month,
             pool_ranges):

    hit_logs = []
    monthly_rows = []

    pool = initial_pool
    monthly_TO = to_per_session * sessions_per_day * 30
    session_idx = 0

    for month in range(1, full_months+1):

        total_to = 0
        jp_paid = 0
        jp_count = 0

        for day in range(30):
            for _ in range(sessions_per_day):
                session_idx += 1
                total_to += to_per_session

                pool += to_per_session * contribute_percent

                # Determine win chance by pool ranges
                win_percent = 0
                for rmin, rmax, p in pool_ranges:
                    if rmin <= pool <= rmax:
                        win_percent = p
                        break

                if random.random() < win_percent:
                    hit_logs.append({
                        "month": month,
                        "cycle": session_idx,
                        "value": pool
                    })
                    jp_count += 1
                    jp_paid += pool
                    pool = initial_pool

        profit = (total_to * contribute_percent) - jp_paid
        pl_percent = profit / total_to * 100

        monthly_rows.append({
            "month": month,
            "TO": total_to,
            "jp_count": jp_count,
            "jp_paid": jp_paid,
            "profit": profit,
            "pl_percent": pl_percent
        })

        monthly_TO *= (1 + growth_per_month)

    return hit_logs, monthly_rows

# ============================
# SIDEBAR CONFIG
# ============================
st.sidebar.header("⚙️ Config mô phỏng")

months = st.sidebar.number_input("Số tháng mô phỏng", 1, 60, 6)
sessions_day = st.sidebar.number_input("Số sessions mỗi ngày", 100, 2000, 900)
initial_pool = st.sidebar.number_input("Giá trị hủ ban đầu", 1_000_000, 50_000_000, 10_000_000)
contribute_percent = st.sidebar.number_input(
    "% contribute (0.00000001 → 1.00000000)",
    min_value=0.00000001,
    max_value=1.0,
    value=0.005,
    format="%.8f",
)

to_per_session = st.sidebar.number_input("TO / session", 1_000_000, 50_000_000, 10_000_000)
growth = st.sidebar.number_input("% tăng trưởng TO / tháng", 0.0, 2.0, 1.0)

# Editable pool ranges
st.sidebar.subheader("📌 Pool Ranges & Win Probability (%)")

default_ranges = [
    (0, 15_000_000, 0.00010000),
    (15_000_000, 40_000_000, 0.00050000),
    (40_000_000, 80_000_000, 0.00100000),
    (80_000_000, 150_000_000, 0.00200000),
    (150_000_000, 500_000_000, 0.00500000),
]

pool_ranges = []
for i in range(5):
    st.sidebar.write(f"Range {i+1}")

    r1 = st.sidebar.number_input(
        f"Min {i+1}",
        min_value=0,
        max_value=5_000_000_000,
        value=default_ranges[i][0],
        key=f"rmin{i}",
        format="%d",
    )

    r2 = st.sidebar.number_input(
        f"Max {i+1}",
        min_value=0,
        max_value=5_000_000_000,
        value=default_ranges[i][1],
        key=f"rmax{i}",
        format="%d",
    )

    wp = st.sidebar.number_input(
        f"Win % {i+1}",
        min_value=0.00000001,
        max_value=1.0,
        value=float(default_ranges[i][2]),
        key=f"wp{i}",
        format="%.8f",
    )

    pool_ranges.append((r1, r2, wp))
# ============================
# RUN BUTTON
# ============================
if st.sidebar.button("🚀 Run Simulation"):
    hit_logs, monthly_rows = simulate(
        months,
        sessions_day,
        initial_pool,
        contribute_percent,
        to_per_session,
        growth,
        pool_ranges
    )

    st.title("💥 Volta MD5 Jackpot Simulator PRO – Version A")

    # HIT TABLE
    st.header("🔔 BẢNG 10 LẦN NỔ GẦN ĐÂY NHẤT")
    df_hit = pd.DataFrame(hit_logs).sort_values("cycle", ascending=False).head(10)
    df_hit["value_fmt"] = df_hit["value"].apply(fmt)
    st.dataframe(df_hit[["month", "cycle", "value_fmt"]])

    # MONTHLY SUMMARY
    st.header("📊 CHI TIẾT TỪNG THÁNG")
    df_mon = pd.DataFrame(monthly_rows)
    df_mon["TO_fmt"] = df_mon["TO"] / 1_000_000_000
    df_mon["jp_paid_bil"] = df_mon["jp_paid"] / 1_000_000_000
    df_mon["profit_mil"] = df_mon["profit"] / 1_000_000
    df_mon["pl_fmt"] = df_mon["pl_percent"].apply(lambda x: f"{x:.2f}%")

    st.dataframe(df_mon[["month","TO_fmt","jp_count","jp_paid_bil","profit_mil","pl_fmt"]])

    # STATISTICS
    st.header("📈 STATISTICS")
    st.write(f"• Tổng số lần nổ: **{len(hit_logs)}**")
    st.write(f"• Avg Cycle (sessions/hit): **{fmt(len(hit_logs) and (max([h['cycle'] for h in hit_logs]) / len(hit_logs)) or 0)}**")
    st.write(f"• Growth/month: **{growth*100:.2f}%**")
    st.write(f"• Sessions/day: **{sessions_day}**")

    # TIMELINE CHART
    st.header("📌 Jackpot Timeline (Cycle → Value)")
    if len(hit_logs) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[h["cycle"] for h in hit_logs],
            y=[h["value"] for h in hit_logs],
            mode="lines+markers",
            line=dict(width=2),
            marker=dict(size=6)
        ))
        fig.update_layout(
            template="plotly_dark",
            height=400,
            xaxis_title="Cycle",
            yaxis_title="Jackpot Value"
        )
        st.plotly_chart(fig, use_container_width=True)
