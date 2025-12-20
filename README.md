# Songs API

Production-ready REST API built with Flask, MongoDB, and modern Python patterns.

## Quick Start

### Docker Compose (Recommended)
```bash
# Optional: Set MongoDB credentials via environment variables
# export MONGO_ROOT_USERNAME=myuser
# export MONGO_ROOT_PASSWORD=mypassword
# Or create a .env file with these variables

docker-compose up -d
# API: http://localhost:5000
# Swagger: http://localhost:5000/docs
```

### Local Development
```bash
# Start MongoDB
docker run -d --name songs_db -p 27017:27017 mongo:7.0

# Install dependencies
make install

# Setup environment (optional - for custom MongoDB credentials)
# cp .env.example .env
# Edit .env with your MongoDB username/password if needed

# Initialize database and seed data
make seed  # Seeds songs + test user (testuser/testpass)
# Note: Passwords are stored as secure hashes in the database, never as plain text

# Run
make run-dev  # Development with auto-reload
make run      # Production-like with gunicorn
```

## Configuration

Essential environment variables (see `.env.example` for all options):

### Docker Compose Variables

When using Docker Compose, you can set these variables in a `.env` file or export them:

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_ROOT_USERNAME` | `admin` | MongoDB root username |
| `MONGO_ROOT_PASSWORD` | `adminpassword` | MongoDB root password |
| `MONGO_DB_NAME` | `songs_db` | MongoDB database name |
| `JWT_SECRET_KEY` | `change-this-secret-key-in-production` | JWT secret key |

### Application Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Runtime: `local`, `development`, `production` |
| `MONGO_URI` | Auto-built | MongoDB connection string (auto-built from components if not provided) |
| `MONGO_DB_NAME` | `songs_db` | Database name |
| `MONGO_ROOT_USERNAME` | `admin` | MongoDB root username (used to build MONGO_URI) |
| `MONGO_ROOT_PASSWORD` | `adminpassword` | MongoDB root password (used to build MONGO_URI) |
| `MONGO_HOST` | `localhost` | MongoDB host (used to build MONGO_URI) |
| `MONGO_PORT` | `27017` | MongoDB port (used to build MONGO_URI) |
| `JWT_SECRET_KEY` | - | **Required** - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `LOG_FORMAT` | `text` | `text` (dev) or `json` (production) |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_DEFAULT` | `100 per minute` | Default rate limit |
| `RATE_LIMIT_STORAGE_URI` | `memory://` | `memory://` (dev) or `redis://host:port` (production) |

**Production example:**
```bash
ENVIRONMENT=production
MONGO_URI=mongodb://user:pass@host:27017/songs_db
JWT_SECRET_KEY=<generated-secret>
LOG_FORMAT=json
RATE_LIMIT_STORAGE_URI=redis://redis:6379
```

## API Endpoints

All routes require JWT authentication (except `/api/v1/health`, `/api/v1/auth/login`, and `/api/v1/auth/register`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login to get JWT token |
| GET | `/api/v1/songs` | List songs (pagination: `page`, `page_size`) |
| GET | `/api/v1/songs/difficulty/average` | Average difficulty (`level` optional) |
| GET | `/api/v1/songs/search` | Search by artist/title (`message`, `page`, `page_size`) |
| POST | `/api/v1/songs/ratings` | Add rating (`{"song_id": "...", "rating": 1-5}`) |
| GET | `/api/v1/songs/<song_id>/ratings` | Get rating stats |

**Authentication & Seed Data:**

A test user is automatically seeded when you run `make seed` or `uv run flask seed-users`:
- **Username:** `testuser`
- **Password:** `testpass`

**Important Security Note:** Passwords are stored as secure hashes (using Werkzeug's password hashing) in the database, never as plain text. The seed script creates a user with a hashed password, and the login endpoint verifies passwords against these hashes.

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword123"}'

# Login with seeded test user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Response: {"access_token": "...", "token_type": "bearer"}
# Use token (IMPORTANT: Include "Bearer " prefix before the token)
curl -X GET http://localhost:8000/api/v1/songs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Features

- **MongoEngine ODM** with schema validation
- **Unit of Work pattern** for clean data access
- **JWT Authentication** with PyJWT
- **Pydantic Validation** for request/response
- **OpenAPI/Swagger** docs at `/docs`
- **Structured Logging** (JSON in production, colored text in dev)
- **Rate Limiting** (per-user/IP, Redis support)
- **Environment-aware** configuration (local/development/production)

## Commands

```bash
make install       # Install dependencies
make install-prod  # Production dependencies only
make run           # Run with gunicorn
make run-dev       # Run with auto-reload
make test          # Run tests
make test-cov      # Tests with coverage
make lint          # Check code
make lint-fix      # Auto-fix issues
make format        # Format code

# Database & Seeding
make init-db       # Initialize database and create indexes
make seed-songs    # Seed songs from songs.json
make seed-users    # Seed test user (testuser/testpass)
make seed          # Initialize DB and seed all data (songs + test user)
```

## Seed Data

The application includes seed data for development and testing:

- **Songs:** Run `make seed-songs` to populate the database with songs from `songs.json`
- **Test User:** Run `make seed-users` to create a test user:
  - Username: `testuser`
  - Password: `testpass`
  - **Note:** The password is stored as a secure hash in the database (using Werkzeug's password hashing), never as plain text

You can run `make seed` to initialize the database and seed all data at once.

## Testing

```bash
make test
make test-cov
# Or in Docker:
docker-compose run --rm api pytest
```

## Architecture

```
Routes → Services → UoW → MongoEngine
```

- **Routes** (`api/v1/routes.py`): HTTP handling, validation
- **Services** (`services/`): Business logic
- **Unit of Work** (`uow.py`): Repository pattern
- **Models** (`models/documents.py`): ODM documents
- **Settings** (`settings.py`): Environment configuration

## Deployment

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Configure environment
export ENVIRONMENT=production
export JWT_SECRET_KEY=<secret>
export MONGO_URI=<mongo-uri>
export LOG_FORMAT=json
export RATE_LIMIT_STORAGE_URI=redis://redis:6379

# Install and run
make install-prod
make run
```

## Requirements

- Python 3.14+
- MongoDB
- uv package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Redis (optional, for production rate limiting)

## License

MIT
