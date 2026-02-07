"""Business logic for campaign insights retrieval."""

import logging

from app.models.campaign_insight import CampaignInsight

logger = logging.getLogger(__name__)


class InsightService:
    """Service for fetching campaign performance insights."""

    @staticmethod
    def get_campaign_insights(campaign_id):
        """Return the most recent insight snapshot for a campaign.

        If no snapshots exist yet the method returns a zeroed-out dict
        so the API always returns a valid CampaignInsights body.

        Returns:
            dict matching the CampaignInsights schema.
        """
        insight = (
            CampaignInsight.query.filter_by(campaign_id=campaign_id)
            .order_by(CampaignInsight.captured_at.desc())
            .first()
        )

        if insight is None:
            logger.debug(
                "No insights found for campaign %s – returning zeros",
                campaign_id,
            )
            return {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "ctr": 0.0,
                "cpc": 0.0,
                "roi": 0.0,
                "engagement": {"likes": 0, "shares": 0, "comments": 0},
            }

        return {
            "impressions": insight.impressions,
            "clicks": insight.clicks,
            "conversions": insight.conversions,
            "ctr": float(insight.ctr),
            "cpc": float(insight.cpc),
            "roi": float(insight.roi),
            "engagement": {
                "likes": insight.engagement_likes,
                "shares": insight.engagement_shares,
                "comments": insight.engagement_comments,
            },
        }
