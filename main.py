from exam import ExamScraper, gen_payload as exam_pl
from sis import stats_i
from scraper import gen_usn, roll_range, set_cache


if __name__ == '__main__':
	YEAR = "21"
	DEPT = "IS"

	"""
	if lite is true, minimal information is given and is faster
	"""

	# === single usn example
	m1, m2 = stats_i(YEAR, DEPT, 1, lite=True)
	print(m1, m2)
