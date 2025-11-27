#!/bin/bash

# Health check script for monitoring

API_URL="${API_URL:-http://localhost:8000}"

echo "Checking API health at $API_URL..."

response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")

if [ "$response" = "200" ]; then
    echo "✓ API is healthy (HTTP $response)"
    exit 0
else
    echo "✗ API is unhealthy (HTTP $response)"
    exit 1
fi
