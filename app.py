import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Jackpot Simulator PRO", layout="wide")
st.title("💥 Jackpot Simulator PRO – Option B (Fixed Version)")

# =============================
# INPUT CONFIG
# =============================
st.sidebar.header("⚙️ Config mô phỏng")

months = st.sidebar.number_input("Số tháng mô phỏng", 1, 60, 6)
sessions_per_day = st.sidebar.number_input("Số sessions mỗi ngày", 100, 3000, 900)
base_pool = st.sidebar.number_input("Giá trị hủ ban đầu", 1_000_000, 100_000_000, 10_000_000)
config_percent = st.sidebar.number_input("% contribute (0.00001 → 1.00000)", 0.00001, 1.0, 0.003, format="%.5f")
stake_value = st.sidebar.number_input("TO / session", 1_000_000, 50_000_000, 10_000_000)
growth_rate = st.sidebar.number_input("% tăng trưởng TO / tháng", 0.0, 5.0, 1.0)
win_threshold = st.sidebar.number_input("Ngưỡng jackpot", 1_000_000, 100_000_000, 15_000_000)
win_chance = st.sidebar.number_input("Win probability (0 → 1)", 0.0, 1.0, 0.0008, format="%.5f")

# =============================
# SIMULATION
# =============================
def simulate_month(days, sessions, base_pool, config_percent, stake_value, win_threshold, win_chance):
    pool = base_pool
    total_to = 0
    jp_count = 0
    jp_paid = 0
    records = []

    for d in range(days):
        for s in range(sessions):
            total_to += stake_value
            pool += stake_value * config_percent

            # Check jackpot
            if pool >= win_threshold or random.random() < win_chance:
                jp_count += 1
                jp_paid += pool
                records.append({"cycle": s + d*sessions, "value": round(pool, 0)})
                pool = base_pool

    profit = total_to * config_percent - jp_paid
    pl_percent = profit / total_to

    summary = {
        "total_to": total_to / 1_000_000_000,
        "jp_count": jp_count,
        "jp_paid": jp_paid / 1_000_000_000,
        "profit": profit / 1_000_000,
        "pl_percent": pl_percent * 100
    }

    return summary, records


# =============================
# RUN SIMULATION ALL MONTHS
# =============================

all_month_records = []
monthly_summary = []
df_jp = pd.DataFrame()

sessions_month = sessions_per_day * 30

for m in range(1, months + 1):
    summary, records = simulate_month(
        30,
        sessions_per_day,
        base_pool,
        config_percent,
        stake_value,
        win_threshold,
        win_chance
    )

    for r in records:
        r["month"] = m
    all_month_records.extend(records)

    monthly_summary.append({
        "month": m,
        "TO (tỷ)": round(summary["total_to"], 2),
        "Nổ (lần)": summary["jp_count"],
        "Trả JP (tỷ)": round(summary["jp_paid"], 2),
        "Lãi ròng (triệu)": round(summary["profit"], 1),
        "P/L (%)": f"{summary['pl_percent']:.2f}%"
    })

df_jp = pd.DataFrame(all_month_records)
df_sum = pd.DataFrame(monthly_summary)

# =============================
# LAST 10 JACKPOTS TABLE
# =============================
st.header("🧨 BẢNG 10 LẦN NỔ GẦN ĐÂY NHẤT")

if len(df_jp) > 0:
    df_last10 = df_jp.sort_values("month", ascending=False).tail(10)[["month", "cycle", "value"]]
    df_last10.rename(columns={
        "month": "Tháng",
        "cycle": "Cycle",
        "value": "Giá trị (VND)"
    }, inplace=True)

    st.dataframe(df_last10, width=900)
else:
    st.info("Chưa có jackpot nào trong mô phỏng.")

# =============================
# MONTHLY SUMMARY TABLE
# =============================
st.header("📊 CHI TIẾT TỪNG THÁNG")

st.dataframe(df_sum, width=1200)

# =============================
# STATISTIC BLOCK
# =============================
st.header("📈 Statistics")

total_hits = df_jp.shape[0]
avg_cycle = df_jp["cycle"].mean() if total_hits > 0 else 0
avg_jp_value = df_jp["value"].mean() if total_hits > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("Tổng số lần nổ", total_hits)
col2.metric("Avg Cycle (sessions)", f"{avg_cycle:,.0f}")
col3.metric("Avg Jackpot (VND)", f"{avg_jp_value:,.0f}")

# =============================
# JACKPOT TIMELINE
# =============================
st.header("📉 Jackpot Timeline")

if len(df_jp) > 0:
    st.line_chart(df_jp[["cycle", "value"]].set_index("cycle"))
else:
    st.info("Không có dữ liệu để vẽ biểu đồ.")
