from backend.app.services.financial_service import get_fundamental_metrics
from backend.app.services.sec_service import (
    classify_company_type,
    get_company_submissions,
)


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
    net_debt_to_fcf = metrics.get("net_debt_to_fcf")
    net_debt_to_ocf = metrics.get("net_debt_to_ocf")
    current_ratio = metrics.get("current_ratio")
    debt_to_equity = metrics.get("debt_to_equity")

    score = 0

    # Primary leverage measure: max 12 points
    if net_debt_to_fcf is not None:
        if net_debt_to_fcf <= 0:
            score += 12
        elif net_debt_to_fcf <= 1:
            score += 11
        elif net_debt_to_fcf <= 2:
            score += 8
        elif net_debt_to_fcf <= 3:
            score += 5
        elif net_debt_to_fcf <= 4:
            score += 2

    # Secondary leverage check: max 6 points
    if net_debt_to_ocf is not None:
        if net_debt_to_ocf <= 0:
            score += 6
        elif net_debt_to_ocf <= 1:
            score += 5
        elif net_debt_to_ocf <= 2:
            score += 3
        elif net_debt_to_ocf <= 3:
            score += 1

    # Liquidity: max 4 points
    if current_ratio is not None:
        if current_ratio >= 1.5:
            score += 4
        elif current_ratio >= 1.2:
            score += 3
        elif current_ratio >= 1.0:
            score += 2
        elif current_ratio >= 0.75:
            score += 1

    # Supporting capital-structure signal: max 3 points
    if debt_to_equity is not None:
        if debt_to_equity <= 0.5:
            score += 3
        elif debt_to_equity <= 1.0:
            score += 2
        elif debt_to_equity <= 2.0:
            score += 1

    return score


def _calculate_data_completeness(metrics: dict) -> dict:
    required_metrics = [
        "revenue_cagr_5y",
        "eps_cagr_5y",
        "net_margin",
        "fcf_margin",
        "fcf_cagr_5y",
        "net_debt_to_fcf",
        "net_debt_to_ocf",
        "current_ratio",
        "debt_to_equity",
    ]

    available_count = sum(
        1
        for metric_name in required_metrics
        if metrics.get(metric_name) is not None
    )

    total_count = len(required_metrics)

    completeness = (
        available_count / total_count
    ) * 100

    if completeness >= 85:
        confidence = "high"
    elif completeness >= 65:
        confidence = "medium"
    else:
        confidence = "low"

    missing_metrics = [
        metric_name
        for metric_name in required_metrics
        if metrics.get(metric_name) is None
    ]

    return {
        "data_completeness": round(completeness, 1),
        "confidence": confidence,
        "available_metrics": available_count,
        "required_metrics": total_count,
        "missing_metrics": missing_metrics,
    }

def get_fundamental_score(cik: str) -> dict:
    submissions = get_company_submissions(cik)

    sic = submissions.get("sic")
    sic_description = submissions.get("sicDescription")
    company_type = classify_company_type(sic)

    metrics = get_fundamental_metrics(cik)
    #data_quality = _calculate_data_completeness(metrics)

    if company_type == "financial_company":
        return {
            "score_status": "not_applicable",
            "fundamental_score": None,
            "max_score": 100,
            "company_type": company_type,
            "sic": sic,
            "sic_description": sic_description,
            "data_quality": None,
            "reason": (
                "Financial company detected. "
                "The generic operating-company scoring model is not applicable. "
                "A dedicated financial-company scoring model is required."
            ),
            "components": None,
            "metrics": metrics,
        }

    growth_score = _score_growth(metrics)
    data_quality = _calculate_data_completeness(metrics)
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
        "score_status": "scored",
        "fundamental_score": total_score,
        "max_score": 100,
        "company_type": company_type,
        "sic": sic,
        "sic_description": sic_description,
        "data_quality": data_quality,
        "components": {
            "growth": growth_score,
            "profitability": profitability_score,
            "cash_flow": cash_flow_score,
            "balance_sheet": balance_sheet_score,
        },
        "metrics": metrics,
    }