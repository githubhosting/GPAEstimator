from exam import micro
from sis import micro


if __name__ == '__main__':
	YEAR = "22"
	DEPT = "IS"
	TEMP = True

	"""
	if lite is true, minimal information is given and is faster
	"""

	# === single usn example
	m1, m2 = micro(YEAR, DEPT, 1, True, lite=True)
	print(m1, m2)
