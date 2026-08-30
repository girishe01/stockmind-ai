from datetime import date

from backend.app.services.sec_service import get_company_facts


REVENUE_TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
]

NET_INCOME_TAGS = [
    "NetIncomeLoss",
    "ProfitLoss",
]

def get_annual_net_income_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = company_facts.get("facts", {}).get("us-gaap", {})

    return _extract_annual_fact_history(
        us_gaap_facts,
        NET_INCOME_TAGS,
        "USD",
    )

def _get_first_available_fact(
    us_gaap_facts: dict,
    possible_tags: list[str],
) -> dict | None:
    for tag in possible_tags:
        if tag in us_gaap_facts:
            return us_gaap_facts[tag]

    return None


def _is_annual_period(item: dict) -> bool:
    start = item.get("start")
    end = item.get("end")

    if not start or not end:
        return False

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)

    duration_days = (end_date - start_date).days

    return 300 <= duration_days <= 380
def _extract_annual_fact_history(
    us_gaap_facts: dict,
    possible_tags: list[str],
    unit: str,
) -> list[dict]:
    fact = _get_first_available_fact(
        us_gaap_facts,
        possible_tags,
    )

    if fact is None:
        return []

    values = fact.get("units", {}).get(unit, [])

    periods = {}

    for item in values:
        if item.get("form") != "10-K":
            continue

        if item.get("fp") != "FY":
            continue

        if not _is_annual_period(item):
            continue

        period_end = item["end"]

        existing = periods.get(period_end)

        if existing is None or item.get("filed", "") > existing.get("filed", ""):
            periods[period_end] = {
                "fiscal_year": int(period_end[:4]),
                "period_start": item["start"],
                "period_end": period_end,
                "value": item["val"],
                "filed": item.get("filed"),
                "accession_number": item.get("accn"),
            }

    return sorted(
        periods.values(),
        key=lambda item: item["period_end"],
    )

def get_annual_revenue_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = company_facts.get("facts", {}).get("us-gaap", {})

    return _extract_annual_fact_history(
        us_gaap_facts,
        REVENUE_TAGS,
        "USD",
    )

    if revenue_fact is None:
        return []

    usd_values = revenue_fact.get("units", {}).get("USD", [])

    periods = {}

    for item in usd_values:
        if item.get("form") != "10-K":
            continue

        if item.get("fp") != "FY":
            continue

        if not _is_annual_period(item):
            continue

        period_end = item["end"]

        existing = periods.get(period_end)

        if existing is None or item.get("filed", "") > existing.get("filed", ""):
            periods[period_end] = {
                "fiscal_year": int(period_end[:4]),
                "period_start": item["start"],
                "period_end": period_end,
                "value": item["val"],
                "filed": item.get("filed"),
                "accession_number": item.get("accn"),
            }

    return sorted(
        periods.values(),
        key=lambda item: item["period_end"],
    )


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> float | None:
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return None

    return (end_value / start_value) ** (1 / years) - 1


def get_revenue_growth_metrics(cik: str) -> dict:
    revenue_history = get_annual_revenue_history(cik)

    metrics = {
        "latest_revenue": None,
        "latest_period_end": None,
        "revenue_cagr_3y": None,
        "revenue_cagr_5y": None,
    }

    if not revenue_history:
        return metrics

    latest = revenue_history[-1]

    metrics["latest_revenue"] = latest["value"]
    metrics["latest_period_end"] = latest["period_end"]

    if len(revenue_history) >= 4:
        start = revenue_history[-4]

        metrics["revenue_cagr_3y"] = calculate_cagr(
            start["value"],
            latest["value"],
            3,
        )

    if len(revenue_history) >= 6:
        start = revenue_history[-6]

        metrics["revenue_cagr_5y"] = calculate_cagr(
            start["value"],
            latest["value"],
            5,
        )

    return metrics

def get_net_margin_history(cik: str) -> list[dict]:
    revenue_history = get_annual_revenue_history(cik)
    net_income_history = get_annual_net_income_history(cik)

    revenue_by_period = {
        item["period_end"]: item
        for item in revenue_history
    }

    margins = []

    for net_income_item in net_income_history:
        period_end = net_income_item["period_end"]

        revenue_item = revenue_by_period.get(period_end)

        if revenue_item is None:
            continue

        revenue = revenue_item["value"]
        net_income = net_income_item["value"]

        if revenue == 0:
            continue

        margins.append(
            {
                "fiscal_year": net_income_item["fiscal_year"],
                "period_end": period_end,
                "revenue": revenue,
                "net_income": net_income,
                "net_margin": net_income / revenue,
            }
        )

    return margins