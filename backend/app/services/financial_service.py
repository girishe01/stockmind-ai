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

DILUTED_EPS_TAGS = [
    "EarningsPerShareDiluted",
]

OPERATING_CASH_FLOW_TAGS = [
    "NetCashProvidedByUsedInOperatingActivities",
]

CAPEX_TAGS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
]   

CASH_TAGS = [
    "CashAndCashEquivalentsAtCarryingValue",
]

CURRENT_DEBT_TAGS = [
    "LongTermDebtCurrent",
    "ShortTermBorrowings",
]

LONG_TERM_DEBT_TAGS = [
    "LongTermDebtNoncurrent",
    "LongTermDebt",
]

SHAREHOLDERS_EQUITY_TAGS = [
    "StockholdersEquity",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
]

TOTAL_ASSETS_TAGS = [
    "Assets",
]

TOTAL_LIABILITIES_TAGS = [
    "Liabilities",
]

CURRENT_ASSETS_TAGS = [
    "AssetsCurrent",
]

CURRENT_LIABILITIES_TAGS = [
    "LiabilitiesCurrent",
]

def get_annual_total_assets_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        TOTAL_ASSETS_TAGS,
        "USD",
    )


def get_annual_total_liabilities_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        TOTAL_LIABILITIES_TAGS,
        "USD",
    )


def get_annual_current_assets_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_ASSETS_TAGS,
        "USD",
    )


def get_annual_current_liabilities_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_LIABILITIES_TAGS,
        "USD",
    )

def get_annual_shareholders_equity_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        SHAREHOLDERS_EQUITY_TAGS,
        "USD",
    )

def get_annual_current_debt_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_DEBT_TAGS,
        "USD",
    )


def get_annual_long_term_debt_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        LONG_TERM_DEBT_TAGS,
        "USD",
    )

def get_annual_cash_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_instant_fact_history(
        us_gaap_facts,
        CASH_TAGS,
        "USD",
    )

def get_annual_operating_cash_flow_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_fact_history(
        us_gaap_facts,
        OPERATING_CASH_FLOW_TAGS,
        "USD",
    )


def get_annual_capex_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_fact_history(
        us_gaap_facts,
        CAPEX_TAGS,
        "USD",
    )

def get_annual_net_income_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_fact_history(
        us_gaap_facts,
        NET_INCOME_TAGS,
        "USD",
    )

def get_annual_diluted_eps_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    return _extract_annual_fact_history(
        us_gaap_facts,
        DILUTED_EPS_TAGS,
        "USD/shares",
    )

def _get_first_available_fact(
    us_gaap_facts: dict,
    possible_tags: list[str],
) -> dict | None:
    for tag in possible_tags:
        if tag in us_gaap_facts:
            return us_gaap_facts[tag]

    return None

