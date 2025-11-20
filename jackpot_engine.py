import random
import pandas as pd

def simulate_month(days=30, sessions_per_day=900, base_pool=10_000_000, config_percent=0.003, win_threshold=15_000_000, win_chance=0.0008):
    """
    Trả về data frame với các cột:
    month, total_to, jp_count, jp_paid, profit, pl_percent
    """
    pool = base_pool
    total_to = 0
    jp_count = 0
    jp_paid = 0

    for _ in range(days):
        for _ in range(sessions_per_day):
            stake = 10_000_000  # 10M per session TO
            total_to += stake
            pool += stake * config_percent

            # check jackpot
            if pool >= win_threshold or random.random() < win_chance:
                jp_paid += pool
                jp_count += 1
                pool = base_pool  # reset pool

    profit = (total_to * config_percent) - jp_paid
    pl_percent = profit / total_to

    return {
        "total_to": total_to / 1_000_000_000,   # convert to tỷ
        "jp_count": jp_count,
        "jp_paid": round(jp_paid / 1_000_000_000, 2),   # tỷ
        "profit": round(profit / 1_000_000, 0),         # triệu
        "pl_percent": round(pl_percent * 100, 2)        # %
    }
