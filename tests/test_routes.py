"""Tests for API route endpoints."""

from fastapi.testclient import TestClient
from app.main import app
from core.config import get_settings

client = TestClient(app)
settings = get_settings()

VALID_HEADERS = {"X-API-Key": settings.api_key_secret}


class TestHealthEndpoint:

    def test_health_returns_200(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self):
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestAuthentication:

    def test_missing_api_key_returns_401(self):
        response = client.post(
            "/api/v1/papers/question",
            json={"paper_id": "test", "question": "What is this about in detail?"},
        )
        assert response.status_code == 401

    def test_wrong_api_key_returns_403(self):
        response = client.post(
            "/api/v1/papers/question",
            json={"paper_id": "test", "question": "What is this about in detail?"},
            headers={"X-API-Key": "completely-wrong-key"},
        )
        assert response.status_code == 403


class TestRootEndpoint:

    def test_root_returns_200_or_redirect(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [200, 307, 302]