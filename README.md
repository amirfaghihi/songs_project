# Songs API

Production-ready REST API built with Flask, MongoDB, and modern Python patterns.

## Quick Start

### Docker Compose (Recommended)

#### Standalone Mode (Default)
Includes MongoDB, Redis, and API:
```bash
docker-compose up -d
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
# Redis: localhost:6379
```

#### With Custom Credentials
Create a `.env` file:
```bash
MONGO_ROOT_USERNAME=myadmin
MONGO_ROOT_PASSWORD=mypassword
```

Then run:
```bash
docker-compose up -d
```

#### With Replica Set (Production)
Create a `.env` file:
```bash
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=adminpassword
MONGODB_REPLICA_SET_MODE=primary
MONGODB_REPLICA_SET_NAME=rs0
MONGODB_REPLICA_SET_KEY=replicasetkey123
MONGO_URI=mongodb://root:adminpassword@mongodb:27017/songs_db?authSource=admin&replicaSet=rs0
```

Then run:
```bash
docker-compose up -d
```

### Local Development
```bash
# Start MongoDB (Bitnami image)
docker run -d --name songs_db -p 27017:27017 \
  -e MONGODB_ROOT_PASSWORD=adminpassword \
  bitnami/mongodb:latest

# Start Redis (optional, for caching and rate limiting)
docker run -d --name songs_redis -p 6379:6379 redis:7-alpine

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
make run      # Production-like with gunicorn (default: 4 workers)
make run 8    # Run with 8 workers
```

## Configuration

Essential environment variables (see `.env.example` for all options):

### Docker Compose Variables

When using Docker Compose, you can set these variables in a `.env` file or export them:

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_ROOT_USERNAME` | `root` | MongoDB root username (customizable) |
| `MONGO_ROOT_PASSWORD` | `adminpassword` | MongoDB root password |
| `MONGO_DB_NAME` | `songs_db` | MongoDB database name |
| `JWT_SECRET_KEY` | `change-this-secret-key-in-production` | JWT secret key |
| `GUNICORN_WORKERS` | `4` | Number of gunicorn worker processes |

#### Replica Set Configuration (Optional)

For production deployments with high availability:

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_REPLICA_SET_MODE` | _(empty)_ | Set to `primary` to enable replica set |
| `MONGODB_REPLICA_SET_NAME` | `rs0` | Replica set name |
| `MONGODB_REPLICA_SET_KEY` | `replicasetkey123` | Replica set key for security |
| `MONGO_URI` | _(auto-built)_ | Override to include `replicaSet` parameter |

**Example `.env` for Replica Set:**
```bash
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=securepassword
MONGODB_REPLICA_SET_MODE=primary
MONGODB_REPLICA_SET_NAME=rs0
MONGODB_REPLICA_SET_KEY=yoursecretkey
MONGO_URI=mongodb://root:securepassword@mongodb:27017/songs_db?authSource=admin&replicaSet=rs0
```

### Application Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Runtime: `local`, `development`, `production` |
| `MONGO_URI` | Auto-built | MongoDB connection string (auto-built from components if not provided) |
| `MONGO_DB_NAME` | `songs_db` | Database name |
| `MONGO_ROOT_USERNAME` | `root` | MongoDB root username (Bitnami default, used to build MONGO_URI) |
| `MONGO_ROOT_PASSWORD` | `adminpassword` | MongoDB root password (used to build MONGO_URI) |
| `MONGO_HOST` | `localhost` | MongoDB host (used to build MONGO_URI) |
| `MONGO_PORT` | `27017` | MongoDB port (used to build MONGO_URI) |
| `JWT_SECRET_KEY` | - | **Required** - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `LOG_FORMAT` | `text` | `text` (dev) or `json` (production) |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `RATE_LIMIT_DEFAULT` | `100 per minute` | Default rate limit |
| `RATE_LIMIT_REDIS_URL` | `redis://localhost:6379/1` | Redis URL for rate limiting |
| `RATE_LIMIT_STORAGE_URI` | `memory://` | `memory://` (dev) or `redis://host:port` (production) |
| `CACHE_ENABLED` | `true` | Enable Redis caching |
| `CACHE_REDIS_URL` | `redis://localhost:6379/0` | Redis URL for caching |
| `CACHE_DEFAULT_TTL` | `300` | Default cache TTL in seconds |
| `GUNICORN_WORKERS` | `4` | Number of gunicorn worker processes |

**Notes:** 
- When using Bitnami MongoDB, the root username is `root`, not `admin`.
- Redis is optional for development but **required for production** for caching and distributed rate limiting.

**Production examples:**

