import time

class CacheManager:
    """Ein einfacher In-Memory-Cache mit Verfallszeit."""
    def __init__(self, ttl_seconds=300):
        self._cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        """Holt einen Wert aus dem Cache, wenn er gültig ist."""
        if key in self._cache:
            entry_time, value = self._cache[key]
            if time.time() - entry_time < self.ttl:
                print(f"Cache HIT für Schlüssel: {key}")
                return value
            else:
                print(f"Cache EXPIRED für Schlüssel: {key}")
                del self._cache[key]
        print(f"Cache MISS für Schlüssel: {key}")
        return None

    def set(self, key, value):
        """Setzt einen Wert im Cache."""
        print(f"Cache SET für Schlüssel: {key}")
        self._cache[key] = (time.time(), value)

    def clear(self):
        """Leert den gesamten Cache."""
        self._cache = {}