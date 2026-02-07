"""CampaignInsight ORM model.

Maps to the ``campaign_insights`` table defined in db-schema.sql.
Stores point-in-time performance snapshots for a campaign.
"""

import uuid

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class CampaignInsight(db.Model):
    """Time-series performance snapshot for a campaign."""

    __tablename__ = "campaign_insights"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    captured_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
    impressions = db.Column(db.BigInteger, nullable=False)
    clicks = db.Column(db.BigInteger, nullable=False)
    conversions = db.Column(db.BigInteger, nullable=False)
    ctr = db.Column(db.Numeric(5, 2), nullable=False)
    cpc = db.Column(db.Numeric(10, 2), nullable=False)
    roi = db.Column(db.Numeric(8, 2), nullable=False)
    engagement_likes = db.Column(db.BigInteger, nullable=False)
    engagement_shares = db.Column(db.BigInteger, nullable=False)
    engagement_comments = db.Column(db.BigInteger, nullable=False)

    # Relationship ----------------------------------------------------------
    campaign = db.relationship("Campaign", back_populates="insights")

    def __repr__(self):
        return (
            f"<CampaignInsight {self.id!s} "
            f"campaign={self.campaign_id!s} @ {self.captured_at}>"
        )