def _get_us_gaap_facts(company_facts: dict) -> dict:
    return company_facts.get("facts", {}).get("us-gaap", {})


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
def _extract_annual_instant_fact_history(
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

        period_end = item.get("end")

        if not period_end:
            continue

        existing = periods.get(period_end)

        if (
            existing is None
            or item.get("filed", "") > existing.get("filed", "")
        ):
            periods[period_end] = {
                "fiscal_year": int(period_end[:4]),
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

    us_gaap_facts = _get_us_gaap_facts(company_facts)

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

def get_eps_growth_metrics(cik: str) -> dict:
    eps_history = get_annual_diluted_eps_history(cik)

    metrics = {
        "latest_eps": None,
        "latest_period_end": None,
        "eps_cagr_3y": None,
        "eps_cagr_5y": None,
    }

    if not eps_history:
        return metrics

    latest = eps_history[-1]

    metrics["latest_eps"] = latest["value"]
    metrics["latest_period_end"] = latest["period_end"]

    if len(eps_history) >= 4:
        start = eps_history[-4]

        metrics["eps_cagr_3y"] = calculate_cagr(
            start["value"],
            latest["value"],
            3,
        )

    if len(eps_history) >= 6:
        start = eps_history[-6]

        metrics["eps_cagr_5y"] = calculate_cagr(
            start["value"],
            latest["value"],
            5,
        )

    return metrics

def get_net_margin_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    revenue_history = _extract_annual_fact_history(
        us_gaap_facts,
        REVENUE_TAGS,
        "USD",
    )

    net_income_history = _extract_annual_fact_history(
        us_gaap_facts,
        NET_INCOME_TAGS,
        "USD",
    )

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

def get_free_cash_flow_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    operating_cash_flow_history = _extract_annual_fact_history(
        us_gaap_facts,
        OPERATING_CASH_FLOW_TAGS,
        "USD",
    )

    capex_history = _extract_annual_fact_history(
        us_gaap_facts,
        CAPEX_TAGS,
        "USD",
    )

    capex_by_period = {
        item["period_end"]: item
        for item in capex_history
    }

    free_cash_flow_history = []

    for ocf_item in operating_cash_flow_history:
        period_end = ocf_item["period_end"]

        capex_item = capex_by_period.get(period_end)

        if capex_item is None:
            continue

        operating_cash_flow = ocf_item["value"]
        capex = capex_item["value"]

        free_cash_flow_history.append(
            {
                "fiscal_year": ocf_item["fiscal_year"],
                "period_end": period_end,
                "operating_cash_flow": operating_cash_flow,
                "capex": capex,
                "free_cash_flow": operating_cash_flow - capex,
            }
        )

    return free_cash_flow_history


def get_free_cash_flow_margin_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)

    us_gaap_facts = _get_us_gaap_facts(company_facts)

    revenue_history = _extract_annual_fact_history(
        us_gaap_facts,
        REVENUE_TAGS,
        "USD",
    )

    operating_cash_flow_history = _extract_annual_fact_history(
        us_gaap_facts,
        OPERATING_CASH_FLOW_TAGS,
        "USD",
    )

    capex_history = _extract_annual_fact_history(
        us_gaap_facts,
        CAPEX_TAGS,
        "USD",
    )

    revenue_by_period = {
        item["period_end"]: item
        for item in revenue_history
    }

    capex_by_period = {
        item["period_end"]: item
        for item in capex_history
    }

    margins = []

    for ocf_item in operating_cash_flow_history:
        period_end = ocf_item["period_end"]

        revenue_item = revenue_by_period.get(period_end)
        capex_item = capex_by_period.get(period_end)

        if revenue_item is None or capex_item is None:
            continue

        revenue = revenue_item["value"]

        if revenue == 0:
            continue

        free_cash_flow = (
            ocf_item["value"]
            - capex_item["value"]
        )

        margins.append(
            {
                "fiscal_year": ocf_item["fiscal_year"],
                "period_end": period_end,
                "free_cash_flow": free_cash_flow,
                "revenue": revenue,
                "fcf_margin": free_cash_flow / revenue,
            }
        )

    return margins

def get_free_cash_flow_growth_metrics(cik: str) -> dict:
    fcf_history = get_free_cash_flow_history(cik)

    metrics = {
        "latest_free_cash_flow": None,
        "latest_period_end": None,
        "fcf_cagr_3y": None,
        "fcf_cagr_5y": None,
    }

    if not fcf_history:
        return metrics

    latest = fcf_history[-1]

    metrics["latest_free_cash_flow"] = latest["free_cash_flow"]
    metrics["latest_period_end"] = latest["period_end"]

    if len(fcf_history) >= 4:
        start = fcf_history[-4]

        metrics["fcf_cagr_3y"] = calculate_cagr(
            start["free_cash_flow"],
            latest["free_cash_flow"],
            3,
        )

    if len(fcf_history) >= 6:
        start = fcf_history[-6]

        metrics["fcf_cagr_5y"] = calculate_cagr(
            start["free_cash_flow"],
            latest["free_cash_flow"],
            5,
        )

    return metrics


def get_total_debt_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    current_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_DEBT_TAGS,
        "USD",
    )

    long_term_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        LONG_TERM_DEBT_TAGS,
        "USD",
    )

    current_debt_by_period = {
        item["period_end"]: item
        for item in current_debt_history
    }

    total_debt_history = []

    for long_term_item in long_term_debt_history:
        period_end = long_term_item["period_end"]

        current_item = current_debt_by_period.get(period_end)

        current_debt = (
            current_item["value"]
            if current_item is not None
            else 0
        )

        long_term_debt = long_term_item["value"]

        total_debt_history.append(
            {
                "fiscal_year": long_term_item["fiscal_year"],
                "period_end": period_end,
                "current_debt": current_debt,
                "long_term_debt": long_term_debt,
                "total_debt": current_debt + long_term_debt,
            }
        )

    return total_debt_history

