import redis

# Redis Connection
redis_client = redis.Redis(host="redis", port=6379, db=0)