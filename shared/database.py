import redis
from dotenv import load_dotenv
import os

# Redis configuration
load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Redis Connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)