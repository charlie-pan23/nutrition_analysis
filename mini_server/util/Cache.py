from cachetools import TTLCache


class Cache:
    def __init__(self, maxsize=100, ttl=10):  # ttl是时间至生存（秒）
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def set(self, key, value):
        self.cache[key] = value

    def get(self, key):
        return self.cache.get(key)