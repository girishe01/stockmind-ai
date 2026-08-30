import httpx



SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

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