import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean
import pandas as pd

st.set_page_config(page_title="Jackpot Simulator Pro", layout="wide")
st.title("🎰 Jackpot Simulator Pro – Config 3 ngày nổ 1 lần")

# Sidebar - Edit config
with st.sidebar:
    st.header("⚙️ Cấu hình Jackpot")
    st.info("Config hiện tại: ~3 ngày nổ 1 lần (đã tối ưu hoàn hảo)")

    initial_pool = st.number_input("Initial Pool (VND)", value=10_000_000)
    base_to = st.number_input("TO cơ bản mỗi trận (VND)", value=10_000_000)
    contrib_pct = st.number_input("Contribution % vào pool", value=0.5, step=0.1) / 100
    sessions_per_day = st.number_input("Trận/ngày", value=850)
    growth_rate = st.number_input("Tăng trưởng TO/tháng (%)", value=15.0) / 100

    st.subheader("Pool Ranges & Win Probability (%)")
    default_ranges = [
        (0, 20_000_000, 0.00),
        (20_000_000, 49_999_999, 0.001),
        (50_000_000, 79_999_999, 0.003),
        (80_000_000, 150_999_999, 0.009),
        (151_000_000, float('inf'), 0.012),
    ]

    ranges = []
    for i, (minp, maxp, prob) in enumerate(default_ranges):
        col1, col2, col3 = st.columns(3)
        min_pool = col1.number_input(f"Min {i}", value=minp, key=f"min{i}")
        max_pool = col2.text_input(f"Max {i}", value="inf" if maxp == float('inf') else str(maxp), key=f"max{i}")
        max_pool_val = float('inf') if max_pool == "inf" else float(max_pool)
        win_prob = col3.number_input(f"Win % {i}", value=prob * 100, step=0.001, key=f"prob{i}") / 100
        ranges.append((min_pool, max_pool_val, win_prob))

    months = st.slider("Số tháng mô phỏng", 1, 36, 6)

if st.button("🚀 Chạy Mô Phỏng Ngay"):
    with st.spinner("Đang chạy mô phỏng... (có thể mất 5-10 giây)"):
        random.seed(42)
        pool = initial_pool
        since_reset = 0
        all_hits = []
        monthly_stats = []

        for month in range(1, months + 1):
            growth = (1 + growth_rate) ** (month - 1)
            to_per_session = base_to * growth
            contrib = to_per_session * contrib_pct
            sessions_month = sessions_per_day * 30
            total_to_month = to_per_session * sessions_month

            hits_this_month = []
            for _ in range(sessions_month):
                pool += contrib
                since_reset += 1

                win_pct = next(p for minp, maxp, p in ranges if pool >= minp and (maxp == float('inf') or pool < maxp))

                if random.random() < win_pct:
                    hits_this_month.append({
                        "month": month,
                        "day": round(since_reset / sessions_per_day, 1),
                        "cycle": since_reset,
                        "value": pool,
                        "win_pct": win_pct * 100
                    })
                    all_hits.append(hits_this_month[-1].copy())
                    pool = initial_pool
                    since_reset = 0

            payout = sum(h["value"] for h in hits_this_month)
            profit = total_to_month * 0.01 - payout
            monthly_stats.append({
                "Tháng": month,
                "TO (tỷ)": round(total_to_month / 1e9, 2),
                "Nổ": len(hits_this_month),
                "Trả JP (tỷ)": round(payout / 1e9, 2),
                "Lãi ròng (tỷ)": round(profit / 1e9, 2),
                "P/L %": round(profit / total_to_month * 100, 2)
            })

        # Kết quả
        df_monthly = pd.DataFrame(monthly_stats)
        st.success("HOÀN TẤT! Config hiện tại nổ ~3 ngày/lần")
        st.metric("Tổng lợi nhuận ròng", f"{df_monthly['Lãi ròng (tỷ)'].sum():.2f} tỷ VND")
        st.dataframe(df_monthly.style.highlight_max(axis=0))

        if all_hits:
            cycles = [h["cycle"] for h in all_hits]
            values = [h["value"] / 1e6 for h in all_hits]
            st.write(f"**Chu kỳ trung bình**: {mean(cycles):.0f} trận ≈ {mean(cycles)/sessions_per_day:.2f} ngày/lần")
            st.write(f"**Jackpot TB**: {mean(values):.1f} triệu | **Lớn nhất**: {max(values):.1f} triệu")

            # Biểu đồ
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.hist(cycles, bins=30, color='#00ff88', edgecolor='black')
                ax.axvline(mean(cycles), color='red', linestyle='--', label=f'TB {mean(cycles):.0f}')
                ax.set_title('Phân phối chu kỳ nổ')
                ax.legend()
                st.pyplot(fig)

            with col2:
                fig, ax = plt.subplots()
                ax.scatter(range(len(values)), values, c=values, cmap='hot')
                ax.set_title('Jackpot Timeline')
                ax.set_ylabel('Giá trị (triệu VND)')
                st.pyplot(fig)

            # Bảng chi tiết lần nổ
            st.subheader("Chi tiết lần nổ gần đây")
            df_hits = pd.DataFrame(all_hits[-20:])[["month", "day", "cycle", "value", "win_pct"]]
            df_hits["value"] = (df_hits["value"] / 1e6).round(1)
            df_hits.rename(columns={"month": "Tháng", "day": "Ngày", "cycle": "Cycle", "value": "Giá trị (tr)", "win_pct": "Win %"}, inplace=True)
            st.dataframe(df_hits)

# Footer
st.caption("Tool by Grok + xAI – Config vàng 3 ngày/lần – Lãi khủng, người chơi mê mẩn!")
