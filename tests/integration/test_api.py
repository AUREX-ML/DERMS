"""
Integration tests for the DERMS REST API.

Uses ``httpx.AsyncClient`` with ASGITransport to test the FastAPI app
end-to-end without spinning up a live server.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_schema(self, client: AsyncClient):
        response = await client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data


class TestResourcesEndpoint:
    @pytest.mark.asyncio
    async def test_list_resources_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/resources")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_resources_response_schema(self, client: AsyncClient):
        response = await client.get("/api/v1/resources")
        data = response.json()
        assert "total" in data
        assert "resources" in data
        assert isinstance(data["resources"], list)

    @pytest.mark.asyncio
    async def test_register_resource_returns_201(self, client: AsyncClient):
        payload = {
            "name": "Test Battery A",
            "type": "battery",
            "site_id": "site-integration",
            "capacity_kw": 100.0,
        }
        response = await client.post("/api/v1/resources", json=payload)
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_register_resource_returns_id(self, client: AsyncClient):
        payload = {
            "name": "Test Solar B",
            "type": "solar",
            "site_id": "site-integration",
            "capacity_kw": 250.0,
        }
        response = await client.post("/api/v1/resources", json=payload)
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("res-")

    @pytest.mark.asyncio
    async def test_get_resource_status_404_for_unknown(self, client: AsyncClient):
        response = await client.get("/api/v1/resources/nonexistent-id/status")
        assert response.status_code == 404


class TestForecastEndpoint:
    @pytest.mark.asyncio
    async def test_forecast_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/forecast")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_forecast_contains_points(self, client: AsyncClient):
        response = await client.get("/api/v1/forecast?horizon_h=4&interval=1h")
        data = response.json()
        assert "forecast" in data
        assert len(data["forecast"]) == 4
