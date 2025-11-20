import streamlit as st
import pandas as pd
import plotly.express as px
from jackpot_engine import simulate_month, monte_carlo

st.set_page_config(page_title="Jackpot Simulator PRO", layout="wide")

st.title("🎰 Jackpot Simulator – Volta Balance PRO")

# --------------------------
# LEFT SIDEBAR CONFIG
# --------------------------

with st.sidebar:
    st.header("⚙️ Simulation Config")

    months = st.number_input("Months to simulate", 1, 36, 3)
    sessions = st.number_input("Sessions per day", 100, 2000, 850)
    init_pool = st.number_input("Initial pool value", 1_000_000, 50_000_000, 10_000_000, step=1_000_000)
    to_per_session = st.number_input("TO per session", 1_000_000, 30_000_000, 10_000_000, step=1_000_000)
    contribute = st.number_input("Contribution %", 0.1, 5.0, 0.5)

    st.subheader("📊 Turnover Growth")
    growth_pct = st.number_input("Monthly TO Growth %", 0.0, 100.0, 15.0)

    st.subheader("🏆 Win Probability Table")
    st.markdown("Nhập theo format: **min, max, win_prob%**")

    rows = st.number_input("Number of range rows", 1, 10, 5)

    pool_ranges = []
    for i in range(rows):
        c1, c2, c3 = st.columns(3)
        min_p = c1.number_input(f"Min Pool {i+1}", 0, 5_000_000_000, 0)
        max_p = c2.number_input(f"Max Pool {i+1}", 0, 5_000_000_000, 20_000_000)
        prob = c3.number_input(f"Win % {i+1}", 0.0, 100.0, 0.0)
        pool_ranges.append((min_p, max_p, prob))

# --------------------------
# RUN SIMULATION
# --------------------------
if st.button("🚀 Run Simulation"):
    st.success("Running...")

    current_to = to_per_session
    df_all = []

    for m in range(months):
        df = simulate_month(
            days=30,
            sessions_per_day=sessions,
            initial_pool=init_pool,
            to_per_session=current_to,
            contribute_percent=contribute,
            pool_ranges=pool_ranges
        )
        df["month"] = m + 1
        df_all.append(df)

        current_to *= (1 + growth_pct/100)

    df_final = pd.concat(df_all)

    st.subheader("📌 Monthly Summary")
    summary = df_final.groupby("month")[["TO", "jackpot_payout", "net_pl"]].sum()
    st.dataframe(summary)

    fig = px.line(summary, y=["TO", "jackpot_payout", "net_pl"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # Export download
    st.download_button(
        "📥 Download CSV",
        df_final.to_csv().encode("utf-8"),
        "jackpot_result.csv",
        "text/csv"
    )

# --------------------------
# MONTE CARLO
# --------------------------
st.header("📈 Monte-Carlo Analysis")

runs = st.number_input("Monte-Carlo Runs", 10, 3000, 200)

if st.button("Run Monte-Carlo"):
    st.info("Running Monte-Carlo...")
    mc = monte_carlo(
        runs=runs,
        days=30,
        sessions_per_day=sessions,
        initial_pool=init_pool,
        to_per_session=to_per_session,
        contribute_percent=contribute,
        pool_ranges=pool_ranges
    )

    df_mc = pd.DataFrame({"P/L": mc})
    fig2 = px.histogram(df_mc, x="P/L", nbins=40)
    st.plotly_chart(fig2, use_container_width=True)

    st.write("Mean P/L:", df_mc["P/L"].mean())
    st.write("Worst Case:", df_mc["P/L"].min())
    st.write("Best Case:", df_mc["P/L"].max())
