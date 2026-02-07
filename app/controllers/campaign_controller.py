"""Campaign API endpoints (Blueprint).

Routes:
    GET    /api/campaigns                  List campaigns
    POST   /api/campaigns                  Create campaign
    GET    /api/campaigns/<id>             Get campaign
    PATCH  /api/campaigns/<id>             Update campaign
    DELETE /api/campaigns/<id>             Delete campaign
    GET    /api/campaigns/<id>/insights    Get campaign insights
"""

import logging

from flask import Blueprint, abort, jsonify, request

from app.schemas import (
    CampaignCreateSchema,
    CampaignInsightSchema,
    CampaignListQuerySchema,
    CampaignSchema,
    CampaignUpdateSchema,
)
from app.services.campaign_service import CampaignService
from app.services.insight_service import InsightService

logger = logging.getLogger(__name__)

campaign_bp = Blueprint("campaigns", __name__)

# Instantiate schemas once (they are stateless & thread-safe)
_campaign_schema = CampaignSchema()
_campaigns_schema = CampaignSchema(many=True)
_create_schema = CampaignCreateSchema()
_update_schema = CampaignUpdateSchema()
_query_schema = CampaignListQuerySchema()
_insight_schema = CampaignInsightSchema()


# ------------------------------------------------------------------
# GET /api/campaigns
# ------------------------------------------------------------------
@campaign_bp.route("", methods=["GET"])
def list_campaigns():
    """Return a paginated list of campaigns with optional filters."""
    params = _query_schema.load(request.args)
    campaigns, total = CampaignService.list_campaigns(**params)

    response = jsonify(_campaigns_schema.dump(campaigns))
    response.headers["X-Total-Count"] = str(total)
    return response


# ------------------------------------------------------------------
# POST /api/campaigns
# ------------------------------------------------------------------
@campaign_bp.route("", methods=["POST"])
def create_campaign():
    """Create a new campaign."""
    body = request.get_json(silent=True)
    if body is None:
        abort(400, description="Request body must be valid JSON")

    data = _create_schema.load(body)
    campaign = CampaignService.create_campaign(data)
    return jsonify(_campaign_schema.dump(campaign)), 201


# ------------------------------------------------------------------
# GET /api/campaigns/<id>
# ------------------------------------------------------------------
@campaign_bp.route("/<uuid:campaign_id>", methods=["GET"])
def get_campaign(campaign_id):
    """Fetch a single campaign by ID."""
    campaign = CampaignService.get_campaign(campaign_id)
    if campaign is None:
        abort(404, description="Campaign not found")
    return jsonify(_campaign_schema.dump(campaign))


# ------------------------------------------------------------------
# PATCH /api/campaigns/<id>
# ------------------------------------------------------------------
@campaign_bp.route("/<uuid:campaign_id>", methods=["PATCH"])
def update_campaign(campaign_id):
    """Partially update an existing campaign."""
    body = request.get_json(silent=True)
    if body is None:
        abort(400, description="Request body must be valid JSON")

    data = _update_schema.load(body)
    campaign = CampaignService.update_campaign(campaign_id, data)
    if campaign is None:
        abort(404, description="Campaign not found")
    return jsonify(_campaign_schema.dump(campaign))


# ------------------------------------------------------------------
# DELETE /api/campaigns/<id>
# ------------------------------------------------------------------
@campaign_bp.route("/<uuid:campaign_id>", methods=["DELETE"])
def delete_campaign(campaign_id):
    """Delete a campaign."""
    deleted = CampaignService.delete_campaign(campaign_id)
    if not deleted:
        abort(404, description="Campaign not found")
    return "", 204


# ------------------------------------------------------------------
# GET /api/campaigns/<id>/insights
# ------------------------------------------------------------------
@campaign_bp.route("/<uuid:campaign_id>/insights", methods=["GET"])
def get_campaign_insights(campaign_id):
    """Return performance insights for a campaign."""
    campaign = CampaignService.get_campaign(campaign_id)
    if campaign is None:
        abort(404, description="Campaign not found")

    insights = InsightService.get_campaign_insights(campaign_id)
    return jsonify(_insight_schema.dump(insights))
