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

    def cache_url_and_get_id(self, url: str, one_time: bool) -> str:
        shorted_url_id = self.__generate_unique()
        if one_time:
            self.__db.set_one_time(shorted_url_id, url, self.__ttl)
        self.__db.set(shorted_url_id, url, self.__ttl)
        return shorted_url_id

    def __generate_unique(self) -> str:
        while True:
            random_url_id = self.__generate_random()
            if not self.__db.exists(random_url_id):
                return random_url_id

    def __generate_random(self):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for _ in range(self.__length))


class Expander:
    def __init__(self):
        self.__connect_database()

    def __connect_database(self):
        self.__db = DB()

    def expand(self, id: str) -> str:
        try:
            result = self.__db.get(id)
        except KeyNotExistsError:
            raise URLNotShortenedException
        return result

