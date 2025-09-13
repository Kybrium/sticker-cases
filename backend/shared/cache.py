import json
from django.core.cache import cache

class CacheService:

    @staticmethod
    def set(key: str, value: dict, ttl: int | None = None):
        cache.set(key, json.dumps(value), timeout=ttl)

    @staticmethod
    def get(key: str):
        result = cache.get(key)
        return json.loads(result) if result else None

    @staticmethod
    def delete(key: str):
        cache.delete(key)

    @staticmethod
    def is_active_key(telegram_id: str) -> bool:
        active_nonces = cache.get(f"active_nonces:{telegram_id}") or []
        return bool(active_nonces)

    @staticmethod
    def add_active_nonce(telegram_id: str, nonce: str):
        key = f"active_nonces:{telegram_id}"
        active_nonces = cache.get(key) or []
        active_nonces.append(nonce)
        cache.set(key, active_nonces, timeout=300)