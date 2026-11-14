import asyncio

import httpx

from apps.api.main import app


def test_health_reports_api_ready_and_dataset_unavailable() -> None:
    async def request_health() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/v1/health")

    response = asyncio.run(request_health())

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dataset_ready": False,
        "dataset_version": None,
    }
