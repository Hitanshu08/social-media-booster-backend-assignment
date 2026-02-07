"""Application factory for the Social Booster Campaigns API."""

import logging
import os

from flask import Flask

from app.extensions import cors, db, migrate
from app.middleware.error_handler import register_error_handlers
from config import config


def create_app(config_name=None):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration environment name
                     ('development', 'testing', 'production').

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    # --------------- Logging ---------------
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # --------------- Extensions ---------------
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}},
        expose_headers=["X-Total-Count"],
    )

    # --------------- Blueprints ---------------
    from app.controllers.campaign_controller import campaign_bp
    from app.controllers.dashboard_controller import dashboard_bp
    from app.controllers.health_controller import health_bp

    app.register_blueprint(campaign_bp, url_prefix="/api/campaigns")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(health_bp, url_prefix="/api")

    # --------------- Error handlers ---------------
    register_error_handlers(app)

    app.logger.info("Application created with config: %s", config_name)
    return app
