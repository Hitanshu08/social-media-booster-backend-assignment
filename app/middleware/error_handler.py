"""Centralised error handling for the application.

Provides consistent JSON error responses that match the OpenAPI
ErrorResponse / ValidationError schemas.
"""

import logging

from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Application-level error that renders as a JSON response."""

    def __init__(self, message, code="error", status_code=400, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


def register_error_handlers(app):
    """Register all error handlers on the Flask app."""

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation(error):
        """Convert marshmallow validation errors to the API format."""
        details = []
        for field, messages in error.messages.items():
            if isinstance(messages, list):
                for msg in messages:
                    details.append({"field": field, "message": msg})
            elif isinstance(messages, dict):
                for sub_field, sub_msgs in messages.items():
                    for msg in sub_msgs:
                        details.append(
                            {"field": f"{field}.{sub_field}", "message": msg}
                        )
            else:
                details.append({"field": field, "message": str(messages)})

        return (
            jsonify(
                {
                    "code": "validation_error",
                    "message": "Validation failed",
                    "details": details,
                }
            ),
            400,
        )

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom application errors."""
        body = {"code": error.code, "message": error.message}
        if error.details:
            body["details"] = error.details
        return jsonify(body), error.status_code

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database constraint violations."""
        from app.extensions import db

        db.session.rollback()
        logger.warning("Integrity error: %s", error.orig)
        return (
            jsonify(
                {
                    "code": "validation_error",
                    "message": "Database constraint violation",
                    "details": [
                        {"field": "_schema", "message": str(error.orig)}
                    ],
                }
            ),
            400,
        )

    @app.errorhandler(400)
    def handle_bad_request(error):
        return (
            jsonify(
                {
                    "code": "bad_request",
                    "message": getattr(error, "description", "Bad request"),
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        return (
            jsonify(
                {
                    "code": "not_found",
                    "message": getattr(
                        error, "description", "Resource not found"
                    ),
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return (
            jsonify(
                {
                    "code": "method_not_allowed",
                    "message": "Method not allowed",
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.exception("Internal server error")
        return (
            jsonify(
                {
                    "code": "server_error",
                    "message": "An internal server error occurred",
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Catch-all for unhandled exceptions."""
        if isinstance(error, HTTPException):
            return (
                jsonify({"code": "error", "message": error.description}),
                error.code,
            )
        logger.exception("Unexpected error: %s", error)
        return (
            jsonify(
                {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            ),
            500,
        )
