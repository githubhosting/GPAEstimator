import asyncio
import csv
import os

from .scraper import Scraper, gen_usn, validate_usn


def gen_payload(usn: str) -> dict[str, str]:
    return {
        "usn": usn.upper(),
        "osolCatchaTxt": "",
        "osolCatchaTxtInst": "0",
        "option": "com_examresult",
        "task": "getResult"
    }


# todo: improve this
def body_validator(soup):
    try:
        _ = soup.find_all("h3")[0].text
        return True
    except IndexError:
        return False


class ExamScraper(Scraper):
    DEPTS = ["AD", "AI", "AT", "BT", "CH", "CI", "CS", "CV", "CY", "EC", "EE", "ET", "IS", "ME"]
    BASE_URL = "https://exam.msrit.edu/"

    def __init__(self, even=False):
        self.URL = self.BASE_URL
        if even: self.URL += "eresultseven/"
        super(ExamScraper, self).__init__()

    async def get_stats(self, *USNS) -> list[dict[str, str]]:
        assert all(validate_usn(usn) for usn in USNS)
        soups = await self.get_soups(self.URL, method="POST", payload=[gen_payload(usn) for usn in USNS])
        return [{
            "usn": USNS[soups.index(soup)],
            "name": soup.find_all("h3")[0].text,
            "sgpa": soup.find_all("p")[3].text,
            "sem": soup.find("p").text.split(",")[-1].strip(),
            "photo": self.BASE_URL + soup.find_all("img")[1]['src'],
        } for soup in soups if body_validator(soup)]

    async def stats_dept(self, year: int, dept: str, temp: bool = False, start: int = 1, stop: int = 150):
        assert 1 <= start <= stop
        assert dept in self.DEPTS
        USNS = (gen_usn(year, dept, i, temp) for i in range(start, stop))
        return await self.get_stats(*USNS)


def macro(year: int, dept: str, temp=False, even=False, file=None, dry: bool = False):
    async def __macro():
        async with ExamScraper(even) as EXAM:
            return await EXAM.stats_dept(year, dept, temp)

    stats = asyncio.run(__macro())

    if file is None and not dry:
        folder = f"exam/{dept}/{year}"
        if not os.path.exists(folder): os.makedirs(folder)
        file = f"{folder}/{stats[0]['sem'].replace(' ', '_')}.csv"

    if file and not dry:
        with open(file, "w+") as f:
            writer = csv.DictWriter(f, stats[0].keys())
            writer.writeheader()
            writer.writerows(stats)

    for stat in stats:
        print(stat)

    return stats


def micro(usn: str, even=False):
    async def __micro():
        async with ExamScraper(even) as EXAM:
            return (await EXAM.get_stats(usn))[0]

    return asyncio.run(__micro())
