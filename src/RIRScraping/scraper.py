import base64
import hashlib
import pickle
import re
from abc import ABCMeta
from functools import wraps
from typing import Literal, Union

from bs4 import BeautifulSoup
from requests import Session


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

	def get_soup(self, URL, type_: Literal["GET", "POST"] = "GET", payload_=None) -> BeautifulSoup:
		if type_ == "GET":
			response = self.Se.get(URL, headers=self.HEADERS)
		elif type_ == "POST":
			response = self.Se.post(URL, data=payload_, headers=self.HEADERS)
		else:
			raise ValueError(f"invalid {type_=}")
		return BeautifulSoup(response.content, 'html.parser')

	def get_img(self, URL) -> bytes:
		return base64.encodebytes(self.Se.get(URL).content)


def cached(cache, ignore: tuple = None):
	if ignore is None: ignore = ()

	def casher(func):
		func.cache = cache

		@wraps(func)
		def wrapper(self, **kwargs):
			_hash = hash_it(kwargs, ignore=ignore)
			try:
				r = func.cache[_hash]
				return r
			except KeyError:
				if (result := func(self, **kwargs)) is not None: func.cache[_hash] = result
				return result

		return wrapper

	return casher


def hash_it(kwargs, ignore):
	hasher = hashlib.md5()
	for key in sorted(kwargs):
		if key in ignore: continue
		hasher.update(str(key).encode())
		hasher.update(str(kwargs[key]).encode())
	return hasher.hexdigest()


def get_cache(name) -> dict[str, str]:
	try:
		with open(f'data/{name}.cache', 'rb') as file:
			return pickle.load(file)
	except FileNotFoundError:
		return {}


def set_cache(name, func):
	assert hasattr(func, "cache")
	with open(f'data/{name}.cache', 'wb') as file:
		pickle.dump(func.cache, file)


def gen_usn(year: int, dept: str, i: int, temp=False) -> str:
	assert year > 2000
	return (f"1MS{year - 2000}{dept}{i:03}" + ("-T" if temp else "")).upper()


def validate_usn(usn):
	return re.search(r"^1MS\d{2}[A-Z]{2}\d{3}(-T)?$", usn) is not None


def roll_range(start=1, stop=None):
	if stop is None: stop = float('inf')
	assert isinstance(start, int) and start > 0, \
		"start must be int > 0"
	i = start
	while i < stop:
		yield i
		i += 1
