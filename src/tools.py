def sub_lists(marks: dict):
	assert isinstance(marks, dict)
	try:
		sub_codes = list(marks.keys())
		sub_names = [m["sub"] for m in marks.values()]
		sub_attds = [m["attd"] for m in marks.values()]
		sub_marks = [m["tot"][0] for m in marks.values()]
		sub_max_marks = [m["tot"][1] for m in marks.values()]
	except KeyError:
		print("Invalid Marks dict")
		return
	return sub_codes, sub_names, sub_attds, sub_marks, sub_max_marks


def grade_estimates(sub_marks, sub_names, max_marks=100, **kwargs: int):
	"""
	kwargs: grade: min_marks
	"""
	grade_lists = {}
	for grade, min_mark in kwargs.items():
		grade_lists[grade] = lis = []
		for mark, name in zip(sub_marks, sub_names):
			to_score = to_score if 0 <= (to_score := min_mark - mark) <= max_marks / 2 else ""
			lis.append(to_score * 2 if " lab" not in name.lower() else to_score)
	return grade_lists
