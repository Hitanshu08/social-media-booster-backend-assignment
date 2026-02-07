"""Marshmallow schemas for Campaign-related request / response payloads.

Handles:
* camelCase <-> snake_case mapping via ``data_key``
* Input validation matching the OpenAPI spec constraints
* Serialisation of ORM model instances to JSON-friendly dicts
"""

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates_schema

# ---------------------------------------------------------------------------
# Allowed enum values (must stay in sync with db-schema.sql enums)
# ---------------------------------------------------------------------------
CAMPAIGN_STATUSES = ("active", "paused", "completed", "draft")
PLATFORMS = ("facebook", "google", "instagram", "linkedin", "twitter")


# ---------------------------------------------------------------------------
# Read / Response schemas
# ---------------------------------------------------------------------------
class CampaignSchema(Schema):
    """Full campaign representation (used for API responses)."""

    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)
    status = fields.String(required=True)
    platform = fields.String(required=True)
    budget = fields.Float(required=True)
    start_date = fields.Date(data_key="startDate")
    end_date = fields.Date(data_key="endDate")
    description = fields.String(required=True)
    target_audience = fields.String(data_key="targetAudience")
    created_at = fields.DateTime(dump_only=True, data_key="createdAt")
    updated_at = fields.DateTime(dump_only=True, data_key="updatedAt")


# ---------------------------------------------------------------------------
# Write / Request schemas
# ---------------------------------------------------------------------------
class CampaignCreateSchema(Schema):
    """Validate POST /campaigns request body."""

    name = fields.String(required=True, validate=validate.Length(min=1))
    status = fields.String(
        required=True, validate=validate.OneOf(CAMPAIGN_STATUSES)
    )
    platform = fields.String(
        required=True, validate=validate.OneOf(PLATFORMS)
    )
    budget = fields.Float(
        required=True,
        validate=validate.Range(min=0, min_inclusive=False),
    )
    start_date = fields.Date(required=True, data_key="startDate")
    end_date = fields.Date(required=True, data_key="endDate")
    description = fields.String(
        required=True, validate=validate.Length(min=1)
    )
    target_audience = fields.String(
        required=True, data_key="targetAudience", validate=validate.Length(min=1)
    )

    class Meta:
        unknown = RAISE  # reject unknown fields (additionalProperties: false)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if "start_date" in data and "end_date" in data:
            if data["start_date"] > data["end_date"]:
                raise ValidationError(
                    "End date must be on or after start date.",
                    field_name="endDate",
                )


class CampaignUpdateSchema(Schema):
    """Validate PATCH /campaigns/{id} request body.

    All fields are optional but at least one must be provided
    (minProperties: 1 in the OpenAPI spec).
    """

    name = fields.String(validate=validate.Length(min=1))
    status = fields.String(validate=validate.OneOf(CAMPAIGN_STATUSES))
    platform = fields.String(validate=validate.OneOf(PLATFORMS))
    budget = fields.Float(
        validate=validate.Range(min=0, min_inclusive=False)
    )
    start_date = fields.Date(data_key="startDate")
    end_date = fields.Date(data_key="endDate")
    description = fields.String(validate=validate.Length(min=1))
    target_audience = fields.String(
        data_key="targetAudience", validate=validate.Length(min=1)
    )

    class Meta:
        unknown = RAISE

    @validates_schema
    def validate_not_empty(self, data, **kwargs):
        if not data:
            raise ValidationError("At least one field must be provided.")

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if "start_date" in data and "end_date" in data:
            if data["start_date"] > data["end_date"]:
                raise ValidationError(
                    "End date must be on or after start date.",
                    field_name="endDate",
                )


# ---------------------------------------------------------------------------
# Query-parameter schema for listing
# ---------------------------------------------------------------------------
class CampaignListQuerySchema(Schema):
    """Validate GET /campaigns query parameters."""

    search = fields.String(load_default=None)
    status = fields.String(
        load_default=None, validate=validate.OneOf(CAMPAIGN_STATUSES)
    )
    platform = fields.String(
        load_default=None, validate=validate.OneOf(PLATFORMS)
    )
    limit = fields.Integer(
        load_default=50, validate=validate.Range(min=1, max=100)
    )
    offset = fields.Integer(
        load_default=0, validate=validate.Range(min=0)
    )


# ---------------------------------------------------------------------------
# Insights response schema
# ---------------------------------------------------------------------------
class EngagementSchema(Schema):
    """Nested engagement metrics."""

    likes = fields.Integer()
    shares = fields.Integer()
    comments = fields.Integer()


class CampaignInsightSchema(Schema):
    """Campaign performance insights (GET /campaigns/{id}/insights)."""

    impressions = fields.Integer()
    clicks = fields.Integer()
    conversions = fields.Integer()
    ctr = fields.Float()
    cpc = fields.Float()
    roi = fields.Float()
    engagement = fields.Nested(EngagementSchema)
