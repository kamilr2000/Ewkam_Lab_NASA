from fastapi import FastAPI

app = FastAPI(
    title="Terra Analog API",
    version="0.1.0",
    description="API bootstrap; analysis data and search are not available yet.",
)


@app.get("/api/v1/health", tags=["system"])
def get_health() -> dict[str, str | bool | None]:
    """Report API readiness without implying that scientific data are loaded."""
    return {
        "status": "ready",
        "dataset_ready": False,
        "dataset_version": None,
    }
