"""Business logic for the dashboard aggregation endpoint."""

import logging

from sqlalchemy import func

from app.extensions import db
from app.models.campaign import Campaign
from app.schemas.campaign import CAMPAIGN_STATUSES, PLATFORMS

logger = logging.getLogger(__name__)


class DashboardService:
    """Provides aggregated metrics consumed by the dashboard UI."""

    @staticmethod
    def get_metrics():
        """Build the DashboardMetrics payload.

        Returns:
            dict matching the DashboardMetrics schema with keys:
                - campaignsByStatus
                - budgetByPlatform
                - totalActiveBudget
        """

        # --- Campaigns by status -----------------------------------------
        status_rows = (
            db.session.query(Campaign.status, func.count(Campaign.id))
            .group_by(Campaign.status)
            .all()
        )
        campaigns_by_status = {s: 0 for s in CAMPAIGN_STATUSES}
        for status, count in status_rows:
            campaigns_by_status[status] = count

        # --- Budget by platform ------------------------------------------
        budget_rows = (
            db.session.query(Campaign.platform, func.sum(Campaign.budget))
            .group_by(Campaign.platform)
            .all()
        )
        budget_by_platform = {p: 0.0 for p in PLATFORMS}
        for platform, total in budget_rows:
            budget_by_platform[platform] = float(total) if total else 0.0

        # --- Total active budget -----------------------------------------
        total_active = (
            db.session.query(func.sum(Campaign.budget))
            .filter(Campaign.status == "active")
            .scalar()
        )

        return {
            "campaignsByStatus": campaigns_by_status,
            "budgetByPlatform": budget_by_platform,
            "totalActiveBudget": float(total_active) if total_active else 0.0,
        }
