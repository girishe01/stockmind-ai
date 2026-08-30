from backend.app.services.financial_service import get_fundamental_metrics


def _score_growth(metrics: dict) -> float:
    revenue_cagr_5y = metrics.get("revenue_cagr_5y")
    eps_cagr_5y = metrics.get("eps_cagr_5y")

    score = 0

    # Revenue growth: maximum 12 points
    if revenue_cagr_5y is not None:
        if revenue_cagr_5y >= 0.20:
            score += 12
        elif revenue_cagr_5y >= 0.15:
            score += 11
        elif revenue_cagr_5y >= 0.10:
            score += 9
        elif revenue_cagr_5y >= 0.05:
            score += 6
        elif revenue_cagr_5y > 0:
            score += 3

    # EPS growth: maximum 13 points
    if eps_cagr_5y is not None:
        if eps_cagr_5y >= 0.20:
            score += 13
        elif eps_cagr_5y >= 0.15:
            score += 11
        elif eps_cagr_5y >= 0.10:
            score += 9
        elif eps_cagr_5y >= 0.05:
            score += 6
        elif eps_cagr_5y > 0:
            score += 3

    return score


def _score_profitability(metrics: dict) -> float:
    net_margin = metrics.get("net_margin")

    if net_margin is None:
        return 0

    if net_margin >= 0.30:
        return 25
    if net_margin >= 0.20:
        return 22
    if net_margin >= 0.15:
        return 18
    if net_margin >= 0.10:
        return 14
    if net_margin >= 0.05:
        return 8

    return 2


def _score_cash_flow(metrics: dict) -> float:
    fcf_margin = metrics.get("fcf_margin")
    fcf_cagr_5y = metrics.get("fcf_cagr_5y")
    fcf_growth_1y = metrics.get("fcf_growth_1y")
    fcf_consecutive_declines = metrics.get(
        "fcf_consecutive_declines",
        0,
    )

    if fcf_margin is None:
        return 0

    score = 0

    # FCF margin: max 15 points
    if fcf_margin >= 0.20:
        score += 15
    elif fcf_margin >= 0.15:
        score += 12
    elif fcf_margin >= 0.10:
        score += 9
    elif fcf_margin >= 0.05:
        score += 5

    # Long-term FCF growth: max 10 points
    if fcf_cagr_5y is not None:
        if fcf_cagr_5y >= 0.15:
            score += 10
        elif fcf_cagr_5y >= 0.10:
            score += 8
        elif fcf_cagr_5y >= 0.05:
            score += 6
        elif fcf_cagr_5y > 0:
            score += 3

    # Recent deterioration penalty
    if fcf_consecutive_declines >= 3:
        score -= 5
    elif fcf_consecutive_declines == 2:
        score -= 3
    elif fcf_consecutive_declines == 1:
        score -= 1

    # Extra penalty for a severe latest-year drop
    if (
        fcf_growth_1y is not None
        and fcf_growth_1y <= -0.20
    ):
        score -= 2

    return max(score, 0)


def _score_balance_sheet(metrics: dict) -> float:
    debt_to_equity = metrics.get("debt_to_equity")
    current_ratio = metrics.get("current_ratio")

    score = 0

    if debt_to_equity is not None:
        if debt_to_equity <= 0.25:
            score += 15
        elif debt_to_equity <= 0.50:
            score += 12
        elif debt_to_equity <= 1.00:
            score += 8
        elif debt_to_equity <= 2.00:
            score += 4

    if current_ratio is not None:
        if current_ratio >= 1.5:
            score += 10
        elif current_ratio >= 1.2:
            score += 8
        elif current_ratio >= 1.0:
            score += 5

    return score


def get_fundamental_score(cik: str) -> dict:
    metrics = get_fundamental_metrics(cik)

    growth_score = _score_growth(metrics)
    profitability_score = _score_profitability(metrics)
    cash_flow_score = _score_cash_flow(metrics)
    balance_sheet_score = _score_balance_sheet(metrics)

    total_score = (
        growth_score
        + profitability_score
        + cash_flow_score
        + balance_sheet_score
    )

    return {
        "fundamental_score": total_score,
        "max_score": 100,
        "components": {
            "growth": growth_score,
            "profitability": profitability_score,
            "cash_flow": cash_flow_score,
            "balance_sheet": balance_sheet_score,
        },
        "metrics": metrics,
    }
