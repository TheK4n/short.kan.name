import string
import random
from exceptions import URLNotShortenedException
from db import DB, KeyNotExistsError


__all__ = ["URL", "expand"]


class URL:
    def __init__(self, db: DB, ttl: int, length: int):
        self.__db = db
        self.__ttl = ttl
        self.__length = length

    def cache(self, url_to_be_shortened: str) -> str:
        shorted_url_id = self.__generate_unique()
        self.__db.set(shorted_url_id, url_to_be_shortened, self.__ttl)
        return shorted_url_id

    def cache_one_time(self, url_to_be_shortened: str) -> str:
        shorted_url_id = self.__generate_unique()
        self.__db.set_one_time(shorted_url_id, url_to_be_shortened, self.__ttl)
        return shorted_url_id

    def __generate_unique(self) -> str:
        while True:
            random_url_id = self.__generate_random()
            if not self.__db.exists(random_url_id):
                return random_url_id

    def __generate_random(self):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for _ in range(self.__length))


def expand(db: DB, id: str) -> str:
    try:
        result = db.get(id)
    except KeyNotExistsError:
        raise URLNotShortenedException
    return result

