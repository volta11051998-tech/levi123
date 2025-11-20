import streamlit as st
import pandas as pd
from jackpot_engine import simulate_month

st.set_page_config(page_title="Jackpot Simulator PRO", layout="wide")

st.title("💥 Jackpot Simulator PRO – Option B (Fixed Version)")

# ============================
# INPUT PANEL
# ============================
col1, col2, col3, col4 = st.columns(4)

months = col1.number_input("Số tháng mô phỏng", 1, 12, 6)
sessions = col2.number_input("Sessions / ngày", 100, 2000, 900)
base_pool = col3.number_input("Giá trị hủ ban đầu (VND)", 1_000_000, 50_000_000, 10_000_000)
config_percent = col4.number_input("Config % cộng hủ", 0.0001, 0.01, 0.003)

win_threshold = st.number_input("Ngưỡng Jackpot nổ (VND)", 1_000_000, 50_000_000, 15_000_000)
win_chance = st.number_input("Win chance ngẫu nhiên", 0.0001, 0.01, 0.0008)

run_btn = st.button("🚀 Chạy mô phỏng")

if run_btn:
    st.success("Đang chạy mô phỏng...")

    df_all = []
    df_jp = []

    for m in range(1, months + 1):
        result = simulate_month(
            days=30,
            sessions_per_day=sessions,
            base_pool=base_pool,
            config_percent=config_percent,
            win_threshold=win_threshold,
            win_chance=win_chance
        )
        result["month"] = m
        df_all.append(result)

        # Dùng lại để tạo bảng 10 lần nổ
        df_jp.append({
            "month": m,
            "jp_count": result["jp_count"],
            "jp_paid": result["jp_paid"],
            "pl_percent": result["pl_percent"],
        })

    df_all = pd.DataFrame(df_all)
    df_jp = pd.DataFrame(df_jp)

    # =============================
    # BẢNG 10 LẦN NỔ GẦN NHẤT
    # =============================
    st.header("🧨 BẢNG 10 LẦN NỔ GẦN ĐÂY NHẤT (để so sánh với app)")

    df_last10 = df_jp.sort_values("month", ascending=False).head(10)
    df_last10.columns = ["Tháng", "Nổ (lần)", "Giá trị (tỷ)", "Win %"]

    st.dataframe(df_last10, width="stretch")

    # =============================
    # CHI TIẾT TỪNG THÁNG
    # =============================
    st.header("📊 CHI TIẾT TỪNG THÁNG")

    df_month = df_all[["month", "total_to", "jp_count", "jp_paid", "profit", "pl_percent"]]
    df_month.columns = ["Tháng", "TO (tỷ)", "Nổ (lần)", "Trả JP (tỷ)", "Lãi ròng (triệu)", "P/L (%)"]

    st.dataframe(df_month, width="stretch")

    st.success("Hoàn tất mô phỏng!")
