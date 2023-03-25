import asyncio
import json
import os
import re
from typing import Union

from .scraper import Scraper, AsyncCache, gen_usn, validate_usn, validate_dob

try:
    from private.dob_cracker import DobCracker
except ImportError:
    class DobCracker:
        pass


class SisScraper(DobCracker, Scraper):
    DEPTS = ["AD", "AI", "AT", "BT", "CH", "CI", "CS", "CV", "CY", "EC", "EE", "ET", "IS", "ME"]
    encoding = "Windows-1252"
    BASE_URL = "https://parents.msrit.edu/"
    MARKS_CURL = "index.php?option=com_studentdashboard&controller=studentdashboard&task=dashboard"
    CREDS_CURL = "index.php?option=com_coursefeedback&controller=feedbackentry&task=feedback"
    SGPAS_CURL = "index.php?option=com_history&task=getResult"

    @staticmethod
    def gen_payload(usn: str, dob: str) -> dict[str, str]:
        return {
            "username": usn.upper(),
            "dd": "",
            "mm": "",
            "yyyy": "",
            "passwd": dob,
            "remember": "",
            "option": "com_user",
            "task": "login",
            "return": "",
            "ea07d18ec2752bcca07e20a852d96337": "1"
        }

    @staticmethod
    def body_validator(soup):
        return soup.find(id="username") is None

    async def get_dob(self, usn: str) -> str:
        if hasattr(self, "brute_year"):
            return await self.brute_dob(usn)

    def __init__(self, odd=False):
        super(SisScraper, self).__init__()
        self.URL = self.BASE_URL + ("parentsodd/" if odd else "")
        self.odd = odd

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.brute_year.save_cache()
        self.__cred_worker.save_cache()
        return super().__aexit__(exc_type, exc_val, exc_tb)

    async def __stats_worker(self, usn: str, dob: str):
        async with SisScraper(self.odd) as self:
            soup, = await self.get_soups(self.URL, method="POST", payload=[self.gen_payload(usn, dob)])
            stats = {}
            if self.body_validator(soup):
                course, sem, sec = soup.find_all("p")[6].text.split(",")
                creds = await self.get_credits()
                sgpas = await self.get_sgpas()
                marks = await self.get_marks()
                stats["name"] = soup.find("h3").text.strip()
                stats["usn"] = usn
                stats["dob"] = dob
                stats["course"] = course.strip()
                stats["sem"] = sem.strip()
                stats["sec"] = sec.strip()
                stats["creds"] = creds
                stats["sgpas"] = sgpas
                stats["marks"] = marks
            return stats

    # todo: specify which apis to use
    async def login_and_stats(self, USNS, DOBS) -> list[dict[str, str]]:
        assert len(USNS) == len(DOBS)
        assert all(validate_usn(usn) for usn in USNS)
        assert all(validate_dob(dob) for dob in DOBS if dob is not None)
        tasks = [asyncio.ensure_future(self.__stats_worker(usn, dob)) for usn, dob in zip(USNS, DOBS)]
        return list(await asyncio.gather(*tasks))

    async def __mark_worker(self, curl):
        soup, = await self.get_soups(self.URL + curl)
        if not self.body_validator(soup): raise ValueError("Not logged in")
        table = soup.find("table")
        sub, code = table.find("caption").text.strip().replace(")", "").split("( ")
        mark = [t.text.replace("Abscent", "0/0").split('/') if t.text != "-" else None for t in table.find_all("td")]
        script = soup.find_all("script")[-1].text
        script_data = script[script.find("["):script.find("]") + 1].replace("\r", '').replace("\n", '')
        pattern = r'"(\w+)":\s*("[^"]+"|[\w\s]+)(?:,|$)'
        data = [dict(re.findall(pattern, raw)) for raw in re.findall(r"\{.*?}", script_data)]
        if len(mark[7]) == 1: mark[7] = ['0', '0']
        return code, {
            "sub": sub,
            "attd": int(mark.pop(-2)[0].removesuffix("%")),
            "cies": [(int(m["optainmarks"]), mm, int(m["col1"])) for m in data[0:4] if (mm := int(m["maxmarks"]))],
            "ces": [(int(m["optainmarks"]), mm, int(m["col1"])) for m in data[4:] if (mm := int(m["maxmarks"]))],
            "tot": tuple(map(int, mark[7])),
        }

    @AsyncCache("siscacheri956kh45.creds", ignore=("curl",))
    async def __cred_worker(self, *, curl, code) -> Union[tuple[str, int], None]:
        soup, = await self.get_soups(self.URL + curl)
        if not self.body_validator(soup): raise ValueError("Not logged in")
        sub_code, cred = soup.find_all("table")[2:4]
        if sub_code.find_all("div")[1].text != code: raise ValueError("Invalid code and curl")
        return code, int(float(cred.find("div").text))

    async def get_credits(self) -> dict[str, int]:
        soup, = await self.get_soups(self.URL + self.CREDS_CURL)
        if not self.body_validator(soup): raise ValueError("Not logged in")
        head = soup.find("div", {"id": "sims-container"})
        subs = head.find_all("a")
        tasks = []
        for sub in subs:
            k = sub.parent.parent.parent.find("tr").text.split()[0]
            tasks.append(asyncio.ensure_future(self.__cred_worker(curl=sub.get("href"), code=k)))
        return dict(await asyncio.gather(*tasks))

    async def get_sgpas(self):
        soup, = await self.get_soups(self.URL + self.SGPAS_CURL)
        if not self.body_validator(soup): raise ValueError("Not logged in")
        return [float(s.text.replace("SGPA:", "")) for s in soup.find_all("span", {"class": "cn-bgcolor1"})]

    # fixme: website changed
    # def get_metas(self, soups):
    #     metas = []
    #     for soup in soups:
    #         if body_validator(soup):
    #             td = soup.find_all("td")
    #             trs = soup.find_all("tbody")[1].find_all("tr")
    #             i = soups.index(soup)
    #             metas.append({
    #                 "name": td[0].text.split(":")[1].strip(),
    #                 "usn": USNS[i],
    #                 "dob": DOBS[i],
    #                 "email": td[1].text.split(":")[1].strip(),
    #                 "sem": td[2].text.split(":")[1].strip(),
    #                 "quota": td[4].text.split(":")[1].strip(),
    #                 "mobile": td[5].text.split(":")[1].strip(),
    #                 "course": td[6].text.split(":")[1].strip(),
    #                 "category": td[8].text.split(":")[1].strip(),
    #                 "class": soup.find_all("p")[6].text.strip(),
    #                 "batch": td[9].text.split(":")[1].strip(),
    #                 "paid": [tr.find_all("td")[3].text.strip() for tr in trs]
    #             })

    async def get_marks(self) -> dict[str, Union[dict, dict]]:
        soup, = await self.get_soups(self.URL + self.MARKS_CURL)
        if not self.body_validator(soup): raise ValueError("Not logged in")
        subs = soup.find("tbody").find_all("tr")
        tasks = [asyncio.ensure_future(self.__mark_worker(s.find_all("a")[-1].get("href"))) for s in subs]
        return dict(await asyncio.gather(*tasks))

    async def stats_dept(
            self,
            year: int,
            dept: str,
            roll_set: set[int],
            temp: bool = False,
            dobs: dict[int, str] = None,
    ):
        if dobs is None:
            input("Warning: DOBs not provided. "
                  "This will take a lot of time and load on the server. Press Enter to continue: ")
        assert dept in self.DEPTS
        assert not dobs or len(dobs) == len(roll_set)
        USNS = [gen_usn(year, dept, i, temp) for i in roll_set]
        DOBS = [dobs[i] if dobs and dobs[i] else await self.get_dob(gen_usn(year, dept, i, temp)) for i in roll_set]
        stats = []
        for split in range(0, len(USNS), 20):
            stats += await self.login_and_stats(USNS[split:split + 20], DOBS[split:split + 20])
        return stats


def macro(year: int,
          dept: str,
          roll_set,
          temp=False,
          odd=False,
          dobs=None,
          file=None,
          dry: bool = False):
    async def __macro():
        async with SisScraper(odd=odd) as SIS:
            return await SIS.stats_dept(year, dept, roll_set, temp, dobs)

    stats = asyncio.run(__macro())

    if file is None and not dry:
        folder = f"sis/{dept}/{year}"
        if not os.path.exists(folder): os.makedirs(folder)
        file = f"{folder}/{stats[0]['sem'].replace(' ', '_')}.json"

    if file and not dry: json.dump(stats, open(file, "w"))

    for stat in stats:
        for key, val in stat.items():
            print(f"{key}: {val}")
        print("---")

    return stats


def micro(usn: str, dob: str = None, odd=False):
    async def main():
        async with SisScraper(odd=odd) as SIS:
            if not dob: _dob = await SIS.get_dob(usn)
            return (await SIS.login_and_stats([usn], [dob or _dob]))[0]

    return asyncio.run(main())
