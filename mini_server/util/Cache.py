from cachetools import TTLCache


class Cache:
    def __init__(self, maxsize=100, ttl=60):  # ttl是时间至生存（秒）
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def set(self, key, value):
        print(f"将 {key} 添加到缓存中。结果{value}")
        print(self)
        self.cache[key] = value

    def get(self, key):
        print(f"从缓存中获取 {key},结果{self.cache.get(key)}")
        print(self)
        return self.cache.get(key)