def get_net_debt_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    cash_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CASH_TAGS,
        "USD",
    )

    current_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_DEBT_TAGS,
        "USD",
    )

    long_term_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        LONG_TERM_DEBT_TAGS,
        "USD",
    )

    cash_by_period = {
        item["period_end"]: item
        for item in cash_history
    }

    current_debt_by_period = {
        item["period_end"]: item
        for item in current_debt_history
    }

    net_debt_history = []

    for long_term_item in long_term_debt_history:
        period_end = long_term_item["period_end"]

        cash_item = cash_by_period.get(period_end)
        current_item = current_debt_by_period.get(period_end)

        if cash_item is None:
            continue

        current_debt = (
            current_item["value"]
            if current_item is not None
            else 0
        )

        long_term_debt = long_term_item["value"]
        total_debt = current_debt + long_term_debt
        cash = cash_item["value"]

        net_debt_history.append(
            {
                "fiscal_year": long_term_item["fiscal_year"],
                "period_end": period_end,
                "cash": cash,
                "total_debt": total_debt,
                "net_debt": total_debt - cash,
            }
        )

    return net_debt_history

def get_debt_to_equity_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    current_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_DEBT_TAGS,
        "USD",
    )

    long_term_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        LONG_TERM_DEBT_TAGS,
        "USD",
    )

    equity_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        SHAREHOLDERS_EQUITY_TAGS,
        "USD",
    )

    current_debt_by_period = {
        item["period_end"]: item
        for item in current_debt_history
    }

    equity_by_period = {
        item["period_end"]: item
        for item in equity_history
    }

    ratios = []

    for long_term_item in long_term_debt_history:
        period_end = long_term_item["period_end"]

        current_item = current_debt_by_period.get(period_end)
        equity_item = equity_by_period.get(period_end)

        if equity_item is None:
            continue

        equity = equity_item["value"]

        if equity <= 0:
            continue

        current_debt = (
            current_item["value"]
            if current_item is not None
            else 0
        )

        long_term_debt = long_term_item["value"]
        total_debt = current_debt + long_term_debt

        ratios.append(
            {
                "fiscal_year": long_term_item["fiscal_year"],
                "period_end": period_end,
                "total_debt": total_debt,
                "shareholders_equity": equity,
                "debt_to_equity": total_debt / equity,
            }
        )

    return ratios

def get_current_ratio_history(cik: str) -> list[dict]:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    current_assets_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_ASSETS_TAGS,
        "USD",
    )

    current_liabilities_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_LIABILITIES_TAGS,
        "USD",
    )

    liabilities_by_period = {
        item["period_end"]: item
        for item in current_liabilities_history
    }

    ratios = []

    for assets_item in current_assets_history:
        period_end = assets_item["period_end"]

        liabilities_item = liabilities_by_period.get(period_end)

        if liabilities_item is None:
            continue

        current_assets = assets_item["value"]
        current_liabilities = liabilities_item["value"]

        if current_liabilities <= 0:
            continue

        ratios.append(
            {
                "fiscal_year": assets_item["fiscal_year"],
                "period_end": period_end,
                "current_assets": current_assets,
                "current_liabilities": current_liabilities,
                "current_ratio": current_assets / current_liabilities,
            }
        )

    return ratios

