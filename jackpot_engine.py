import random
import pandas as pd


def get_win_probability(pool_value, win_config):
    """
    win_config = [
        {"min": 10_000_000, "max": 20_000_000, "prob": 0.0002},
        {"min": 20_000_000, "max": 30_000_000, "prob": 0.0005},
        {"min": 30_000_000, "max": 50_000_000, "prob": 0.001},
        {"min": 50_000_000, "max": 999_000_000, "prob": 0.003}
        {"min": 100_000_000, "max": 1999_000_000, "prob": 0.003}
    ]
    """
    for cfg in win_config:
        if cfg["min"] <= pool_value < cfg["max"]:
            return cfg["prob"]
    return 0


def simulate_jackpot(
    months,
    matches_per_month,
    base_pool,
    contribute_percent,
    stake_per_match,
    growth_rate,
    win_config,
):
    """
    Trả về:
    - hit_records (list)
    - monthly_summary (list)
    - timeline (list of pool values)
    """
    hit_records = []
    monthly_summary = []
    timeline = []

    global_session_index = 0

    current_stake = stake_per_match

    for month in range(1, months + 1):
        month_to = 0
        month_pool_profit = 0
        month_pool_cost = 0

        pool = base_pool
        cycles = 0

        for match in range(1, matches_per_month + 1):
            global_session_index += 1
            cycles += 1

            # contribute
            pool += current_stake * contribute_percent
            month_to += current_stake

            # win chance
            prob = get_win_probability(pool, win_config)
            if random.random() < prob:
                hit_records.append({
                    "month": month,
                    "match": match,
                    "global_session": global_session_index,
                    "value": round(pool),
                    "cycle": cycles,
                })

                month_pool_cost += pool
                pool = base_pool
                cycles = 0

            timeline.append({"session": global_session_index, "value": pool})

        # P/L
        month_pool_profit = month_to * contribute_percent
        pl_before_jp = month_pool_profit
        pl_after_jp = month_pool_profit - month_pool_cost

        monthly_summary.append({
            "month": month,
            "to": round(month_to),
            "pool_contribute": round(month_pool_profit),
            "jp_cost": round(month_pool_cost),
            "pl_before": round(pl_before_jp),
            "pl_after": round(pl_after_jp),
            "pl_percent": round(pl_after_jp / month_to * 100, 3)
        })

        # tăng trưởng TO
        current_stake *= (1 + growth_rate)

    return hit_records, monthly_summary, timeline
