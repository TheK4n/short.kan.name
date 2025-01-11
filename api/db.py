import redis


__all__ = ["KeyNotExistsError", "DB"]


class KeyNotExistsError(Exception):
    pass


class DB:
    def __init__(self, host: str, port: int):
        pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.connection = redis.Redis(connection_pool=pool)

    def set(self, key: str, value: str, ttl: int):
        self.connection.hmset(key, {"url": value})
        self.connection.expire(key, ttl)

    def set_one_time(self, key: str, value: str, ttl: int):
        self.connection.hmset(key, {"url": value, "one-time": "true"})
        self.connection.expire(key, ttl)

    def get(self, key: str) -> str:
        value, one_time, *_ = self.connection.hmget(key, "url", "one-time")
        if not value:
            raise KeyNotExistsError(f"Key '{key}' not exists")

        if one_time:
            self.connection.delete(key)

        return value.decode()

    def exists(self, key: str) -> bool:
        return bool(self.connection.exists(key))  # bool because 'exists' returns number of keys
