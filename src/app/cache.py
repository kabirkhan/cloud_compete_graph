from redis import Redis


class Cache:

    def __init__(self, host=None, key=None, testing=False):
        self.testing = testing

        if testing:
            self.cache = {}
        else:
            self.cache = Redis(host, port=6380, db=0, password=key, ssl=True)
    
    def get(self, key: str) -> str:
        return self.cache.get(key)

    def set(self, key: str, value: str, expire_after: int=300):
        if self.testing:
            self.cache[key] = value
        else:
            self.cache.set(key, value)
            if expire_after:
                self.cache.expire(key, time=expire_after)
