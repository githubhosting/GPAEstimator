import os
import tempfile
from urllib.parse import urlparse

from scraper import Scraper, gen_usn, roll_range


class ExamScraper(Scraper):
	def __init__(self, url="https://exam.msrit.edu/"):
		self.URL = url + ("/" if url[-1] != "/" else "")
		super(ExamScraper, self).__init__()

	def get_post_body(self, payload):
		soup = self.get_soup(self.URL, "POST", payload)
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

	def stats_dept(self, year, dept, start=1, stop=None):
		tol = 4
		pl = gen_payload()
		for i in roll_range(start, stop):
			if tol <= 0: return
			pl["usn"] = gen_usn(year, dept, i)
			stat = self.get_stats(pl)
			if len(stat) == 0:
				tol -= 1
				continue
			tol = 4
			yield stat


def gen_payload() -> dict[str, str]:
	return {
		"usn": "",
		"osolCatchaTxt": "",
		"osolCatchaTxtInst": "0",
		"option": "com_examresult",
		"task": "getResult"
	}


def macro(year: str, dept: str, file=None, dry: bool = False):
	if not os.path.exists(f"results/{dept}") and not dry: os.makedirs(f"results/{dept}")
	file = f"results/{dept}/results_{dept}_{year}.csv" if file is None else file
	USN_LEN = 3 + len(year + dept) + 3 + 5
	with ExamScraper("https://exam.msrit.edu/eresultseven/") as EXAM, \
			(tempfile.TemporaryFile("w+") if dry else open(file, "w+")) as f:
		write = f"{'usn':{USN_LEN}}, {'name':64}, {'sgpa':5}, photo"
		if not dry: f.write(write + "\n")
		print(write)
		for stat in EXAM.stats_dept(year, dept):
			write = f"{stat['usn']:{USN_LEN}}, {stat['name']:64}, {stat['sgpa']:5}, {stat['photo']}"
			if not dry: f.write(write + "\n")
			print(write)


def micro(usn):
	with ExamScraper("https://exam.msrit.edu/eresultseven/") as Exam:
		pl = gen_payload()
		pl['usn'] = usn
		return Exam.get_stats(pl)


if __name__ == '__main__':
	HEAD = "1MS"
	YEAR = "21"
	DEPT = "IS"

	s = micro(gen_usn(YEAR, DEPT, 17))
	print(s)

# for DEPT in ["AD", "AI", "AT", "BT", "CH", "CI", "CS", "CV", "CY", "EC", "EE", "ET", "IS", "ME"]:
#     for YEAR in ["19", "20", "21"]:
#         macro(HEAD, YEAR, DEPT, dry=False)
