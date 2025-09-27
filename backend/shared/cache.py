import json
from django_redis import get_redis_connection

class CacheService:
    @staticmethod
    def set(key: str, value: dict, ttl: int | None = None):
        redis_conn = get_redis_connection("default")
        serialized_value = json.dumps(value)
        if ttl is not None:
            redis_conn.setex(key, ttl, serialized_value)
        else:
            redis_conn.set(key, serialized_value)

    @staticmethod
    def get(key: str):
        redis_conn = get_redis_connection("default")
        value = redis_conn.get(key)
        return json.loads(value) if value else None

    @staticmethod
    def delete(key: str):
        redis_conn = get_redis_connection("default")
        redis_conn.delete(key)

    @staticmethod
    def get_ttl(key: str) -> int | None:
        redis_conn = get_redis_connection("default")
        ttl = redis_conn.ttl(key)
        return ttl if ttl >= 0 else None
