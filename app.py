import streamlit as st
import pandas as pd
import plotly.express as px

from jackpot_engine import simulate_month, simulate_month_multi

st.set_page_config(page_title="Volta MD5 Jackpot Simulator PRO", layout="wide")
st.markdown("""
<style>
body {
    background-color: #0D0D0D;
    color: #EAEAEA;
}
.block {
    padding: 20px;
    background: rgba(30,30,30,0.5);
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #333;
}
</style>import streamlit as st
import pandas as pd
import plotly.express as px

from jackpot_engine import (
    simulate_n_months,
    monte_carlo_month,
    short_number
)

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="Jackpot Simulator PRO — Volta MD5",
    layout="wide",
    page_icon="🎰"
)

# ================================
# CUSTOM CSS — VOLTA MD5 REALISTIC
# ================================
st.markdown("""
<style>

body {
    background-color: #0d0f1a;
}

.main > div {
    background: #0d0f1a;
}

.block-container {
    padding-top: 1.5rem;
}

.big-number {
    font-size: 28px;
    font-weight: 700;
    color: #30e0a1;
}

.sub {
    font-size: 14px;
    opacity: 0.7;
}

.card {
    padding: 18px;
    border-radius: 12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)


# ================================
# HEADER
# ================================
st.markdown("<h1 style='color:#30e0a1;'>🎰 Jackpot Simulator PRO — Volta MD5</h1>", unsafe_allow_html=True)
st.markdown("### Realistic Jackpot engine with cycle tracking, multi-month modeling & Monte-Carlo accuracy")


# ================================
# INPUT CONFIG
# ================================
st.sidebar.header("⚙️ Simulation Configuration")

months = st.sidebar.number_input("Số tháng mô phỏng", 1, 60, 6)
sessions = st.sidebar.number_input("Số trận mỗi ngày", 100, 2000, 850)
base_pool = st.sidebar.number_input("Giá trị hủ ban đầu", 1_000_000, 500_000_000, 10_000_000)
contribute_percent = st.sidebar.number_input("% contribute hủ theo TO", 0.00001, 1.00000, 0.00500, format="%.5f")
to_per_session = st.sidebar.number_input("TO mỗi trận", 1_000_000, 50_000_000, 10_000_000)
growth_rate = st.sidebar.number_input("% tăng TO mỗi tháng", 0.0, 1.0, 0.15, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧨 Jackpot Win Probability Config")

win_config = []
default_rows = 5

for i in range(default_rows):
    with st.sidebar.expander(f"Range #{i+1}", expanded=True):
        min_v = st.number_input(f"Min Pool {i+1}", 0, 5_000_000_000, i * 20_000_000)
        max_v = st.number_input(f"Max Pool {i+1}", 1, 5_000_000_000, (i + 1) * 20_000_000)
        prob = st.number_input(f"%Win {i+1}", 0.00001, 1.00000, 0.00500, format="%.5f")
        win_config.append({"min": min_v, "max": max_v, "prob": prob})


# ================================
# RUN SIMULATION
# ================================
st.markdown("## 🚀 Run Multi-Month Simulation")

run_btn = st.button("▶️ RUN SIMULATION", use_container_width=True)

if run_btn:
    df_jp, df_month = simulate_n_months(
        months=months,
        base_sessions=sessions,
        base_pool=base_pool,
        contribute_percent=contribute_percent,
        to_per_session=to_per_session,
        growth_rate=growth_rate,
        win_config=win_config
    )

    # =====================
    # FORMAT OUTPUT
    # =====================
    df_jp_display = df_jp.copy()
    df_jp_display["value"] = df_jp_display["value"].apply(short_number)
    df_jp_display["session"] = df_jp_display["session"].apply(short_number)
    df_jp_display["win_prob"] = df_jp_display["win_prob"].apply(lambda x: f"{x:.5f}%")

    df_month_display = df_month.copy()
    df_month_display["to"] = df_month_display["to"].apply(short_number)
    df_month_display["jp_paid"] = df_month_display["jp_paid"].apply(short_number)
    df_month_display["profit_before"] = df_month_display["profit_before"].apply(short_number)
    df_month_display["profit_after"] = df_month_display["profit_after"].apply(short_number)
    df_month_display["pl_after"] = df_month_display["pl_after"].apply(lambda x: f"{x:.2f}%")

    # =====================
    # SUMMARY CARDS
    # =====================
    total_jp = len(df_jp)
    avg_cycle = df_jp["session"].mean() if total_jp > 0 else 0
    avg_value = df_jp["value"].mean() if total_jp > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.markdown("<div class='card'><div class='big-number'>"
                  f"{short_number(total_jp)}</div><div class='sub'>Total Jackpot Hits</div></div>",
                  unsafe_allow_html=True)

    col2.markdown("<div class='card'><div class='big-number'>"
                  f"{short_number(avg_cycle)}</div><div class='sub'>Avg. Sessions Per Hit</div></div>",
                  unsafe_allow_html=True)

    col3.markdown("<div class='card'><div class='big-number'>"
                  f"{short_number(avg_value)}</div><div class='sub'>Avg. Jackpot Value</div></div>",
                  unsafe_allow_html=True)

    st.markdown("---")

    # =====================
    # DETAILED HIT RECORDS
    # =====================
    st.subheader("🧨 Detailed Jackpot Hit Records")
    st.dataframe(df_jp_display, height=300, use_container_width=True)

    # =====================
    # MONTHLY SUMMARY
    # =====================
    st.subheader("📊 Monthly Summary")
    st.dataframe(df_month_display, height=300, use_container_width=True)

    # =====================
    # JACKPOT TIMELINE
    # =====================
    if len(df_jp) > 0:
        fig = px.scatter(
            df_jp,
            x="session",
            y="value",
            color="month",
            title="Jackpot Timeline (Value vs Session)",
            labels={"value": "Jackpot Value", "session": "Session"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# ======================================================
# MONTE CARLO BLOCK (OPTION 2 — placed at bottom)
# ======================================================

st.markdown("## 🎲 Monte-Carlo Analysis (Run X times for 1 month)")

with st.expander("Run Monte-Carlo Simulation", expanded=False):
    mc_runs = st.number_input("Số lần mô phỏng (Monte-Carlo)", 10, 2000, 100)
    mc_btn = st.button("▶️ Run Monte-Carlo", type="primary")

    if mc_btn:
        df_mc = monte_carlo_month(
            runs=mc_runs,
            sessions=sessions,
            base_pool=base_pool,
            contribute_percent=contribute_percent,

""", unsafe_allow_html=True)

st.title("⚡ Volta MD5 — Jackpot Simulator PRO (Dark Premium)")


# ===============================
# CONFIG INPUTS
# ===============================
with st.sidebar:
    st.header("⚙️ Configuration")

    months = st.number_input("Số tháng mô phỏng", 1, 120, 6)
    sessions = st.number_input("Số trận mỗi tháng", 1000, 100000, 27000)
    base_pool = st.number_input("Giá trị hủ ban đầu", 1_000_000, 200_000_000, 10_000_000)
    config_percent = st.number_input("% Contribute hủ (0.00001 → 1%)", 0.00001, 1.0, 0.003)
    to_per_session = st.number_input("TO mỗi trận", 1_000_000, 50_000_000, 10_000_000)
    growth_rate = st.number_input("% tăng trưởng TO mỗi tháng", 0.0, 50.0, 0.0)

    st.markdown("---")
    st.subheader("Win Range Configs")

    win_config = []
    for i in range(5):
        st.markdown(f"##### Range #{i+1}")
        c1, c2, c3 = st.columns(3)
        min_val = c1.number_input(f"Min {i+1}", 10_000_000, 500_000_000, (i+1) * 15_000_000)
        max_val = c2.number_input(f"Max {i+1}", 20_000_000, 800_000_000, (i+1) * 25_000_000)
        prob_val = c3.number_input(f"Prob {i+1}", 0.000001, 1.0, 0.0005)
        win_config.append({"min": min_val, "max": max_val, "prob": prob_val})


# ===============================
# MAIN SIMULATION
# ===============================
st.header("🎯 Simulation Result")

df_all = []
current_to = to_per_session

for m in range(1, months + 1):
    df, final_pool, total_to, total_jp = simulate_month(
        month_index=m,
        sessions_per_month=sessions,
        base_pool=base_pool,
        config_percent=config_percent,
        to_per_session=current_to,
        win_config=win_config
    )
    df_all.append(df)

    current_to *= (1 + growth_rate / 100)

df_jp = pd.concat(df_all, ignore_index=True)


# ========== OUTPUT 1: HIT RECORDS ==========
st.subheader("🧨 Detailed Hit Records")
st.dataframe(df_jp)


# ========== OUTPUT 2: MONTHLY SUMMARY ==========
st.subheader("📅 Monthly Summary")

summary = []
current_to = to_per_session

for m in range(1, months + 1):
    df = df_jp[df_jp["month"] == m]
    session_to = current_to * sessions
    total_jp = df["value"].sum()

    profit_before = session_to * config_percent
    profit_after = profit_before - total_jp
    pl_percent = profit_after / session_to * 100

    summary.append([
        m,
        session_to,
        total_jp,
        profit_before,
        profit_after,
        pl_percent
    ])

    current_to *= (1 + growth_rate / 100)

summary_df = pd.DataFrame(summary, columns=[
    "Month", "Total TO", "Jackpot Paid",
    "P/L Before JP", "P/L After JP", "P/L %"
])

st.dataframe(summary_df)


# ========== OUTPUT 3: STATISTICS ==========
st.subheader("📊 Statistics")

avg_cycle = df_jp["cycle"].mean() if len(df_jp) > 0 else 0
avg_jp = df_jp["value"].mean() if len(df_jp) > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total Jackpot Hits", len(df_jp))
c2.metric("Avg Cycle", round(avg_cycle, 2))
c3.metric("Avg Jackpot Value", f"{avg_jp:,.0f}")


# ========== OUTPUT 4: TIMELINE CHART ==========
st.subheader("📈 Jackpot Timeline")
if len(df_jp) > 0:
    fig = px.scatter(df_jp, x="cycle", y="value", color="month",
                     title="Jackpot Trigger Timeline")
    st.plotly_chart(fig, use_container_width=True)


# ===============================
# NEW SECTION — MULTI RUN MONTH SIMULATOR
# ===============================
st.markdown("---")
st.header("📦 Multi-Run Monthly Overview (NEW)")

runs = st.number_input("Số lần chạy mô phỏng 1 tháng", 10, 5000, 200)

if st.button("🚀 Run Multi Simulation"):
    df_multi = simulate_month_multi(
        runs=runs,
        sessions_per_month=sessions,
        base_pool=base_pool,
        config_percent=config_percent,
        to_per_session=to_per_session,
        win_config=win_config
    )

    st.success("✔ Done!")
    st.dataframe(df_multi)

    fig2 = px.scatter(df_multi, x="run", y="profit_percent",
                      title="Distribution of Profit (%) per Month")
    st.plotly_chart(fig2, use_container_width=True)
