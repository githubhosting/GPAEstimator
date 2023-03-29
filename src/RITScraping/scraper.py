import asyncio
import base64
import hashlib
import os
import pickle
import re
from functools import wraps
from pathlib import Path
from typing import Literal, Union

import aiohttp
from bs4 import BeautifulSoup


class Scraper:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.45 Safari/537.36",
        "X-Amzn-Trace-Id": "Root=1-61acac03-6279b8a6274777eb44d81aae",
        "X-Client-Data": "CJW2yQEIpLbJAQjEtskBCKmdygEIuevKAQjr8ssBCOaEzAEItoXMAQjLicwBCKyOzAEI3I7MARiOnssB"
    }

    Se: Union["aiohttp.ClientSession", None]
    encoding: str = None

    def __init__(self):
        self.Se = None

    async def __aenter__(self):
        self.Se = aiohttp.ClientSession()
        await self.Se.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.Se.__aexit__(exc_type, exc_val, exc_tb)
        self.Se = None

    @staticmethod
    async def img(encoded):
        return base64.encodebytes(encoded)

    async def get(self, session: "aiohttp.ClientSession", url: str):
        async with session.get(url, headers=self.HEADERS) as response:
            return await response.text(encoding=self.encoding)

    async def post(self, session: "aiohttp.ClientSession", url: str, data: dict[str, str] = None):
        async with session.post(url, data=data, headers=self.HEADERS) as response:
            return await response.text(encoding=self.encoding)

    @staticmethod
    async def gen_soup(response):
        return BeautifulSoup(await response, "html.parser")

    async def get_soups(self, *URLS, method: Literal["GET", "POST"] = "GET",
                        payload=None, async_worker=None) -> list[BeautifulSoup]:
        if async_worker is None:
            async def async_worker(soup):
                return await soup
        payload = payload or [None] * len(URLS)
        if len(URLS) == 1: URLS = [URLS[0]] * len(payload)
        assert len(URLS) == len(payload), \
            f"{len(URLS)=} != {len(payload)=}"
        if method == "GET":
            tasks = [self.gen_soup(self.get(self.Se, URL)) for URL in URLS]
        elif method == "POST":
            tasks = [self.gen_soup(self.post(self.Se, URL, data=data)) for URL, data in zip(URLS, payload)]
        else:
            raise ValueError(f"invalid {method=}")
        tasks = (asyncio.ensure_future(async_worker(task)) for task in tasks)
        return list(await asyncio.gather(*tasks))

    async def get_img(self, *URLS, method: Literal["GET", "POST"] = "GET", payload=None) -> list[bytes]:
        payload = payload or [None] * len(URLS)
        if len(URLS) == 1: URLS = [URLS[0]] * len(payload)
        assert len(URLS) == len(payload)
        if method == "GET":
            tasks = [asyncio.ensure_future(self.img(self.get(self.Se, URL))) for URL in URLS]
        elif method == "POST":
            tasks = [asyncio.ensure_future(self.img(self.post(self.Se, URL, data=data))) for URL, data in
                     zip(URLS, payload)]
        else:
            raise ValueError(f"invalid {method=}")
        return list(await asyncio.gather(*tasks))


class AsyncCache:
    cache_location = Path(__file__).parent.parent.parent / "__async_cache__"

    @classmethod
    def load_cache(cls, name) -> dict[str, str]:
        try:
            with open(f'{cls.cache_location}/{name}.cache', 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    def __init__(self, name, ignore: tuple = None):
        self._name = name
        self._ignore = ignore or ()
        self._cache = self.load_cache(name)

    def __call__(self, func):
        func.save_cache = self.save_cache

        @wraps(func)
        async def wrapper(_=None, **kwargs):
            _hash = self.hash(kwargs)
            if _ is not None: kwargs["self"] = _
            try:
                r = self._cache[_hash]
                return r
            except KeyError:
                result = await func(**kwargs)
                self._cache[_hash] = result
                return result

        return wrapper

    def hash(self, kwargs):
        hasher = hashlib.md5()
        for key in sorted(kwargs):
            if key in self._ignore: continue
            hasher.update(str(key).encode())
            hasher.update(str(kwargs[key]).encode())
        return hasher.hexdigest()

    def save_cache(self):
        if not os.path.exists(self.cache_location): os.mkdir(self.cache_location)
        with open(f'{self.cache_location}/{self._name}.cache', 'wb') as file:
            pickle.dump(self._cache, file)


def gen_usn(year: int, dept: str, i: int, temp=False) -> str:
    assert year > 2000
    return (f"1MS{year - 2000}{dept}{i:03}" + ("-T" if temp else "")).upper()


def gen_dob(day: int, month: int, year: int) -> str:
    assert 1 <= day <= 31
    assert 1 <= month <= 12
    return f"{year}-{month:02}-{day:02}"


def validate_usn(usn):
    return re.search(r"^1MS\d{2}[A-Z]{2}\d{3}(-T)?$", usn) is not None


def validate_dob(dob):
    return re.search(r"^\d{4}-\d{2}-\d{2}$", dob) is not None
