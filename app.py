import streamlit as st
import pandas as pd
from jackpot_engine import simulate_jackpot
import plotly.express as px

st.set_page_config(page_title="Jackpot Simulator PRO", layout="wide")

st.title("💥 Jackpot Simulator PRO – Full Version")


# =========================
# INPUT
# =========================
col1, col2, col3 = st.columns(3)
months = col1.number_input("Số tháng mô phỏng", 1, 36, 6)
matches_per_month = col2.number_input("Số trận / tháng", 100, 200000, 27000)
base_pool = col3.number_input("Giá trị hủ ban đầu", 1_000_000, 50_000_000, 10_000_000)

col4, col5, col6 = st.columns(3)
contribute_percent = col4.number_input("% contribute theo TO", 0.0001, 0.1, 0.003)
stake_per_match = col5.number_input("TO mỗi trận", 1_000_000, 50_000_000, 10_000_000)
growth_rate = col6.number_input("% tăng trưởng TO mỗi tháng", 0.0, 0.3, 0.05)


st.subheader("⚙️ Config Win Probability by Pool Range")
win_config = []
for i in range(4):
    cols = st.columns(3)
    min_v = cols[0].number_input(f"Min range {i+1}", 0, 1_000_000_000, i*10_000_000)
    max_v = cols[1].number_input(f"Max range {i+1}", 1, 2_000_000_000, (i+1)*10_000_000)
    prob = cols[2].number_input(f"Win prob {i+1}", 0.00001, 1.0, 0.0003)
    win_config.append({"min": min_v, "max": max_v, "prob": prob})


run = st.button("🚀 RUN SIMULATION")


if run:
    st.success("Running simulation...")

    hit_records, summary, timeline = simulate_jackpot(
        months=months,
        matches_per_month=matches_per_month,
        base_pool=base_pool,
        contribute_percent=contribute_percent,
        stake_per_match=stake_per_match,
        growth_rate=growth_rate,
        win_config=win_config
    )

    df_hits = pd.DataFrame(hit_records)
    df_summary = pd.DataFrame(summary)
    df_timeline = pd.DataFrame(timeline)

    # =======================
    # Detailed Hit Records
    # =======================
    st.header("🧨 Detailed Hit Records")
    if len(df_hits) > 0:
        df_hits = df_hits.reset_index().rename(columns={"index": "stt"})
        st.dataframe(df_hits, width="stretch")
    else:
        st.info("Không có lần nổ nào.")

    # =======================
    # Monthly Summary
    # =======================
    st.header("📊 Monthly Summary")
    st.dataframe(df_summary, width="stretch")

    # =======================
    # Statistics
    # =======================
    st.header("📈 Statistics")

    total_hits = len(df_hits)
    sessions_per_day = matches_per_month / 30
    avg_cycle = df_hits["cycle"].mean() if total_hits > 0 else 0
    avg_jp = df_hits["value"].mean() if total_hits > 0 else 0

    st.metric("Total Hits", total_hits)
    st.metric("Sessions / Day", round(sessions_per_day))
    st.metric("TO Growth Rate", f"{growth_rate*100:.2f}% / month")
    st.metric("Avg Cycle", round(avg_cycle))
    st.metric("Avg Jackpot", f"{avg_jp:,.0f} VND")

    # =======================
    # Jackpot Timeline Chart
    # =======================
    st.header("📉 Jackpot Timeline (Pool Value vs Session)")

    fig = px.line(df_timeline, x="session", y="value", title="Jackpot Pool Over Time")
    st.plotly_chart(fig, use_container_width=True)
