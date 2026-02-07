"""Campaign ORM model.

Maps to the ``campaigns`` table defined in db-schema.sql.
Uses String columns for status/platform for portability – enum validation
is enforced at the API layer via marshmallow schemas.
The DB-level trigger handles ``updated_at`` automatically on UPDATE.
"""

import uuid

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class Campaign(db.Model):
    """Represents a social-media advertising campaign."""

    __tablename__ = "campaigns"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    budget = db.Column(db.Numeric(12, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    # Relationship ----------------------------------------------------------
    insights = db.relationship(
        "CampaignInsight",
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Campaign {self.id!s} – {self.name}>"
