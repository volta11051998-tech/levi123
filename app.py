import streamlit as st
import pandas as pd
import plotly.express as px
from jackpot_engine import simulate_full

st.set_page_config(page_title="Jackpot Simulator PRO", layout="wide")

st.title("🎰 Jackpot Simulator PRO – Volta Balance")

st.sidebar.header("⚙️ Cấu hình mô phỏng")

months = st.sidebar.number_input("Số tháng mô phỏng", 1, 36, 6)
sessions_per_day = st.sidebar.number_input("Sessions/ngày", 100, 2000, 850)
init_pool = st.sidebar.number_input("Initial Pool", 1_000_000, 50_000_000, 10_000_000)
to_per_session = st.sidebar.number_input("TO mỗi session", 1_000_000, 30_000_000, 20_000_000)
contribute_percent = st.sidebar.number_input("Contribution %", 0.1, 5.0, 0.5)
growth_percent = st.sidebar.number_input("TO Growth % mỗi tháng", 0.0, 50.0, 15.0)

st.sidebar.subheader("📌 Win probability table")
rows = st.sidebar.number_input("Số dòng", 1, 10, 5)

pool_ranges = []
for i in range(rows):
    c1, c2, c3 = st.sidebar.columns(3)
    min_p = c1.number_input(f"Min {i+1}", 0, 5_000_000_000, 0)
    max_p = c2.number_input(f"Max {i+1}", 0, 5_000_000_000, 20_000_000)
    prob = c3.number_input(f"Win% {i+1}", 0.0, 100.0, 0.0)
    pool_ranges.append((min_p, max_p, prob))

if st.sidebar.button("🚀 Run Simulation"):
    st.success("Đang chạy mô phỏng...")

    df_all, df_jp = simulate_full(
        months,
        sessions_per_day,
        init_pool,
        to_per_session,
        contribute_percent,
        pool_ranges,
        growth_percent
    )

    # =============================
    # 🧨 BẢNG 10 LẦN NỔ GẦN NHẤT
    # =============================
    st.header("🧨 BẢNG 10 LẦN NỔ GẦN ĐÂY NHẤT")

    df_last10 = df_jp.sort_values("month", ascending=False).tail(10)[
        ["month", "cycle", "value", "win_prob"]
    ]

    df_last10["value"] = df_last10["value"] / 1_000_000
    df_last10["win_prob"] = df_last10["win_prob"].round(2)

    df_last10.columns = ["Tháng", "Cycle (trận)", "Giá trị (triệu)", "Win %"]

    st.table(df_last10)

    # =============================
    # 📊 CHI TIẾT TỪNG THÁNG
    # =============================
    st.header("📊 CHI TIẾT TỪNG THÁNG")

    summary = df_all.groupby("month").agg({
        "TO": "sum",
        "jackpot_payout": "sum",
        "net_pl": "sum"
    })

    summary["Nổ (lần)"] = df_jp.groupby("month").size()
    summary["TO (tỷ)"] = summary["TO"] / 1_000_000_000
    summary["Trả JP (tỷ)"] = summary["jackpot_payout"] / 1_000_000_000
    summary["Lãi ròng (triệu)"] = summary["net_pl"] / 1_000_000
    summary["P/L (%)"] = summary["net_pl"] / summary["TO"]

    summary = summary[["TO (tỷ)", "Nổ (lần)", "Trả JP (tỷ)", "Lãi ròng (triệu)", "P/L (%)"]]
    st.table(summary.style.format({
        "TO (tỷ)": "{:.2f}",
        "Trả JP (tỷ)": "{:.2f}",
        "Lãi ròng (triệu)": "{:,.0f}",
        "P/L (%)": "{:.2%}"
    }))

    # =============================
    # 📈 BIỂU ĐỒ
    # =============================
    fig = px.line(
        summary,
        y=["TO (tỷ)", "Trả JP (tỷ)", "Lãi ròng (triệu)"],
        markers=True,
        title="📈 Xu hướng theo tháng"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "📥 Download Full CSV",
        df_all.to_csv().encode("utf-8"),
        "jackpot_full.csv",
        "text/csv"
    )
