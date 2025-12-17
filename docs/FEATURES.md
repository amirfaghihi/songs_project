# Features Summary

## Runtime Environments

The application supports three distinct runtime environments:

### LOCAL (Default)
- Development on local machine
- Colored, human-readable logs
- Full debug information
- Memory-based rate limiting

### DEVELOPMENT
- Deployed development environment
- Human-readable logs
- Debug information enabled
- Can use Redis for rate limiting

### PRODUCTION
- Production environment
- **JSON structured logs** for log aggregation
- Minimal debug information
- Redis-based rate limiting recommended

**Configuration:**
```bash
ENVIRONMENT=local|development|production
```

## Structured Logging with Loguru

### Features
- **Environment-aware** logging configuration
- **JSON format** in production for easy parsing
- **Colored output** in development for readability
- **Request context** automatically included in logs
- **User tracking** for authenticated requests
- **Exception details** with full tracebacks

### Log Formats

#### Development/Local
```
2025-12-17 22:52:50 | INFO     | songs_api:create_app:25 | Starting Songs API in local mode
2025-12-17 22:52:51 | INFO     | songs_api:log_response:82 | GET /api/v1/songs - 200
```

#### Production (JSON)
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
  "status_code": 200,
  "user": "testuser"
}
```

### Automatic Request Logging

All requests are automatically logged with:
- HTTP method
- Request path
- Response status code
- Remote IP address
- Authenticated user (if applicable)

### Configuration
```bash
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL
LOG_FORMAT=text|json
```

## Rate Limiting

### Features
- **Per-user tracking** for authenticated users
- **Per-IP tracking** for anonymous users
- **Configurable limits** per endpoint
- **Multiple storage backends** (Memory, Redis)
- **Rate limit headers** in all responses
- **Automatic logging** of rate limit violations

### Default Protection
All endpoints automatically protected with default rate limit:
```bash
RATE_LIMIT_DEFAULT=100 per minute
```

### Storage Options

#### Memory (Development)
```bash
RATE_LIMIT_STORAGE_URI=memory://
```
- Fast and simple
- No external dependencies
- Not shared across servers
- Lost on restart

#### Redis (Production)
```bash
RATE_LIMIT_STORAGE_URI=redis://localhost:6379
```
- Persistent
- Shared across multiple servers
- Production-ready
- Requires Redis server

### Response Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1671321600
```

### Rate Limit Exceeded
```json
HTTP/1.1 429 Too Many Requests

{
  "error": "Rate limit exceeded",
  "message": "100 per 1 minute"
}
```

## Configuration Management

### Environment Variables
All configuration via environment variables:
- Follows 12-factor app principles
- Easy deployment to any platform
- Secure secrets management

### Settings File
- Type-safe configuration with Pydantic
- Automatic validation
- Clear documentation
- Default values for development

### Sample Configuration
Copy `.env.sample` to `.env`:
```bash
cp .env.sample .env
```

## Integration Benefits

### Logging + Rate Limiting
Rate limit violations are automatically logged:
```json
{
  "level": "WARNING",
  "message": "Rate limit exceeded for user:testuser on GET /api/v1/songs",
  "identifier": "user:testuser",
  "endpoint": "get_songs"
}
```

### Logging + Environment
Log format automatically adjusts based on environment:
- Production: JSON for ELK/Splunk/Datadog
- Development: Colored text for terminal

### Authentication + Rate Limiting
Authenticated users tracked separately from anonymous users:
- Fair resource allocation
- Per-user limits possible
- Abuse prevention

## Production Readiness Checklist

- [x] Environment-specific configuration
- [x] Structured JSON logging
- [x] Rate limiting with Redis support
- [x] Request/response logging
- [x] Error tracking with full context
- [x] User identification and tracking
- [x] Database connection management
- [x] JWT authentication
- [x] Comprehensive test coverage
- [x] Makefile for common operations

## Quick Start

### Development
```bash
# Install dependencies
make install

# Copy environment file
cp .env.sample .env

# Run with auto-reload
make run-dev
```

### Production
```bash
# Set environment
export ENVIRONMENT=production
export LOG_FORMAT=json
export RATE_LIMIT_STORAGE_URI=redis://redis:6379
export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Install dependencies
make install-prod

# Run with gunicorn
make run
```

## Documentation

- [Configuration Guide](CONFIGURATION.md) - Complete configuration reference
- [Rate Limiting Guide](RATE_LIMITING.md) - Rate limiting details and examples
- [README](../README.md) - Project overview and API documentation

