import time


class CacheService:
    """Simple in-memory TTL cache for TBA API responses."""

    _cache = {}
    DEFAULT_TTL = 300  # 5 minutes

    @classmethod
    def get(cls, key):
        entry = cls._cache.get(key)
        if entry and entry['expires'] > time.time():
            return entry['value']
        if entry:
            del cls._cache[key]
        return None

    @classmethod
    def set(cls, key, value, ttl=None):
        cls._cache[key] = {
            'value': value,
            'expires': time.time() + (ttl or cls.DEFAULT_TTL),
        }

    @classmethod
    def clear(cls):
        cls._cache.clear()
