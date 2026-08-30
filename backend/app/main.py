from fastapi import FastAPI, HTTPException
from sqlalchemy import text

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
    normalized_ticker = ticker.upper()

    query = text("""
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
        result = connection.execute(
            query,
            {"ticker": normalized_ticker}
        ).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company {normalized_ticker} not found"
        )

    return dict(result)