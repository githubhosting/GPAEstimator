from exam import micro
from sis import micro


if __name__ == '__main__':
	YEAR = "21"
	DEPT = "IS"

	"""
	if lite is true, minimal information is given and is faster
	"""

	# === single usn example
	m1, m2 = micro(YEAR, DEPT, 1, lite=True)
	print(m1, m2)
