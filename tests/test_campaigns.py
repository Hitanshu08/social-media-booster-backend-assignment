"""Tests for the Campaign API endpoints."""

import json

import pytest

from tests.conftest import make_campaign_payload


# ------------------------------------------------------------------ helpers
def _post_campaign(client, **overrides):
    """Create a campaign via POST and return the JSON response."""
    payload = make_campaign_payload(**overrides)
    resp = client.post(
        "/api/campaigns",
        data=json.dumps(payload),
        content_type="application/json",
    )
    return resp


# ------------------------------------------------------------------ CREATE
class TestCreateCampaign:
    def test_create_success(self, client):
        resp = _post_campaign(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Test Campaign"
        assert data["status"] == "draft"
        assert "id" in data
        assert "createdAt" in data

    def test_create_missing_required_field(self, client):
        payload = make_campaign_payload()
        del payload["name"]
        resp = client.post(
            "/api/campaigns",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["code"] == "validation_error"

    def test_create_invalid_status(self, client):
        resp = _post_campaign(client, status="invalid")
        assert resp.status_code == 400

    def test_create_invalid_platform(self, client):
        resp = _post_campaign(client, platform="tiktok")
        assert resp.status_code == 400

    def test_create_budget_zero(self, client):
        resp = _post_campaign(client, budget=0)
        assert resp.status_code == 400

    def test_create_invalid_date_range(self, client):
        resp = _post_campaign(
            client, startDate="2025-12-31", endDate="2025-01-01"
        )
        assert resp.status_code == 400

    def test_create_unknown_field_rejected(self, client):
        resp = _post_campaign(client, extraField="nope")
        assert resp.status_code == 400

    def test_create_no_json_body(self, client):
        resp = client.post("/api/campaigns", data="not json")
        assert resp.status_code == 400


# ------------------------------------------------------------------ LIST
class TestListCampaigns:
    def test_list_empty(self, client):
        resp = client.get("/api/campaigns")
        assert resp.status_code == 200
        assert resp.get_json() == []
        assert resp.headers.get("X-Total-Count") == "0"

    def test_list_returns_created(self, client):
        _post_campaign(client, name="Alpha")
        _post_campaign(client, name="Beta")

        resp = client.get("/api/campaigns")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        assert resp.headers.get("X-Total-Count") == "2"

    def test_list_filter_by_status(self, client):
        _post_campaign(client, name="Active", status="active")
        _post_campaign(client, name="Draft", status="draft")

        resp = client.get("/api/campaigns?status=active")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Active"

    def test_list_filter_by_platform(self, client):
        _post_campaign(client, name="FB", platform="facebook")
        _post_campaign(client, name="GG", platform="google")

        resp = client.get("/api/campaigns?platform=google")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "GG"

    def test_list_search(self, client):
        _post_campaign(client, name="Summer Sale")
        _post_campaign(client, name="Winter Promo")

        resp = client.get("/api/campaigns?search=summer")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Summer Sale"

    def test_list_pagination(self, client):
        for i in range(5):
            _post_campaign(client, name=f"Camp {i}")

        resp = client.get("/api/campaigns?limit=2&offset=0")
        assert len(resp.get_json()) == 2
        assert resp.headers.get("X-Total-Count") == "5"

    def test_list_invalid_query_params(self, client):
        resp = client.get("/api/campaigns?limit=999")
        assert resp.status_code == 400


# ------------------------------------------------------------------ GET
class TestGetCampaign:
    def test_get_success(self, client):
        create_resp = _post_campaign(client)
        cid = create_resp.get_json()["id"]

        resp = client.get(f"/api/campaigns/{cid}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == cid

    def test_get_not_found(self, client):
        resp = client.get(
            "/api/campaigns/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404
        assert resp.get_json()["code"] == "not_found"


# ------------------------------------------------------------------ UPDATE
class TestUpdateCampaign:
    def test_update_success(self, client):
        create_resp = _post_campaign(client)
        cid = create_resp.get_json()["id"]

        resp = client.patch(
            f"/api/campaigns/{cid}",
            data=json.dumps({"name": "Updated", "budget": 5000}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Updated"
        assert data["budget"] == 5000.0

    def test_update_empty_body(self, client):
        create_resp = _post_campaign(client)
        cid = create_resp.get_json()["id"]

        resp = client.patch(
            f"/api/campaigns/{cid}",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_update_not_found(self, client):
        resp = client.patch(
            "/api/campaigns/00000000-0000-0000-0000-000000000000",
            data=json.dumps({"name": "X"}),
            content_type="application/json",
        )
        assert resp.status_code == 404


# ------------------------------------------------------------------ DELETE
class TestDeleteCampaign:
    def test_delete_success(self, client):
        create_resp = _post_campaign(client)
        cid = create_resp.get_json()["id"]

        resp = client.delete(f"/api/campaigns/{cid}")
        assert resp.status_code == 204

        # Verify gone
        assert (
            client.get(f"/api/campaigns/{cid}").status_code == 404
        )

    def test_delete_not_found(self, client):
        resp = client.delete(
            "/api/campaigns/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404


# ------------------------------------------------------------------ INSIGHTS
class TestCampaignInsights:
    def test_insights_returns_zeros_when_empty(self, client):
        create_resp = _post_campaign(client)
        cid = create_resp.get_json()["id"]

        resp = client.get(f"/api/campaigns/{cid}/insights")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["impressions"] == 0
        assert data["engagement"]["likes"] == 0

    def test_insights_campaign_not_found(self, client):
        resp = client.get(
            "/api/campaigns/00000000-0000-0000-0000-000000000000/insights"
        )
        assert resp.status_code == 404
