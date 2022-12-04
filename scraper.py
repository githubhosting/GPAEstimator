import base64
import hashlib
from functools import wraps
from typing import Literal, Union
from abc import ABCMeta, abstractmethod

from requests import Session
from bs4 import BeautifulSoup


class Scraper(metaclass=ABCMeta):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.45 Safari/537.36",
        "X-Amzn-Trace-Id": "Root=1-61acac03-6279b8a6274777eb44d81aae",
        "X-Client-Data": "CJW2yQEIpLbJAQjEtskBCKmdygEIuevKAQjr8ssBCOaEzAEItoXMAQjLicwBCKyOzAEI3I7MARiOnssB"
    }

    def __init__(self):
        self.Se: Union["Session", None] = None

    def __enter__(self):
        self.Se = Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Se.close()
        self.Se = None

    def get_soap(self, URL, type_: Literal["GET", "POST"] = "GET", payload_=None) -> BeautifulSoup:
        if type_ == "GET":
            response = self.Se.get(URL, headers=self.HEADERS)
        elif type_ == "POST":
            response = self.Se.post(URL, data=payload_, headers=self.HEADERS)
        else:
            raise ValueError(f"invalid {type_=}")
        return BeautifulSoup(response.content, 'html.parser')

    def get_img(self, URL) -> bytes:
        return base64.encodebytes(self.Se.get(URL).content)


def cached(cache):
    def cashee(func):
        func.cache = cache

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            hasher = hashlib.md5()
            for arg in args: hasher.update(str(arg).encode())
            for _, val in kwargs.items():
                hasher.update(str(val).encode())
            _hash = hasher.hexdigest()
            try:
                r = func.cache[_hash]
                return r
            except KeyError:
                if result := func(self, *args, **kwargs): func.cache[_hash] = result
                return result

        return wrapper

    return cashee


def gen_usn(year: str, dept: str, i: int, head="1MS") -> str:
    return f"{head}{year}{dept}{i:03}"


def roll_range(start=1, stop=None):
    if stop is None: stop = float('inf')
    assert isinstance(start, int) and start > 0, \
        "start must be int > 0"
    i = start
    while i < stop:
        yield i
        i += 1
