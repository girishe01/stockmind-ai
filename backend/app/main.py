from fastapi import FastAPI

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