import random
import math

# ============================
# Money Formatting Utilities
# ============================

def fmt_money(v):
    """Format VND into M, B, T for readability."""
    if v >= 1_000_000_000_000:
        return f"{v/1e12:.2f} T"
    if v >= 1_000_000_000:
        return f"{v/1e9:.2f} B"
    if v >= 1_000_000:
        return f"{v/1e6:.2f} M"
    return f"{v:,.0f}"

# ============================
# Core Jackpot Simulation Logic
# ============================

def pick_win_percent(pool, pool_ranges):
    """Select correct win probability based on pool value."""
    for min_v, max_v, prob in pool_ranges:
        if (pool >= min_v) and (pool < max_v or max_v == float('inf')):
            return prob
    return 0.0

def simulate_session(pool, contrib, pool_ranges):
    """Simulate one session, returns: (hit, new_pool, used_prob)."""
    pool += contrib
    win_percent = pick_win_percent(pool, pool_ranges)
    is_win = random.random() < (win_percent / 100.0)
    return is_win, pool, win_percent
