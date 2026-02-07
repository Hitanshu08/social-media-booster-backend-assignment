"""Dashboard API endpoints (Blueprint).

Routes:
    GET /api/dashboard/metrics   Aggregated metrics for charts
"""

import logging

from flask import Blueprint, jsonify

from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/metrics", methods=["GET"])
def get_metrics():
    """Return aggregated dashboard metrics."""
    metrics = DashboardService.get_metrics()
    return jsonify(metrics)
