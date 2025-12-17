# Configuration Guide

## Environment Setup

The application supports three runtime environments:

- **LOCAL**: Development on local machine (default)
- **DEVELOPMENT**: Deployed development environment
- **PRODUCTION**: Production environment

### Environment Variables

Copy `.env.sample` to `.env` and configure:

```bash
cp .env.sample .env
```

### Key Configuration Options

#### Environment
```bash
ENVIRONMENT=local  # Options: local, development, production
```

#### Logging
```bash
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=text          # text or json
```

- **LOCAL/DEVELOPMENT**: Human-readable colored text format
- **PRODUCTION**: Structured JSON format with request context

#### Rate Limiting
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100 per minute
RATE_LIMIT_STORAGE_URI=memory://  # Use redis://host:port for production
```

Rate limiting is automatically applied to all routes. For production, use Redis:
```bash
RATE_LIMIT_STORAGE_URI=redis://localhost:6379
```

## Logging Features

### Local/Development Logs
- Colored output for easy reading
- Full backtraces for debugging
- File and line number tracking

### Production Logs
- JSON structured format
- Request context (method, path, IP, user-agent)
- User tracking (if authenticated)
- Exception details
- Easy integration with log aggregation tools (ELK, Splunk, etc.)

Example production log:
```json
{
  "timestamp": "2025-12-17T22:52:50.916157+03:30",
  "level": "INFO",
  "message": "GET /api/v1/songs - 200",
  "module": "songs_api",
  "function": "log_response",
  "line": 82,
  "request": {
    "method": "GET",
    "path": "/api/v1/songs",
    "remote_addr": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  },
  "status_code": 200
}
```

## Rate Limiting

### Default Limits
All endpoints have a default rate limit (configured via `RATE_LIMIT_DEFAULT`).

### Custom Limits per Endpoint
To apply custom rate limits to specific endpoints, use the limiter decorator:

```python
from flask import current_app

@app.route('/api/v1/expensive-operation')
@current_app.extensions['limiter'].limit("10 per minute")
def expensive_operation():
    return {"status": "ok"}
```

### Rate Limit Responses
When rate limit is exceeded, returns:
```json
HTTP 429 Too Many Requests
{
  "error": "Rate limit exceeded",
  "message": "100 per 1 minute"
}
```

### Rate Limit Headers
Responses include rate limit information in headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

### User-based Rate Limiting
- Authenticated users are tracked by username
- Anonymous users are tracked by IP address
- This prevents one user from consuming all available requests

## MongoDB Configuration

```bash
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=songs_db
```

For production, use connection string with authentication:
```bash
MONGO_URI=mongodb://user:password@host:27017/songs_db?authSource=admin
```

## JWT Configuration

```bash
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Important**: Change `JWT_SECRET_KEY` in production to a strong random value:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Example Production Configuration

```bash
# Environment
ENVIRONMENT=production

# MongoDB
MONGO_URI=mongodb://user:pass@mongo-host:27017/songs_db?authSource=admin
MONGO_DB_NAME=songs_db

# JWT
JWT_SECRET_KEY=<generated-secure-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100 per minute
RATE_LIMIT_STORAGE_URI=redis://redis:6379

# API
API_TITLE=Songs API
API_VERSION=1.0.0
```

## Running the Application

### Local Development
```bash
make install
make run-dev
```

### Production
```bash
make install-prod
make run
```

Or with environment variables:
```bash
ENVIRONMENT=production LOG_FORMAT=json make run
```

