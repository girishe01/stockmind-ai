from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from backend.app.services.sec_service import get_company_by_ticker

from backend.app.database import engine


app = FastAPI(
    title="StockMind API",
    description="AI-powered stock research and analysis platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "StockMind API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/companies/{ticker}")
def get_company(ticker: str):
    normalized_ticker = ticker.upper().strip()

    select_query = text("""
        select
            id,
            ticker,
            company_name,
            exchange,
            sector,
            industry,
            cik,
            country,
            currency,
            is_active
        from public.companies
        where ticker = :ticker
    """)

    with engine.connect() as connection:
        existing_company = connection.execute(
            select_query,
            {"ticker": normalized_ticker},
        ).mappings().first()

    if existing_company:
        company = dict(existing_company)

    if company["cik"] is None:
        sec_company = get_company_by_ticker(normalized_ticker)

        if sec_company is not None:
            update_query = text("""
                update public.companies
                set
                    company_name = coalesce(company_name, :company_name),
                    cik = coalesce(cik, :cik),
                    updated_at = now()
                where ticker = :ticker
                returning
                    id,
                    ticker,
                    company_name,
                    exchange,
                    sector,
                    industry,
                    cik,
                    country,
                    currency,
                    is_active
            """)

            with engine.begin() as connection:
                updated_company = connection.execute(
                    update_query,
                    {
                        "ticker": normalized_ticker,
                        "company_name": sec_company["company_name"],
                        "cik": sec_company["cik"],
                    },
                ).mappings().one()

            return dict(updated_company)

    return company


    sec_company = get_company_by_ticker(normalized_ticker)

    if sec_company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company {normalized_ticker} not found",
        )

    insert_query = text("""
        insert into public.companies (
            ticker,
            company_name,
            cik
        )
        values (
            :ticker,
            :company_name,
            :cik
        )
        returning
            id,
            ticker,
            company_name,
            exchange,
            sector,
            industry,
            cik,
            country,
            currency,
            is_active
    """)

    with engine.begin() as connection:
        new_company = connection.execute(
            insert_query,
            sec_company,
        ).mappings().one()

    return dict(new_company)