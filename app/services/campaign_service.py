"""Business logic for campaign CRUD operations.

Keeps the controller layer thin by encapsulating queries, transactions,
and domain rules here.
"""

import logging

from sqlalchemy import or_

from app.extensions import db
from app.models.campaign import Campaign
from app.schemas.campaign import CAMPAIGN_STATUSES, PLATFORMS

logger = logging.getLogger(__name__)


class CampaignService:
    """Stateless service class for Campaign operations."""

    # ------------------------------------------------------------------
    # List / Search
    # ------------------------------------------------------------------
    @staticmethod
    def list_campaigns(
        search=None, status=None, platform=None, limit=50, offset=0
    ):
        """Return a paginated, optionally filtered list of campaigns.

        Returns:
            tuple: (list[Campaign], int)  -- campaigns and total count.
        """
        query = Campaign.query

        # Exact filters
        if status:
            query = query.filter(Campaign.status == status)
        if platform:
            query = query.filter(Campaign.platform == platform)

        # Free-text search: case-insensitive substring on name,
        # or exact enum match for status / platform values that contain
        # the search substring.
        if search:
            search_lower = search.lower()
            filters = [Campaign.name.ilike(f"%{search}%")]

            matching_statuses = [
                s for s in CAMPAIGN_STATUSES if search_lower in s
            ]
            if matching_statuses:
                filters.append(Campaign.status.in_(matching_statuses))

            matching_platforms = [
                p for p in PLATFORMS if search_lower in p
            ]
            if matching_platforms:
                filters.append(Campaign.platform.in_(matching_platforms))

            query = query.filter(or_(*filters))

        total = query.count()
        campaigns = (
            query.order_by(Campaign.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return campaigns, total

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    @staticmethod
    def get_campaign(campaign_id):
        """Fetch a single campaign by primary key.

        Returns:
            Campaign | None
        """
        return db.session.get(Campaign, campaign_id)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    @staticmethod
    def create_campaign(data):
        """Persist a new campaign.

        Args:
            data: dict validated by CampaignCreateSchema.

        Returns:
            Campaign
        """
        campaign = Campaign(**data)
        db.session.add(campaign)
        db.session.commit()
        logger.info("Campaign created: %s", campaign.id)
        return campaign

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    @staticmethod
    def update_campaign(campaign_id, data):
        """Apply a partial update to an existing campaign.

        Args:
            campaign_id: UUID of the campaign.
            data: dict validated by CampaignUpdateSchema.

        Returns:
            Campaign | None  -- None when the campaign does not exist.
        """
        campaign = db.session.get(Campaign, campaign_id)
        if campaign is None:
            return None

        for key, value in data.items():
            setattr(campaign, key, value)

        db.session.commit()
        logger.info("Campaign updated: %s", campaign.id)
        return campaign

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    @staticmethod
    def delete_campaign(campaign_id):
        """Delete a campaign by primary key.

        Returns:
            bool -- True if deleted, False if not found.
        """
        campaign = db.session.get(Campaign, campaign_id)
        if campaign is None:
            return False

        db.session.delete(campaign)
        db.session.commit()
        logger.info("Campaign deleted: %s", campaign_id)
        return True
