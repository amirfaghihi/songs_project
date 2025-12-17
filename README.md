# Songs API (Flask + MongoDB)

Production-level REST API built with Flask, MongoEngine ODM, and modern Python patterns.

## Features

- ✅ **MongoEngine ODM**: Document-Object Mapper with schema validation
- ✅ **Unit of Work pattern**: Clean repository pattern for database operations
- ✅ **API Versioning**: All routes under `/api/v1` prefix
- ✅ **JWT Authentication**: Secure token-based authentication with PyJWT
- ✅ **Pydantic Validation**: Custom decorators for request/response validation
- ✅ **OpenAPI/Swagger**: Auto-generated API docs at `/docs` via flasgger
- ✅ **Scalability**: Precomputed rating stats for O(1) retrieval at scale
- ✅ **uv Package Manager**: Fast Rust-based dependency management

## Requirements

- Python 3.14+
- MongoDB (Docker recommended)
- uv (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Quick Start with Docker Compose (Recommended)

```bash
# Start both MongoDB and API
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Stop and remove volumes (data will be lost)
docker-compose down -v
```

**Access the API:**
- API: http://localhost:5000
- Swagger UI: http://localhost:5000/docs

---

## Local Development Setup

### Run MongoDB (Docker)

```bash
docker run --detach --name songs_db --publish 127.0.0.1:27017:27017 mongo:7.0
```

### Setup Python Environment

```bash
uv sync --all-extras
```

### Initialize Database & Seed Data

```bash
export FLASK_APP=wsgi.py
uv run flask init-db
uv run flask seed-songs
```

### Run the API

```bash
export FLASK_APP=wsgi.py
export FLASK_ENV=development
uv run flask run
```

## API Documentation

Once the server is running, access the interactive **Swagger UI** at:

**http://localhost:5000/docs**

Features:
- Interactive API testing
- Request/response examples
- Schema validation info
- JWT authentication testing (click "Authorize" button)

## Docker Build & Run

### Build Docker Image

```bash
docker build -t songs-api .
```

### Run with Docker (without compose)

```bash
# Run MongoDB
docker run -d --name mongodb -p 27017:27017 mongo:7.0

# Run API
docker run -d \
  --name songs-api \
  -p 5000:5000 \
  -e MONGO_URI=mongodb://host.docker.internal:27017 \
  -e MONGO_DB_NAME=songs_db \
  songs-api
```

---

## Configuration

All settings are managed via Pydantic Settings (environment variables or `.env` file):

- `MONGO_URI` (default: `mongodb://localhost:27017`)
- `MONGO_DB_NAME` (default: `songs_db`)
- `SONGS_JSON_PATH` (default: `songs.json`)
- `JWT_SECRET_KEY` (default: `your-secret-key-change-in-production` - **MUST change in production**)
- `JWT_ALGORITHM` (default: `HS256`)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (default: `60`)
- `ADMIN_USERNAME` (default: `admin`)
- `ADMIN_PASSWORD` (default: `admin`)

## API Routes (v1)

All routes require JWT Authentication (except `/api/v1/health` and `/api/v1/auth/login`):

| Method | Endpoint | Description | Query Params | Body |
|--------|----------|-------------|--------------|------|
| GET | `/api/v1/health` | Health check (no auth) | - | - |
| POST | `/api/v1/auth/login` | Login to get JWT token (no auth) | - | `{"username": "...", "password": "..."}` |
| GET | `/api/v1/songs` | List songs with pagination | `page`, `page_size` | - |
| GET | `/api/v1/songs/difficulty/average` | Average difficulty | `level` (optional) | - |
| GET | `/api/v1/songs/search` | Search by artist/title | `message`, `page`, `page_size` | - |
| POST | `/api/v1/songs/ratings` | Add a rating | - | `{"song_id": "...", "rating": 1-5}` |
| GET | `/api/v1/songs/<song_id>/ratings` | Get rating stats | - | - |

### Authentication

**Step 1: Login to get JWT token**

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Step 2: Use token in subsequent requests**

```bash
TOKEN="your-jwt-token-here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/v1/songs
```

## Run Tests

### Local Testing

```bash
uv run pytest
```

### Testing in Docker

```bash
# Run tests in a temporary container
docker-compose run --rm api pytest
```

## Architecture

### **Layered Architecture:**

```
Routes (HTTP) → Services (Business Logic) → UoW (Data Access) → MongoEngine (ODM)
```

**Layer Details:**

- **Routes Layer** (`api/v1/routes.py`): HTTP request/response handling, validation decorators
- **Service Layer** (`services/`): Business logic orchestration
  - `AuthService`: Authentication logic
  - `SongsService`: Songs-related operations
  - `RatingsService`: Ratings-related operations
- **Unit of Work** (`uow.py`): Repository pattern for data access
- **MongoEngine Documents** (`models/documents.py`): `Song`, `Rating`, `RatingStats` ODM models
- **Pydantic Schemas** (`schemas.py`): Request/response validation models
- **Custom Validation Decorators** (`utils/validation.py`): `@validate_request()`, `@validate_query()`
- **Pydantic Settings** (`settings.py`): Environment-based configuration
- **flasgger**: OpenAPI spec generation + Swagger UI at `/docs`
- **Database Manager** (`database.py`): Connection lifecycle management
- **JWT Auth** (`security/jwt_auth.py`): Token generation/validation
- **Centralized Error Handling** (`__init__.py`): ValidationError handler


