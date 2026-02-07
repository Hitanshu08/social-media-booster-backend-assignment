"""Seed the database with sample campaigns and insights.

Automatically creates tables via SQLAlchemy if they don't exist.

Usage:
    python seed.py
"""

import random
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models.campaign import Campaign
from app.models.campaign_insight import CampaignInsight

STATUSES = ["active", "paused", "completed", "draft"]
PLATFORMS = ["facebook", "google", "instagram", "linkedin", "twitter"]

SAMPLE_CAMPAIGNS = [
    {
        "name": "Summer Sale 2025",
        "description": "Annual summer sale across all platforms",
        "target_audience": "Adults 25-45, fashion & lifestyle",
    },
    {
        "name": "Product Launch – Widget X",
        "description": "Launch campaign for the new Widget X product line",
        "target_audience": "Tech enthusiasts 18-35",
    },
    {
        "name": "Brand Awareness Q1",
        "description": "Q1 brand awareness push for new markets",
        "target_audience": "General audience 18-65",
    },
    {
        "name": "Holiday Season Promo",
        "description": "Holiday discounts and giveaways",
        "target_audience": "Families, gift shoppers 25-55",
    },
    {
        "name": "Back to School Drive",
        "description": "Targeted campaign for the back-to-school season",
        "target_audience": "Parents with children 5-18",
    },
    {
        "name": "B2B Lead Generation",
        "description": "Generate qualified leads from LinkedIn and Google",
        "target_audience": "Business decision-makers, SMBs",
    },
    {
        "name": "Influencer Partnership Campaign",
        "description": "Collaborative campaign with top influencers",
        "target_audience": "Young adults 18-30, social-media users",
    },
    {
        "name": "Local Awareness – NYC",
        "description": "Geo-targeted awareness for the NYC metro area",
        "target_audience": "NYC residents 21-50",
    },
    {
        "name": "Retargeting – Cart Abandonment",
        "description": "Retarget users who abandoned their shopping carts",
        "target_audience": "Previous website visitors",
    },
    {
        "name": "App Install Campaign",
        "description": "Drive mobile app installs across platforms",
        "target_audience": "Smartphone users 18-40",
    },
]


def seed():
    """Populate the database with sample data."""
    app = create_app("development")

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("✓ Database tables ready.")

        # Clean existing seed data
        CampaignInsight.query.delete()
        Campaign.query.delete()
        db.session.commit()

        campaigns = []

        for sample in SAMPLE_CAMPAIGNS:
            start = date.today() - timedelta(days=random.randint(1, 90))
            end = start + timedelta(days=random.randint(30, 180))

            campaign = Campaign(
                name=sample["name"],
                status=random.choice(STATUSES),
                platform=random.choice(PLATFORMS),
                budget=round(random.uniform(500, 50_000), 2),
                start_date=start,
                end_date=end,
                description=sample["description"],
                target_audience=sample["target_audience"],
            )
            db.session.add(campaign)
            campaigns.append(campaign)

        db.session.flush()  # assign IDs

        # Create 1-3 insight snapshots per campaign
        for campaign in campaigns:
            for days_ago in random.sample(range(0, 30), k=random.randint(1, 3)):
                impressions = random.randint(1_000, 200_000)
                clicks = random.randint(50, impressions // 3)
                conversions = random.randint(5, max(6, clicks // 5))

                insight = CampaignInsight(
                    campaign_id=campaign.id,
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    ctr=round(clicks / impressions * 100, 2),
                    cpc=round(random.uniform(0.10, 8.00), 2),
                    roi=round(random.uniform(-20, 400), 2),
                    engagement_likes=random.randint(20, 10_000),
                    engagement_shares=random.randint(5, 2_000),
                    engagement_comments=random.randint(2, 800),
                )
                db.session.add(insight)

        db.session.commit()
        print(f"✓ Seeded {len(campaigns)} campaigns with insights.")


if __name__ == "__main__":
    seed()
