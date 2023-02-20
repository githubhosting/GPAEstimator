from src.RIRScraping.sis import micro

if __name__ == '__main__':
	# m1, m2 = micro(2021, "is", 17, lite=True)
	# sub_codes, sub_names, sub_attds, sub_marks, sub_creds = sub_lists(m2)
	# grade_lists = grade_estimates(sub_marks, sub_names, o=90, ap=80, a=70, bp=60, b=55, c=50, p=40, f=0)
	# print(sub_marks)
	# for grade_name, mark_req in grade_lists.items():
	# 	print(grade_name, ":", mark_req)

	if __name__ == '__main__':
		YEAR = 2021
		DEPT = "IS"
		TEMP = False
		LITE = True

		"""
		if lite is true, minimal information is given and is faster
		"""

		# super macro
		# todo

		# macro
		# todo

		# === single usn example
		meta_, marks_ = micro(YEAR, DEPT, 1, TEMP, lite=LITE)
