import random

def pick_win_percent(pool, pool_ranges):
    """Return win% based on pool."""
    for min_v, max_v, prob in pool_ranges:
        if pool >= min_v and (pool < max_v or max_v == float('inf')):
            return prob
    return 0.0


def simulate_session(pool, contrib, pool_ranges):
    """Simulate one session and check jackpot."""
    pool += contrib
    win_percent = pick_win_percent(pool, pool_ranges)
    is_win = random.random() < (win_percent / 100.0)
    return is_win, pool, win_percent


def fmt_money(v):
    """Format money into M/B/T for readability."""
    if v >= 1e12:
        return f"{v/1e12:.2f} T"
    if v >= 1e9:
        return f"{v/1e9:.2f} B"
    if v >= 1e6:
        return f"{v/1e6:.2f} M"
    return f"{v:,.0f}"
