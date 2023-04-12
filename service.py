import string
import random
from exceptions import URLNotShortenedException
from db import DB, KeyNotExistsError


__all__ = ["Cacher", "Expander"]


class Cacher:
    def __init__(self, ttl: int, length: int):
        self.__ttl = ttl
        self.__length = length
        self.__connect_database()

    def __connect_database(self):
        self.__db = DB()

    def cache_url(self, url: str, alias: str):
        self.__db.set(alias, url, self.__ttl)

    def cache_one_time_url(self, url: str, alias: str):
        self.__db.set_one_time(alias, url, self.__ttl)

    def is_cached(self, alias: str) -> bool:
        return self.__db.exists(alias)

    def generate_free_alias(self) -> str:
        while True:
            random_url_id = self.__generate_random()
            if not self.is_cached(random_url_id):
                return random_url_id

    def __generate_random(self):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for _ in range(self.__length))


class Expander:
    def __init__(self):
        self.__connect_database()

    def __connect_database(self):
        self.__db = DB()

    def expand(self, alias: str) -> str:
        try:
            result = self.__db.get(alias)
        except KeyNotExistsError:
            raise URLNotShortenedException
        return result