def get_fundamental_summary(cik: str) -> dict:
    company_facts = get_company_facts(cik)
    us_gaap_facts = _get_us_gaap_facts(company_facts)

    revenue_history = _extract_annual_fact_history(
        us_gaap_facts,
        REVENUE_TAGS,
        "USD",
    )

    net_income_history = _extract_annual_fact_history(
        us_gaap_facts,
        NET_INCOME_TAGS,
        "USD",
    )

    eps_history = _extract_annual_fact_history(
        us_gaap_facts,
        DILUTED_EPS_TAGS,
        "USD/shares",
    )

    ocf_history = _extract_annual_fact_history(
        us_gaap_facts,
        OPERATING_CASH_FLOW_TAGS,
        "USD",
    )

    capex_history = _extract_annual_fact_history(
        us_gaap_facts,
        CAPEX_TAGS,
        "USD",
    )

    cash_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CASH_TAGS,
        "USD",
    )

    current_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_DEBT_TAGS,
        "USD",
    )

    long_term_debt_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        LONG_TERM_DEBT_TAGS,
        "USD",
    )

    equity_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        SHAREHOLDERS_EQUITY_TAGS,
        "USD",
    )

    current_assets_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_ASSETS_TAGS,
        "USD",
    )

    current_liabilities_history = _extract_annual_instant_fact_history(
        us_gaap_facts,
        CURRENT_LIABILITIES_TAGS,
        "USD",
    )

    return {
        "revenue_history": revenue_history,
        "net_income_history": net_income_history,
        "eps_history": eps_history,
        "operating_cash_flow_history": ocf_history,
        "capex_history": capex_history,
        "cash_history": cash_history,
        "current_debt_history": current_debt_history,
        "long_term_debt_history": long_term_debt_history,
        "equity_history": equity_history,
        "current_assets_history": current_assets_history,
        "current_liabilities_history": current_liabilities_history,
    }

