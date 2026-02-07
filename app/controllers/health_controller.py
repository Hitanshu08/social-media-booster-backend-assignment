"""Health-check endpoint.

Useful for load balancers, container orchestrators, and uptime monitors.
"""

import logging

from flask import Blueprint, jsonify

from app.extensions import db

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Verify the application and database are reachable."""
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": str(exc),
                }
            ),
            503,
        )