Standalone MongoDB with Redis:
```bash
ENVIRONMENT=production
MONGO_ROOT_USERNAME=prodadmin
MONGO_ROOT_PASSWORD=secure_password
MONGO_URI=mongodb://prodadmin:secure_password@host:27017/songs_db?authSource=admin
JWT_SECRET_KEY=<generated-secret>
LOG_FORMAT=json

# Redis Configuration (Required for Production)
CACHE_ENABLED=true
CACHE_REDIS_URL=redis://redis:6379/0
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=redis://redis:6379/1
RATE_LIMIT_STORAGE_URI=redis://redis:6379/1
```

With Replica Set and Redis:
```bash
ENVIRONMENT=production
MONGO_ROOT_USERNAME=prodadmin
MONGO_ROOT_PASSWORD=secure_password
MONGODB_REPLICA_SET_MODE=primary
MONGODB_REPLICA_SET_NAME=rs0
MONGO_URI=mongodb://prodadmin:secure_password@host:27017/songs_db?authSource=admin&replicaSet=rs0
JWT_SECRET_KEY=<generated-secret>
LOG_FORMAT=json

# Redis Configuration (Required for Production)
CACHE_ENABLED=true
CACHE_REDIS_URL=redis://redis:6379/0
CACHE_DEFAULT_TTL=300
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=redis://redis:6379/1
RATE_LIMIT_STORAGE_URI=redis://redis:6379/1
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
- **Redis Caching** for improved performance (production)
- **Rate Limiting** (per-user/IP, Redis-backed in production)
- **Environment-aware** configuration (local/development/production)

## Commands

```bash
make install       # Install dependencies
make install-prod  # Production dependencies only
make run           # Run with gunicorn (default: 4 workers)
make run 8         # Run with 8 workers (or any number)
make run-dev       # Run with auto-reload (default: 4 workers)
make run-dev 2     # Run dev mode with 2 workers
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
export GUNICORN_WORKERS=8  # Optional: configure number of workers

# Install and run
make install-prod
make run  # Uses default 4 workers, or specify: make run 8
```

### Configuring Gunicorn Workers

The number of gunicorn workers can be configured in several ways:

**Via Makefile (Local Development):**
```bash
make run 8        # Run with 8 workers
make run-dev 2    # Dev mode with 2 workers
```

**Via Docker Compose:**
```bash
# Set in .env file or environment
GUNICORN_WORKERS=8 docker-compose up -d
```

**Via Docker:**
```bash
docker run -e GUNICORN_WORKERS=8 ...
```

**Recommended:** Set workers to `(2 × CPU cores) + 1` for optimal performance.

## Requirements

- Python 3.14+
- MongoDB (Bitnami MongoDB image recommended for Docker deployments)
- Redis 7+ (optional for development, **required for production**)
- uv package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Technology Stack

- **Database:** Bitnami MongoDB 8.2+ (Docker)
  - Default admin username: `root` (customizable)
  - Supports standalone and replica set modes
  - Authentication enabled by default
- **Cache & Rate Limiting:** Redis 7+ (Alpine)
  - Database 0: Application caching
  - Database 1: Rate limiting
  - Persistent storage with AOF (Append-Only File)
- **Web Framework:** Flask with Gunicorn WSGI server (configurable workers, default: 4)
- **ODM:** MongoEngine for MongoDB object-document mapping
- **Authentication:** JWT tokens with PyJWT
- **Validation:** Pydantic for request/response schemas
- **Package Manager:** uv for fast dependency management

## MongoDB Configuration Modes

### Standalone Mode (Development)
- Single MongoDB instance
- No replica set configuration
- Suitable for local development and testing
- Default configuration

### Replica Set Mode (Production)
- High availability with automatic failover
- Data redundancy across multiple nodes
- Requires setting `MONGODB_REPLICA_SET_MODE=primary`
- Include `replicaSet` parameter in `MONGO_URI`

**Note:** For multi-node replica sets in production, you'll need multiple MongoDB containers. The current docker-compose.yml supports a single-node replica set, which enables replica set features for compatibility but doesn't provide actual redundancy.

## Redis Configuration

### Development Mode
- Caching: **Disabled** (cache is only enabled in production by default)
- Rate Limiting: **Memory-based** (no Redis required)
- You can enable Redis in development by setting `CACHE_ENABLED=true` and `RATE_LIMIT_STORAGE_URI=redis://localhost:6379/1`

### Production Mode
- Caching: **Enabled** with Redis (database 0)
  - Caches API responses for improved performance
  - Configurable TTL per endpoint
  - Automatic cache invalidation on data updates
- Rate Limiting: **Redis-backed** (database 1)
  - Distributed rate limiting across multiple workers
  - Per-user and per-IP tracking
  - Configurable limits per endpoint

### Redis Databases
The application uses two separate Redis databases:
- **Database 0:** Application caching (query results, computed data)
- **Database 1:** Rate limiting counters and metadata

This separation ensures rate limiting data doesn't interfere with cached application data.

## License

MIT
