import random
import pandas as pd

def get_win_prob(pool, pool_ranges):
    for r in pool_ranges:
        min_p, max_p, prob = r
        if min_p <= pool < max_p:
            return prob
    return 0


def simulate_month(
    days,
    sessions_per_day,
    initial_pool,
    to_per_session,
    contribute_percent,
    pool_ranges,
    month_index,
    seed=None
):
    if seed:
        random.seed(seed)

    contribute_value = to_per_session * contribute_percent / 100
    pool = initial_pool
    sessions_since_reset = 0
    jackpot_events = []

    daily_rows = []
    global_sessions = 0

    for day in range(1, days + 1):
        day_to = 0
        day_payout = 0
        jackpot_list = []

        for _ in range(sessions_per_day):
            global_sessions += 1
            sessions_since_reset += 1
            day_to += to_per_session
            pool += contribute_value

            win_prob = get_win_prob(pool, pool_ranges)

            if random.random() < (win_prob / 100):
                jackpot_events.append({
                    "month": month_index,
                    "cycle": sessions_since_reset,
                    "value": pool,
                    "win_prob": win_prob / 100
                })

                jackpot_list.append(pool)
                day_payout += pool
                pool = initial_pool
                sessions_since_reset = 0

        daily_rows.append({
            "day": day,
            "month": month_index,
            "TO": day_to,
            "jackpot_payout": day_payout,
            "net_pl": day_to - day_payout,
            "jackpots": jackpot_list,
        })

    df = pd.DataFrame(daily_rows)
    df_jp = pd.DataFrame(jackpot_events)

    return df, df_jp


def simulate_full(
    months,
    sessions_per_day,
    initial_pool,
    to_per_session,
    contribute_percent,
    pool_ranges,
    growth_percent
):
    all_month_df = []
    all_jp_df = []
    current_to = to_per_session

    for m in range(1, months + 1):
        df_month, df_jp = simulate_month(
            days=30,
            sessions_per_day=sessions_per_day,
            initial_pool=initial_pool,
            to_per_session=current_to,
            contribute_percent=contribute_percent,
            pool_ranges=pool_ranges,
            month_index=m,
            seed=m
        )

        df_jp["month"] = m

        all_month_df.append(df_month)
        all_jp_df.append(df_jp)

        current_to *= (1 + growth_percent / 100)

    return pd.concat(all_month_df), pd.concat(all_jp_df)
