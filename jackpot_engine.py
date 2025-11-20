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
    seed=None
):
    if seed:
        random.seed(seed)

    contribute_value = to_per_session * contribute_percent / 100

    results = []
    pool = initial_pool
    day_idx = 1
    session_global = 0

    for _ in range(days):
        day_to = 0
        day_payout = 0
        day_jackpots = []

        for s in range(sessions_per_day):
            session_global += 1
            pool += contribute_value
            day_to += to_per_session

            win_prob = get_win_prob(pool, pool_ranges)

            if random.random() < (win_prob / 100):
                day_jackpots.append(pool)
                day_payout += pool
                pool = initial_pool

        results.append({
            "day": day_idx,
            "TO": day_to,
            "jackpot_payout": day_payout,
            "net_pl": day_to - day_payout,
            "jackpots": day_jackpots,
        })

        day_idx += 1

    df = pd.DataFrame(results)
    return df


def monte_carlo(
    runs,
    days,
    sessions_per_day,
    initial_pool,
    to_per_session,
    contribute_percent,
    pool_ranges
):
    outs = []
    for r in range(runs):
        df = simulate_month(
            days,
            sessions_per_day,
            initial_pool,
            to_per_session,
            contribute_percent,
            pool_ranges,
            seed=r
        )
        outs.append(df["net_pl"].sum())
    return outs