def build_fundamental_metrics(summary: dict) -> dict:
    revenue_history = summary["revenue_history"]
    net_income_history = summary["net_income_history"]
    eps_history = summary["eps_history"]
    ocf_history = summary["operating_cash_flow_history"]
    capex_history = summary["capex_history"]

    cash_history = summary["cash_history"]
    current_debt_history = summary["current_debt_history"]
    long_term_debt_history = summary["long_term_debt_history"]
    equity_history = summary["equity_history"]

    current_assets_history = summary["current_assets_history"]
    current_liabilities_history = summary["current_liabilities_history"]

    metrics = {
        "latest_period_end": None,
        "revenue": None,
        "net_income": None,
        "net_margin": None,
        "diluted_eps": None,
        "operating_cash_flow": None,
        "capex": None,
        "free_cash_flow": None,
        "fcf_margin": None,
        "revenue_cagr_3y": None,
        "revenue_cagr_5y": None,
        "eps_cagr_3y": None,
        "eps_cagr_5y": None,
        "fcf_cagr_3y": None,
        "fcf_cagr_5y": None,
        "fcf_growth_1y": None,
        "fcf_consecutive_declines": 0,
        "cash": None,
        "total_debt": None,
        "net_debt": None,
        "shareholders_equity": None,
        "debt_to_equity": None,
        "current_assets": None,
        "current_liabilities": None,
        "current_ratio": None,
    }

    if not revenue_history:
        return metrics

    latest_period_end = revenue_history[-1]["period_end"]
    metrics["latest_period_end"] = latest_period_end

    def get_value_for_period(history: list[dict]) -> float | None:
        for item in history:
            if item["period_end"] == latest_period_end:
                return item["value"]
        return None

    revenue = get_value_for_period(revenue_history)
    net_income = get_value_for_period(net_income_history)
    eps = get_value_for_period(eps_history)
    ocf = get_value_for_period(ocf_history)
    capex = get_value_for_period(capex_history)

    cash = get_value_for_period(cash_history)
    current_debt = get_value_for_period(current_debt_history)
    long_term_debt = get_value_for_period(long_term_debt_history)
    equity = get_value_for_period(equity_history)

    current_assets = get_value_for_period(current_assets_history)
    current_liabilities = get_value_for_period(current_liabilities_history)

    metrics["revenue"] = revenue
    metrics["net_income"] = net_income
    metrics["diluted_eps"] = eps
    metrics["operating_cash_flow"] = ocf
    metrics["capex"] = capex

    metrics["cash"] = cash
    metrics["shareholders_equity"] = equity
    metrics["current_assets"] = current_assets
    metrics["current_liabilities"] = current_liabilities

    if revenue and net_income is not None:
        metrics["net_margin"] = net_income / revenue

    if ocf is not None and capex is not None:
        free_cash_flow = ocf - capex
        metrics["free_cash_flow"] = free_cash_flow

        if revenue:
            metrics["fcf_margin"] = free_cash_flow / revenue

    if current_debt is not None or long_term_debt is not None:
        total_debt = (current_debt or 0) + (long_term_debt or 0)

        metrics["total_debt"] = total_debt

        if cash is not None:
            metrics["net_debt"] = total_debt - cash

        if equity and equity > 0:
            metrics["debt_to_equity"] = total_debt / equity

    if current_assets is not None and current_liabilities:
        metrics["current_ratio"] = (
            current_assets / current_liabilities
        )

    if len(revenue_history) >= 4:
        metrics["revenue_cagr_3y"] = calculate_cagr(
            revenue_history[-4]["value"],
            revenue_history[-1]["value"],
            3,
        )

    if len(revenue_history) >= 6:
        metrics["revenue_cagr_5y"] = calculate_cagr(
            revenue_history[-6]["value"],
            revenue_history[-1]["value"],
            5,
        )

    if len(eps_history) >= 4:
        metrics["eps_cagr_3y"] = calculate_cagr(
            eps_history[-4]["value"],
            eps_history[-1]["value"],
            3,
        )

    if len(eps_history) >= 6:
        metrics["eps_cagr_5y"] = calculate_cagr(
            eps_history[-6]["value"],
            eps_history[-1]["value"],
            5,
        )

    fcf_history = []

    capex_by_period = {
        item["period_end"]: item
        for item in capex_history
    }

    for ocf_item in ocf_history:
        capex_item = capex_by_period.get(
            ocf_item["period_end"]
        )

        if capex_item is None:
            continue

        fcf_history.append(
            {
                "period_end": ocf_item["period_end"],
                "value": (
                    ocf_item["value"]
                    - capex_item["value"]
                ),
            }
        )

    if len(fcf_history) >= 2:
        previous_fcf = fcf_history[-2]["value"]
        latest_fcf = fcf_history[-1]["value"]

        if previous_fcf != 0:
            metrics["fcf_growth_1y"] = (
                latest_fcf - previous_fcf
            ) / abs(previous_fcf)

    decline_count = 0

    for index in range(
        len(fcf_history) - 1,
        0,
        -1,
    ):
        current_fcf = fcf_history[index]["value"]
        previous_fcf = fcf_history[index - 1]["value"]

        if current_fcf < previous_fcf:
            decline_count += 1
        else:
            break

    metrics["fcf_consecutive_declines"] = decline_count

    if len(fcf_history) >= 4:
        metrics["fcf_cagr_3y"] = calculate_cagr(
            fcf_history[-4]["value"],
            fcf_history[-1]["value"],
            3,
        )

    if len(fcf_history) >= 6:
        metrics["fcf_cagr_5y"] = calculate_cagr(
            fcf_history[-6]["value"],
            fcf_history[-1]["value"],
            5,
        )

    return metrics

def get_fundamental_metrics(cik: str) -> dict:
    summary = get_fundamental_summary(cik)
    return build_fundamental_metrics(summary)