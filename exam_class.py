import os
import tempfile
from urllib.parse import urlparse

from scraper import Scraper, gen_usn, roll_range


class ExamScraper(Scraper):
    def __init__(self, url="https://exam.msrit.edu/"):
        self.URL = url + ("/" if url[-1] != "/" else "")
        super(ExamScraper, self).__init__()

    def get_post_body(self, payload):
        soup = self.get_soap(self.URL, "POST", payload)
        body = soup.body
        try:
            _ = body.find_all("h3")[0].text
            return body
        except IndexError:
            return

    def get_stats(self, payload) -> dict[str, str]:
        body = self.get_post_body(payload)
        if body is None: return {}
        url = urlparse(self.URL)
        return {
            "usn": payload["usn"],
            "name": body.find_all("h3")[0].text,
            "sgpa": body.find_all("p")[3].text,
            "photo": f"{url[0]}://{url[1]}" + body.find_all("img")[1]['src'],
        }

    def get_dept(self, head: str, year: str, dept: str, _range=None, tolerate: int = 5):
        if _range is None: _range = roll_range()
        payload = gen_payload()
        tol = tolerate
        for roll in _range:
            if tol <= 0: return
            payload["usn"] = gen_usn(year, dept, roll, head)
            stats = self.get_stats(payload)
            if not stats:
                tol -= 1
                continue
            tol = tolerate
            yield stats


def gen_payload() -> dict[str, str]:
    return {
        "usn": "",
        "osolCatchaTxt": "",
        "osolCatchaTxtInst": "0",
        "option": "com_examresult",
        "task": "getResult"
    }


def macro(head: str, year: str, dept: str, file=None, dry: bool = False):
    if not os.path.exists(f"results/{dept}") and not dry: os.mkdir(f"results/{dept}")
    file = f"results/{dept}/results_{dept}_{year}.csv" if file is None else file
    with ExamScraper("https://exam.msrit.edu/eresultseven/") as EXAM, \
            tempfile.TemporaryFile("w+") if dry else open(file, "w+") as f:
        write = \
            f"{'usn':{len(head + year + dept) + 3 + 5}}," \
            f"{'name':64}," \
            f"{'sgpa':5}," \
            f"photo," \
            f""
        if not dry: f.write(write + "\n")
        print(write)
        for stat in EXAM.get_dept(head, year, dept):
            write = \
                f"{stat['usn']:{len(head + year + dept) + 3 + 5}}," \
                f"{stat['name']:64}," \
                f"{stat['sgpa']:5}," \
                f"{stat['photo']}," \
                f""
            if not dry:
                f.write(write + "\n")
            print(write)


def micro(head: str, year: str, dept: str, start, stop=None):
    with ExamScraper("https://exam.msrit.edu/eresultseven/") as EXAM:
        write = \
            f"{'usn':{len(head + year + dept) + 3 + 5}}," \
            f"{'name':64}," \
            f"{'sgpa':5}," \
            f"photo," \
            f""
        print(write)
        for stat in EXAM.get_dept(head, year, dept, roll_range(start, stop)):
            write = \
                f"{stat['usn']:{len(head + year + dept) + 3 + 5}}," \
                f"{stat['name']:64}," \
                f"{stat['sgpa']:5}," \
                f"{stat['photo']}," \
                f""
            print(write)


if __name__ == '__main__':
    HEAD = "1MS"
    YEAR = "21"
    DEPT = "IS"
    macro(HEAD, YEAR, DEPT, dry=True)
    # micro(HEAD, YEAR, DEPT, start=1, stop=None)
