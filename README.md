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
- ✅ **Runtime Environments**: LOCAL, DEVELOPMENT, PRODUCTION configurations
- ✅ **Structured Logging**: Loguru with JSON logging for production
- ✅ **Rate Limiting**: Per-user/IP rate limiting with Redis support
- ✅ **Production Ready**: Gunicorn, environment-based config, comprehensive tests

## Requirements

- Python 3.14+
- MongoDB (Docker recommended)
- uv (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Quick Start

### 1. Docker Compose (Recommended)

```bash
# Start MongoDB and API
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

**Access:**
- API: http://localhost:5000
- Swagger: http://localhost:5000/docs

### 2. Local Development

**Start MongoDB:**
```bash
docker run -d --name songs_db -p 27017:27017 mongo:7.0
```

**Setup and run:**
```bash
# Install dependencies
make install

# Copy and configure environment
cp .env.sample .env
# Edit .env with your settings

# Initialize database
export FLASK_APP=wsgi.py
uv run flask init-db
uv run flask seed-songs

# Run with auto-reload (development)
make run-dev

# Or run with gunicorn (production-like)
make run
```

**Access:**
- API: http://localhost:8000 (default for `make run`)
- Swagger: http://localhost:8000/docs

## API Documentation

Access the interactive **Swagger UI** at `/docs` endpoint once the server is running:
- Docker Compose: http://localhost:5000/docs
- Local Development: http://localhost:8000/docs

Features:
- Interactive API testing
- Request/response examples
- Schema validation info
- JWT authentication testing (click "Authorize" button)


## Configuration

Configure via environment variables or `.env` file (see `.env.sample` for all options):

### Essential Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Runtime environment: `local`, `development`, `production` |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | `songs_db` | Database name |
| `JWT_SECRET_KEY` | - | **Required for production** - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

### Logging (Environment-Specific)

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FORMAT` | `text` | Log format: `text` (colored, dev) or `json` (production) |

**Automatic behavior:**
- **LOCAL/DEVELOPMENT**: Human-readable colored logs
- **PRODUCTION**: Structured JSON logs with request context, user tracking, exception details

### Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `RATE_LIMIT_DEFAULT` | `100 per minute` | Default rate limit for all endpoints |
| `RATE_LIMIT_STORAGE_URI` | `memory://` | Storage backend: `memory://` (dev) or `redis://host:port` (production) |

**Features:**
- Authenticated users tracked by username
- Anonymous users tracked by IP address
- Custom limits per endpoint supported
- Rate limit headers in all responses: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Returns `429 Too Many Requests` when exceeded

### Production Configuration Example

```bash
# .env
ENVIRONMENT=production
MONGO_URI=mongodb://user:pass@mongo-host:27017/songs_db
JWT_SECRET_KEY=<your-secure-random-key>
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100 per minute
RATE_LIMIT_STORAGE_URI=redis://redis:6379
```

## Key Features

### Runtime Environments

Three distinct environments with automatic configuration:
- **LOCAL**: Development with colored logs, debug info, memory rate limiting
- **DEVELOPMENT**: Deployed dev environment with readable logs
- **PRODUCTION**: JSON structured logs, Redis rate limiting, optimized settings

Set via `ENVIRONMENT=local|development|production`

### Structured Logging

**Development/Local:**
```
2025-12-17 22:52:50 | INFO     | songs_api:log_response:82 | GET /api/v1/songs - 200
```

**Production (JSON):**
```json
{
  "timestamp": "2025-12-17T22:52:50.916157+03:30",
  "level": "INFO",
  "message": "GET /api/v1/songs - 200",
  "request": {"method": "GET", "path": "/api/v1/songs", "remote_addr": "192.168.1.1"},
  "status_code": 200,
  "user": "admin"
}
```

All requests/responses automatically logged with context, user info, and exceptions.

### Rate Limiting

- Default: 100 requests per minute per user/IP
- Authenticated users tracked by username
- Anonymous users tracked by IP address
- Returns `429 Too Many Requests` with retry info
- Rate limit headers included: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Configurable storage: Memory (dev) or Redis (production)

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
curl -X POST http://localhost:8000/api/v1/auth/login \
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
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/songs
```

## Makefile Commands

```bash
make help          # Show all available commands
make install       # Install all dependencies (including dev tools)
make install-prod  # Install production dependencies only
make run           # Run with gunicorn (production-like)
make run-dev       # Run with gunicorn + auto-reload (development)
make test          # Run tests
make test-cov      # Run tests with coverage report
make lint          # Check code with ruff
make lint-fix      # Auto-fix linting issues
make format        # Format code with ruff
make clean         # Remove generated files
```

## Run Tests

```bash
# Local
make test

# With coverage
make test-cov

# In Docker
docker-compose run --rm api pytest
```

## Architecture

**Layered Architecture:**
```
Routes (HTTP) → Services (Business Logic) → UoW (Data Access) → MongoEngine (ODM)
```

**Key Components:**
- **Routes** (`api/v1/routes.py`): HTTP handling, validation decorators
- **Services** (`services/`): `AuthService`, `SongsService`, `RatingsService`
- **Unit of Work** (`uow.py`): Repository pattern for data access
- **Models** (`models/documents.py`): `Song`, `Rating`, `RatingStats` ODM
- **Schemas** (`schemas.py`): Pydantic request/response validation
- **Settings** (`settings.py`): Environment-based configuration
- **Logging** (`logging_config.py`): Loguru with environment-specific formatting
- **Rate Limiting** (`rate_limiter.py`): Flask-Limiter with user/IP tracking
- **JWT Auth** (`security/jwt_auth.py`): Token generation/validation

## Deployment

### Production Checklist

```bash
# 1. Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Configure environment
export ENVIRONMENT=production
export JWT_SECRET_KEY=<generated-secret>
export MONGO_URI=mongodb://user:pass@host:27017/songs_db
export LOG_FORMAT=json
export RATE_LIMIT_STORAGE_URI=redis://redis:6379

# 3. Install dependencies
make install-prod

# 4. Initialize database
export FLASK_APP=wsgi.py
uv run flask init-db
uv run flask seed-songs

# 5. Run with gunicorn
make run
# Or customize:
# gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
```

### Docker Deployment

```bash
# Build
docker build -t songs-api .

# Run with docker-compose
docker-compose -f docker-compose.yml up -d

# Or run manually
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e MONGO_URI=mongodb://host.docker.internal:27017 \
  -e JWT_SECRET_KEY=<your-secret> \
  songs-api
```

### Production Requirements

- **MongoDB**: Replica set recommended for production
- **Redis**: Required for distributed rate limiting
- **Gunicorn**: Multi-worker WSGI server (included)
- **Reverse Proxy**: Nginx/Traefik recommended for SSL termination
- **Monitoring**: Use JSON logs with ELK/Splunk/Datadog

## Project Structure

```
songs_project/
├── songs_api/
│   ├── api/v1/          # API routes and error handling
│   ├── models/          # MongoEngine documents
│   ├── services/        # Business logic layer
│   ├── security/        # JWT authentication
│   ├── utils/           # Validation decorators
│   ├── __init__.py      # Flask app factory
│   ├── database.py      # MongoDB connection
│   ├── logging_config.py # Loguru configuration
│   ├── rate_limiter.py  # Rate limiting setup
│   ├── schemas.py       # Pydantic models
│   ├── settings.py      # Environment configuration
│   └── uow.py           # Unit of Work pattern
├── tests/               # Pytest test suite
├── docs/                # Additional documentation
├── .env.sample          # Environment variables template
├── Makefile             # Common commands
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Container image
└── pyproject.toml       # Dependencies and tools
```

## Documentation

- **[Configuration Guide](docs/CONFIGURATION.md)** - Complete environment configuration reference
- **[Rate Limiting Guide](docs/RATE_LIMITING.md)** - Rate limiting details and examples
- **[Features Overview](docs/FEATURES.md)** - Detailed features documentation
- **Swagger UI** - Interactive API docs at `/docs` when running

## License

MIT


