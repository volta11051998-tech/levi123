import random
import pandas as pd

# ============================
# SHORT FORMAT CONVERSION
# ============================

def short_number(n):
    """Convert number to 10K / 10M / 1.2B format."""
    try:
        n = float(n)
    except:
        return n

    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    elif abs(n) >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    elif abs(n) >= 1_000:
        return f"{n/1_000:.2f}K"
    return f"{n:,.0f}"


# ============================
# SIMULATE ONE FULL MONTH
# ============================

def simulate_month(
    days,
    sessions_per_day,
    base_pool,
    contribute_percent,
    to_per_session,
    win_config
):
    pool = base_pool
    total_to = 0
    records = []
    month_jps = []

    session_index = 0

    for d in range(days):
        for _ in range(sessions_per_day):
            stake = to_per_session
            session_index += 1
            total_to += stake
            pool += stake * contribute_percent

            # find current win % based on pool range
            current_prob = 0
            for row in win_config:
                if row["min"] <= pool <= row["max"]:
                    current_prob = row["prob"]
                    break

            is_jp = random.random() < (current_prob / 100)

            if is_jp:
                month_jps.append({
                    "session": session_index,
                    "value": pool,
                    "win_prob": current_prob
                })
                pool = base_pool

    return {
        "total_to": total_to,
        "jackpots": month_jps,
        "ending_pool": pool
    }


# ============================
# MULTI-MONTH SIMULATION
# ============================

def simulate_n_months(
    months,
    base_sessions,
    base_pool,
    contribute_percent,
    to_per_session,
    growth_rate,
    win_config
):

    all_jp = []
    monthly_summary = []

    current_sessions = base_sessions
    current_to = to_per_session

    for m in range(1, months + 1):

        result = simulate_month(
            days=30,
            sessions_per_day=current_sessions,
            base_pool=base_pool,
            contribute_percent=contribute_percent,
            to_per_session=current_to,
            win_config=win_config
        )

        total_to = result["total_to"]
        jp_paid = sum(j["value"] for j in result["jackpots"])
        jp_count = len(result["jackpots"])

        profit_before = total_to * 0.01
        final_profit = profit_before - jp_paid
        pl_after = final_profit / total_to * 100 if total_to > 0 else 0

        for j in result["jackpots"]:
            all_jp.append({
                "month": m,
                "session": j["session"],
                "value": j["value"],
                "win_prob": j["win_prob"]
            })

        monthly_summary.append({
            "month": m,
            "to": total_to,
            "jp_count": jp_count,
            "jp_paid": jp_paid,
            "profit_before": profit_before,
            "profit_after": final_profit,
            "pl_after": pl_after
        })

        # growth
        current_sessions = int(current_sessions * (1 + growth_rate))
        current_to = int(current_to * (1 + growth_rate))

    df_jp = pd.DataFrame(all_jp)
    df_month = pd.DataFrame(monthly_summary)

    return df_jp, df_month


# ============================
# MONTE CARLO - RUN X TIMES
# ============================

def monte_carlo_month(
    runs,
    sessions,
    base_pool,
    contribute_percent,
    to_per_session,
    win_config
):
    results = []

    for _ in range(runs):
        r = simulate_month(
            days=30,
            sessions_per_day=sessions,
            base_pool=base_pool,
            contribute_percent=contribute_percent,
            to_per_session=to_per_session,
            win_config=win_config
        )
        results.append(r)

    df = pd.DataFrame([{
        "jackpot_hits": len(r["jackpots"]),
        "max_jp": max([j["value"] for j in r["jackpots"]], default=0),
        "avg_jp": (sum([j["value"] for j in r["jackpots"]]) / len(r["jackpots"])) if len(r["jackpots"]) > 0 else 0
    } for r in results])

    return df
