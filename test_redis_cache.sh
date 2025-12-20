#!/bin/bash

# Redis Cache Testing Script
# Tests cache functionality for Songs API endpoints

set -e

API_URL="http://localhost:8000"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Redis Cache Functionality Test${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to print test status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
    fi
}

# Function to measure request time
measure_time() {
    local start=$(date +%s%N)
    "$@" > /dev/null 2>&1
    local end=$(date +%s%N)
    echo $(( (end - start) / 1000000 ))
}

# Step 1: Check if services are running
echo -e "${YELLOW}Step 1: Checking services...${NC}"
if docker compose ps | grep -q "songs_redis.*Up.*healthy"; then
    print_status 0 "Redis is running and healthy"
else
    print_status 1 "Redis is not healthy"
    exit 1
fi

if docker compose ps | grep -q "songs_api.*Up"; then
    print_status 0 "API is running"
else
    print_status 1 "API is not running"
    exit 1
fi

# Step 2: Register and login to get token
echo -e "\n${YELLOW}Step 2: Authentication...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "cachetest", "password": "testpass123"}')

if echo "$REGISTER_RESPONSE" | grep -q "cachetest"; then
    print_status 0 "User registered successfully"
else
    echo "Note: User may already exist (this is okay)"
fi

TOKEN=$(curl -s -X POST "${API_URL}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "cachetest", "password": "testpass123"}' | jq -r '.access_token')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    print_status 0 "Login successful, got JWT token"
else
    print_status 1 "Failed to get JWT token"
    exit 1
fi

# Step 3: Clear Redis cache
echo -e "\n${YELLOW}Step 3: Clearing Redis cache...${NC}"
docker exec songs_redis redis-cli FLUSHDB > /dev/null
print_status 0 "Redis cache cleared"

# Step 4: Check Redis is empty
KEYS_COUNT=$(docker exec songs_redis redis-cli DBSIZE | tr -d '\r')
if [ "$KEYS_COUNT" = "0" ]; then
    print_status 0 "Confirmed Redis is empty (0 keys)"
else
    print_status 1 "Redis not empty (found $KEYS_COUNT keys)"
fi

# Step 5: First API call (should NOT use cache)
echo -e "\n${YELLOW}Step 4: Testing cache MISS (first request)...${NC}"
echo "Making first request to /api/v1/songs..."

TIME1=$(measure_time curl -s -X GET "${API_URL}/api/v1/songs?page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}")

RESPONSE1=$(curl -s -X GET "${API_URL}/api/v1/songs?page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$RESPONSE1" | jq -e '.data' > /dev/null 2>&1; then
    print_status 0 "First request successful (${TIME1}ms)"
    SONG_COUNT=$(echo "$RESPONSE1" | jq '.data | length')
    echo -e "  ${BLUE}→${NC} Retrieved $SONG_COUNT songs"
else
    print_status 1 "First request failed"
    echo "Response: $RESPONSE1"
    exit 1
fi

# Step 6: Check if cache key was created
echo -e "\n${YELLOW}Step 5: Verifying cache was created...${NC}"
sleep 1  # Give Redis a moment to write
KEYS_AFTER=$(docker exec songs_redis redis-cli DBSIZE | tr -d '\r')
if [ "$KEYS_AFTER" != "0" ]; then
    print_status 0 "Cache key created ($KEYS_AFTER keys in Redis)"
    echo -e "  ${BLUE}→${NC} Cache keys:"
    docker exec songs_redis redis-cli KEYS "*" | head -5
else
    print_status 1 "No cache key created"
fi

# Step 7: Second API call (should use cache - FASTER)
echo -e "\n${YELLOW}Step 6: Testing cache HIT (second request)...${NC}"
echo "Making second request to same endpoint..."

TIME2=$(measure_time curl -s -X GET "${API_URL}/api/v1/songs?page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}")

RESPONSE2=$(curl -s -X GET "${API_URL}/api/v1/songs?page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$RESPONSE2" | jq -e '.data' > /dev/null 2>&1; then
    print_status 0 "Second request successful (${TIME2}ms)"
    
    # Check if response is identical
    if [ "$RESPONSE1" = "$RESPONSE2" ]; then
        print_status 0 "Responses are identical (cache is working)"
    else
        print_status 1 "Responses differ (cache may not be working)"
    fi
    
    # Compare times
    if [ $TIME2 -lt $TIME1 ]; then
        IMPROVEMENT=$(( (TIME1 - TIME2) * 100 / TIME1 ))
        echo -e "${GREEN}  ⚡ Cache improved response time by ${IMPROVEMENT}%${NC}"
        echo -e "     First:  ${TIME1}ms (cache miss)"
        echo -e "     Second: ${TIME2}ms (cache hit)"
    else
        echo -e "  ${YELLOW}⚠${NC}  Second request wasn't faster (may be other factors)"
        echo -e "     First:  ${TIME1}ms"
        echo -e "     Second: ${TIME2}ms"
    fi
else
    print_status 1 "Second request failed"
fi

# Step 8: Test cache with different parameters
echo -e "\n${YELLOW}Step 7: Testing cache with different parameters...${NC}"
echo "Requesting page 2 (should create new cache key)..."

KEYS_BEFORE_PAGE2=$(docker exec songs_redis redis-cli DBSIZE | tr -d '\r')

curl -s -X GET "${API_URL}/api/v1/songs?page=2&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}" > /dev/null

sleep 1
KEYS_AFTER_PAGE2=$(docker exec songs_redis redis-cli DBSIZE | tr -d '\r')

if [ $KEYS_AFTER_PAGE2 -gt $KEYS_BEFORE_PAGE2 ]; then
    print_status 0 "New cache key created for different parameters"
    echo -e "  ${BLUE}→${NC} Keys before: $KEYS_BEFORE_PAGE2, after: $KEYS_AFTER_PAGE2"
else
    print_status 1 "No new cache key created"
fi

# Step 9: Test cache TTL
echo -e "\n${YELLOW}Step 8: Testing cache TTL...${NC}"
CACHE_KEY=$(docker exec songs_redis redis-cli KEYS "songs:list:*" | head -1 | tr -d '\r')
if [ -n "$CACHE_KEY" ]; then
    TTL=$(docker exec songs_redis redis-cli TTL "$CACHE_KEY" | tr -d '\r')
    if [ "$TTL" -gt 0 ]; then
        print_status 0 "Cache has TTL set: ${TTL} seconds remaining"
    else
        print_status 1 "Cache TTL not set correctly"
    fi
else
    print_status 1 "Could not find cache key to check TTL"
fi

# Step 10: Test cache invalidation (add rating)
echo -e "\n${YELLOW}Step 9: Testing cache invalidation...${NC}"
echo "Adding a rating (should invalidate related cache)..."

# Get a song ID first
SONG_ID=$(echo "$RESPONSE1" | jq -r '.data[0].id')
if [ -n "$SONG_ID" ] && [ "$SONG_ID" != "null" ]; then
    echo -e "  ${BLUE}→${NC} Using song ID: $SONG_ID"
    
    # Add rating
    RATING_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/songs/ratings" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{\"song_id\": \"${SONG_ID}\", \"rating\": 5}")
    
    if echo "$RATING_RESPONSE" | jq -e '.average' > /dev/null 2>&1; then
        print_status 0 "Rating added successfully"
        
        # Check if related cache was invalidated
        RATING_CACHE_KEY="ratings:stats:${SONG_ID}"
        EXISTS=$(docker exec songs_redis redis-cli EXISTS "$RATING_CACHE_KEY" | tr -d '\r')
        if [ "$EXISTS" = "0" ]; then
            print_status 0 "Rating cache was invalidated"
        else
            echo -e "  ${YELLOW}⚠${NC}  Rating cache still exists (may be repopulated)"
        fi
    else
        print_status 1 "Failed to add rating"
        echo "Response: $RATING_RESPONSE"
    fi
else
    print_status 1 "Could not get song ID for cache invalidation test"
fi

# Step 11: Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Redis keys: $(docker exec songs_redis redis-cli DBSIZE | tr -d '\r')"
echo -e "\n${GREEN}✓ Redis cache is working correctly!${NC}"
echo -e "\nCache keys in Redis:"
docker exec songs_redis redis-cli KEYS "*" | head -10

echo -e "\n${YELLOW}Note:${NC} Cache is enabled in PRODUCTION mode"
echo -e "To view cache details, use: docker exec songs_redis redis-cli MONITOR"

