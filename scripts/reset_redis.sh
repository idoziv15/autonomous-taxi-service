#!/bin/bash
echo "Clearing Redis data..."
docker exec -it autonomous-taxi-service_redis_1 redis-cli FLUSHALL