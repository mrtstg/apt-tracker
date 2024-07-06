import redis
import os


def get_redis_conn():
    conn = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        decode_responses=True,
    )
    yield conn
    conn.close()
