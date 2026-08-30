import httpx



SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

SEC_HEADERS = {
    "User-Agent": "StockMind stockmind@example.com",
    "Accept-Encoding": "gzip, deflate",
}


def get_company_by_ticker(ticker: str) -> dict | None:
    normalized_ticker = ticker.upper().strip()

    response = httpx.get(
        SEC_TICKERS_URL,
        headers=SEC_HEADERS,
        timeout=10.0,
    )

    response.raise_for_status()

    companies = response.json()

    for company in companies.values():
        if company["ticker"].upper() == normalized_ticker:
            return {
                "ticker": company["ticker"].upper(),
                "cik": str(company["cik_str"]).zfill(10),
                "company_name": company["title"],
            }

    return None

def get_company_facts(cik: str) -> dict:
    normalized_cik = str(cik).zfill(10)

    url = SEC_COMPANY_FACTS_URL.format(cik=normalized_cik)

    response = httpx.get(
        url,
        headers=SEC_HEADERS,
        timeout=20.0,
    )

    response.raise_for_status()

    return response.json()