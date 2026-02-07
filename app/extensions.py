"""Flask extension instances.

Extensions are instantiated here so they can be imported by other modules
without causing circular imports. They are initialised with the app in
the application factory (app/__init__.py).
"""

from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
