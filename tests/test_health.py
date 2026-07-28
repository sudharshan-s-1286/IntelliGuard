import pytest
from fastapi import status
from httpx import AsyncClient
from starlette.testclient import TestClient


def test_root_health_endpoint_sync(sync_client: TestClient) -> None:
    """
    Tests the GET /health root endpoint using synchronous TestClient.
    """
    response = sync_client.get("/health")
    assert response.status_code == status.HTTP_200_OK

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["app_name"] == "Trust-Agent"
    assert "version" in payload["data"]
    assert "uptime_seconds" in payload["data"]

    # Verify custom tracing middleware headers
    assert "x-request-id" in response.headers
    assert "x-process-time-ms" in response.headers


@pytest.mark.asyncio
async def test_api_v1_health_endpoint_async(async_client: AsyncClient) -> None:
    """
    Tests the GET /api/v1/health endpoint using asynchronous AsyncClient.
    """
    response = await async_client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["app_name"] == "Trust-Agent"
    assert payload["error"] is None
    assert isinstance(payload["meta"], dict)


@pytest.mark.asyncio
async def test_not_found_exception_handler(async_client: AsyncClient) -> None:
    """
    Tests global exception handler response structure for non-existent route.
    """
    response = await async_client.get("/api/v1/nonexistent-route")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    payload = response.json()
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["error"]["code"] == "NOT_FOUND"
    assert "Not Found" in payload["error"]["message"]
