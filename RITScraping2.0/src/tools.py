def sub_lists(marks: dict):
	assert isinstance(marks, dict)
	try:
		sub_codes = list(marks.keys())
		sub_names = [m["sub"] for m in marks.values()]
		sub_attds = [m["attd"] for m in marks.values()]
		sub_marks = [m["tot"][0] for m in marks.values()]
		sub_max_marks = [m["tot"][1] for m in marks.values()]
		sub_avg_cie = [sum(mm[2] for mm in m["cies"]) / len(m["cies"]) if m["cies"] else 0 for m in marks.values()]
		sub_avg_ces = [sum(mm[2] for mm in m["ces"]) / len(m["ces"]) if m["ces"] else 0 for m in marks.values()]
	except KeyError:
		print("Invalid Marks dict")
		return
	return sub_codes, sub_names, sub_attds, sub_marks, sub_max_marks, sub_avg_cie, sub_avg_ces


def grade_estimates(sub_marks, sub_names, sub_max_marks, max_score=100, **min_scores: int):
	for mark, name, max_mark in zip(sub_marks, sub_names, sub_max_marks):
		estimate = {}
		for grade, min_mark in min_scores.items():
			to_score = to_score if 0 <= (to_score := min_mark - mark) <= max_score / 2 else ""
			estimate[grade] = int(to_score) if to_score else "-"
		yield estimate
