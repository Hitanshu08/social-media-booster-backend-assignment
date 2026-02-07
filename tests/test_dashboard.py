"""Tests for the Dashboard API endpoints."""

import json

from tests.conftest import make_campaign_payload


class TestDashboardMetrics:
    def test_metrics_empty_db(self, client):
        resp = client.get("/api/dashboard/metrics")
        assert resp.status_code == 200
        data = resp.get_json()

        assert data["campaignsByStatus"] == {
            "active": 0,
            "paused": 0,
            "completed": 0,
            "draft": 0,
        }
        assert data["totalActiveBudget"] == 0.0
        for p in ("facebook", "google", "instagram", "linkedin", "twitter"):
            assert data["budgetByPlatform"][p] == 0.0

    def test_metrics_with_campaigns(self, client):
        # Seed two active campaigns
        for name, budget, platform in [
            ("A", 1000, "facebook"),
            ("B", 2000, "google"),
        ]:
            payload = make_campaign_payload(
                name=name,
                status="active",
                platform=platform,
                budget=budget,
            )
            client.post(
                "/api/campaigns",
                data=json.dumps(payload),
                content_type="application/json",
            )

        # Add a paused campaign
        payload = make_campaign_payload(
            name="C", status="paused", platform="facebook", budget=500
        )
        client.post(
            "/api/campaigns",
            data=json.dumps(payload),
            content_type="application/json",
        )

        resp = client.get("/api/dashboard/metrics")
        data = resp.get_json()

        assert data["campaignsByStatus"]["active"] == 2
        assert data["campaignsByStatus"]["paused"] == 1
        assert data["totalActiveBudget"] == 3000.0
        assert data["budgetByPlatform"]["facebook"] == 1500.0
        assert data["budgetByPlatform"]["google"] == 2000.0


class TestHealthCheck:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"
