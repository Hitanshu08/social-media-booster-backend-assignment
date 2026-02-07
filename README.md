# Social Media Booster Backend

A RESTful API for managing social-media advertising campaigns, performance
insights, and dashboard metrics. Built with **Flask**, **PostgreSQL**, and an
**MVC** architecture.

---

## Architecture

```
app/
├── __init__.py              # Application factory
├── extensions.py            # Flask extension instances
├── controllers/             # Route handlers (Views in MVC)
│   ├── campaign_controller.py
│   ├── dashboard_controller.py
│   └── health_controller.py
├── models/                  # SQLAlchemy ORM models
│   ├── campaign.py
│   └── campaign_insight.py
├── schemas/                 # Marshmallow schemas (validation & serialisation)
│   └── campaign.py
├── services/                # Business logic layer
│   ├── campaign_service.py
│   ├── dashboard_service.py
│   └── insight_service.py
└── middleware/
    └── error_handler.py     # Centralised JSON error responses
```

| Layer        | Responsibility                                   |
|--------------|--------------------------------------------------|
| Controllers  | Parse HTTP requests, call services, return JSON  |
| Services     | Business rules, querying, transactions           |
| Models       | ORM mapping to PostgreSQL tables                 |
| Schemas      | Request validation & response serialisation      |
| Middleware   | Cross-cutting concerns (error handling, logging) |

---

## API Endpoints

| Method   | Path                             | Description            |
|----------|----------------------------------|------------------------|
| `GET`    | `/api/campaigns`                 | List campaigns         |
| `POST`   | `/api/campaigns`                 | Create a campaign      |
| `GET`    | `/api/campaigns/:id`             | Get a campaign         |
| `PATCH`  | `/api/campaigns/:id`             | Update a campaign      |
| `DELETE` | `/api/campaigns/:id`             | Delete a campaign      |
| `GET`    | `/api/campaigns/:id/insights`    | Get campaign insights  |
| `GET`    | `/api/dashboard/metrics`         | Dashboard metrics      |
| `GET`    | `/api/health`                    | Health check           |

Full specification: [`openapi.yaml`](openapi.yaml)

---

## Prerequisites

- **Python 3.10+**
- **PostgreSQL 14+** (with `pgcrypto` and `pg_trgm` extensions)

---

## Getting Started

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd social-media-booster-backend-assignment

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3. Create the database and apply schema

```bash
createdb social_booster

psql -d social_booster -f db-schema.sql
```

### 4. (Optional) Initialise Flask-Migrate for future migrations

```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### 5. Seed sample data

```bash
python seed.py
```

### 6. Run the development server

```bash
python run.py
# or
flask run --port 3000
```

The API will be available at `http://localhost:3000/api`.

---

## Running Tests

```bash
# Create a test database
createdb social_booster_test
psql -d social_booster_test -f db-schema.sql

# Run tests
pytest -v

# With coverage
pytest --cov=app --cov-report=term-missing
```

---

## Production Deployment

```bash
gunicorn "app:create_app('production')" --bind 0.0.0.0:3000 --workers 4
```

---

## Environment Variables

| Variable            | Description                   | Default                                                   |
|---------------------|-------------------------------|-----------------------------------------------------------|
| `FLASK_ENV`         | Environment name              | `development`                                             |
| `DATABASE_URL`      | PostgreSQL connection URI     | `postgresql://postgres:postgres@localhost:5432/social_booster` |
| `TEST_DATABASE_URL` | Test database connection URI  | `postgresql://postgres:postgres@localhost:5432/social_booster_test` |
| `SECRET_KEY`        | Flask secret key              | `dev-secret-key`                                          |
