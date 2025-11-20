import random
import pandas as pd

def simulate_month(
    month_index,
    sessions_per_month=27000,
    base_pool=10_000_000,
    config_percent=0.003,
    to_per_session=10_000_000,
    win_config=None
):
    """
    Trả về:
    - detailed_df: bảng từng lần nổ
    - final_pool: giá trị hủ cuối tháng
    - total_to: tổng TO tháng
    - total_jp_paid: tổng jackpot trả
    """
    if win_config is None:
        win_config = [
            {"min": 15_000_000, "max": 30_000_000, "prob": 0.001},
            {"min": 30_000_000, "max": 50_000_000, "prob": 0.0005},
            {"min": 50_000_000, "max": 80_000_000, "prob": 0.0003},
            {"min": 80_000_000, "max": 120_000_000, "prob": 0.00015},
            {"min": 120_000_000, "max": 200_000_000, "prob": 0.0001},
        ]

    pool = base_pool
    total_to = 0
    records = []
    cycle = 0

    for _ in range(sessions_per_month):
        cycle += 1
        total_to += to_per_session
        pool += to_per_session * config_percent

        # check jackpot win config
        for cfg in win_config:
            if cfg["min"] <= pool <= cfg["max"]:
                if random.random() < cfg["prob"]:
                    # jackpot hit
                    records.append({
                        "month": month_index,
                        "cycle": cycle,
                        "value": pool,
                        "win_prob": cfg["prob"]
                    })
                    pool = base_pool
                    cycle = 0
                    break

    total_jp_paid = sum([r["value"] for r in records])
    detailed_df = pd.DataFrame(records)
    return detailed_df, pool, total_to, total_jp_paid


def simulate_month_multi(
    runs=100,
    sessions_per_month=27000,
    base_pool=10_000_000,
    config_percent=0.003,
    to_per_session=10_000_000,
    win_config=None
):
    """
    Chạy 1 tháng nhiều lần → Output 10 cột:
    run, total_wins, avg_win_value, max_win_value,
    min_win_value, end_pool, final_total_to, total_jp_paid,
    profit, profit_percent
    """
    results = []

    for i in range(1, runs + 1):
        df, final_pool, total_to, total_jp = simulate_month(
            month_index=1,
            sessions_per_month=sessions_per_month,
            base_pool=base_pool,
            config_percent=config_percent,
            to_per_session=to_per_session,
            win_config=win_config
        )

        total_wins = len(df)
        avg_win = df["value"].mean() if total_wins > 0 else 0
        max_win = df["value"].max() if total_wins > 0 else 0
        min_win = df["value"].min() if total_wins > 0 else 0

        profit = (total_to * config_percent) - total_jp
        profit_percent = (profit / total_to * 100) if total_to > 0 else 0

        results.append({
            "run": i,
            "total_wins": total_wins,
            "avg_win_value": avg_win,
            "max_win_value": max_win,
            "min_win_value": min_win,
            "end_pool": final_pool,
            "final_total_to": total_to,
            "total_jp_paid": total_jp,
            "profit": profit,
            "profit_percent": profit_percent
        })

    return pd.DataFrame(results)
