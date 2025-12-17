# Rate Limiting Guide

## Overview

The Songs API includes built-in rate limiting to protect against abuse and ensure fair resource allocation.

## Default Behavior

- **All endpoints** have a default rate limit (configured via `RATE_LIMIT_DEFAULT`)
- Default: `100 per minute`
- Rate limits can be disabled for testing by setting `RATE_LIMIT_ENABLED=false`

## Identification

Users are identified for rate limiting by:
1. **Authenticated users**: Tracked by JWT username
2. **Anonymous users**: Tracked by IP address

This prevents one authenticated user from consuming all available requests and treats each anonymous user separately.

## Custom Rate Limits

### Per-Endpoint Limits

To apply custom rate limits to specific endpoints, use the limiter decorator:

```python
from flask import Blueprint, current_app

bp = Blueprint('api', __name__)
limiter = current_app.extensions.get('limiter')

@bp.route('/expensive-operation')
@limiter.limit("10 per minute")  # Custom limit
def expensive_operation():
    return {"status": "ok"}

@bp.route('/burst-allowed')
@limiter.limit("100 per hour; 10 per minute")  # Multiple limits
def burst_allowed():
    return {"status": "ok"}
```

### Exempt Endpoints

To exempt an endpoint from rate limiting:

```python
@bp.route('/health')
@limiter.exempt  # No rate limiting
def health():
    return {"status": "healthy"}
```

## Rate Limit Formats

```python
# Per minute
"100 per minute"
"10/minute"

# Per hour
"1000 per hour"
"500/hour"

# Per day
"10000 per day"

# Multiple limits (most restrictive applies)
"100 per hour; 10 per minute"
```

## Response Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1671321600
```

- `X-RateLimit-Limit`: Maximum requests allowed in the window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Rate Limit Exceeded Response

When rate limit is exceeded, the API returns:

```json
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1671321600

{
  "error": "Rate limit exceeded",
  "message": "100 per 1 minute"
}
```

## Storage Backends

### Memory (Default)
```bash
RATE_LIMIT_STORAGE_URI=memory://
```

Good for:
- Development
- Testing
- Single-server deployments

Limitations:
- Not shared across multiple servers
- Lost on restart

### Redis (Recommended for Production)
```bash
RATE_LIMIT_STORAGE_URI=redis://localhost:6379
```

Good for:
- Production environments
- Multi-server deployments
- Persistent rate limit tracking

Install Redis:
```bash
# macOS
brew install redis
redis-server

# Docker
docker run -d -p 6379:6379 redis:alpine

# Update .env
RATE_LIMIT_STORAGE_URI=redis://localhost:6379
```

### Redis with Authentication
```bash
RATE_LIMIT_STORAGE_URI=redis://:password@localhost:6379/0
```

## Configuration Examples

### Development
```bash
ENVIRONMENT=local
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=1000 per minute
RATE_LIMIT_STORAGE_URI=memory://
```

### Production
```bash
ENVIRONMENT=production
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100 per minute
RATE_LIMIT_STORAGE_URI=redis://redis:6379
```

### Testing
```bash
ENVIRONMENT=local
RATE_LIMIT_ENABLED=false
```

## Monitoring

Rate limit exceeded events are automatically logged:

```json
{
  "timestamp": "2025-12-17T22:52:50.916157+03:30",
  "level": "WARNING",
  "message": "Rate limit exceeded for user:testuser on GET /api/v1/songs",
  "identifier": "user:testuser",
  "endpoint": "get_songs"
}
```

## Best Practices

1. **Use Redis in production** for consistent rate limiting across multiple servers
2. **Set appropriate limits** based on your API's capacity and use case
3. **Monitor rate limit logs** to identify potential abuse or adjust limits
4. **Consider different limits** for different user tiers (if applicable)
5. **Exempt health checks** and monitoring endpoints from rate limiting
6. **Use burst allowances** for endpoints with variable load patterns

## Testing Rate Limits

```python
import requests

# Make requests until rate limited
for i in range(150):
    response = requests.get('http://localhost:8000/api/v1/songs', 
                           headers={'Authorization': 'Bearer YOUR_TOKEN'})
    print(f"Request {i+1}: {response.status_code}")
    if response.status_code == 429:
        print("Rate limited!")
        break
```

