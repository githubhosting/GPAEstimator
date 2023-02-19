import datetime

import pandas as pd
import streamlit as st

from src.exam import micro
from src.scraper import get_cache, validate_usn
from src.sis import micro, CACHE_NAME

st.set_page_config(page_title="GPA Calculator", page_icon="📊", layout="centered")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Check CIE Marks", "Grades-Score", "Credit-CGPA", "Crack DOB", "How it works?"])


@st.cache_data
def m1m2(year, dept, i, temp, dob):
	m1, m2 = micro(year, dept, i, temp, dob=dob, lite=True)
	return m1, m2


def tab_1():
	year = dept = i = temp = dob = None
	marks = []
	subject_code = []
	subject_name = []
	attendance = []

	st.title("Check your CIE Marks")
	usn = st.text_input("Enter your USN").upper()

	if validate_usn(usn):
		year = int(usn[3:5]) + 2000
		dept = usn[5:7]
		i = int(usn[7:10])
		if len(usn) == 10:
			temp = False
		else:
			temp = True
		dob = st.date_input("Enter DOB", datetime.date(year - 18, 1, 1))
		get = st.button("Get Marks")
		if get:
			m1, m2 = m1m2(year, dept, i, temp, dob=dob)
			if not m1:
				st.warning("Invalid USN or DOB", icon="🚨")
			else:
				st.subheader(f"Hey {m1['name']}!")
				st.write(f"Here is your CIE Marks for Semester {m1['sem']}")
				for sub_code, sub in m2.items():
					marks.append(sub["tot"][0])
					subject_code.append(sub_code)
					subject_name.append(sub["sub"])
					attendance.append(sub["attd"])
				table = pd.DataFrame({"Subject": subject_name, "Marks": marks},
				                     index=[j for j in range(1, len(marks) + 1)], )
				st.table(table)
				short_attenddence = []
				st.write("Here is your attendance for each subject")
				for j in attendance:
					if j < 75:
						short_attenddence.append("🚨")
					else:
						short_attenddence.append("✅")
				table = pd.DataFrame({"Subject": subject_name,
				                      "Percentage": attendance,
				                      "Attendance": short_attenddence},
				                     index=[k for k in range(1, len(marks) + 1)])
				st.table(table)
	elif usn:
		st.error('Invalid USN', icon="🚨")

	return year, dept, i, temp, dob


def tab_2(year, dept, i, temp, dob):
	marks = []
	subject_code = []
	subject_name = []
	creds = []
	st.title("Each Subject Scoring Criteria")
	st.write("You have to score the following marks in SEE to get the respective grade")
	if dob:
		m1, m2 = m1m2(year, dept, i, temp, dob=dob)
		if not m1:
			st.error("Invalid USN or DOB", icon="🚨")
		else:
			creds = [sub["cred"] for sub in m2.values()]

			for sub_code, sub in m2.items():
				marks.append(sub["tot"][0])
				subject_code.append(sub_code)
				subject_name.append(sub["sub"])
			to_score_o = []
			to_score_ap = []
			to_score_a = []
			to_score_bp = []
			to_score_b = []

			for i in range(len(marks)):
				const = (90 - marks[i]) * (2 if creds[i] > 2 else 1)
				to_score_o.append(const)
				to_score_ap.append(const - (20 if creds[i] > 2 else 10))
				to_score_a.append(const - (40 if creds[i] > 2 else 20))
				to_score_bp.append(const - (60 if creds[i] > 2 else 30))
				to_score_b.append(const - (80 if creds[i] > 2 else 40))
				if const > (100 if creds[i] > 2 else 50): to_score_o[-1] = "-"
				if const > (120 if creds[i] > 2 else 60): to_score_ap[-1] = "-"
				if const > (140 if creds[i] > 2 else 70): to_score_a[-1] = "-"
				if const > (160 if creds[i] > 2 else 80): to_score_bp[-1] = "-"
				if const > (180 if creds[i] > 2 else 90): to_score_b[-1] = "-"

			table = pd.DataFrame({"Subject": subject_name, "Marks": marks, "O": to_score_o, "A+": to_score_ap,
			                      "A": to_score_a, "B+": to_score_bp, "B": to_score_b},
			                     index=[i for i in range(1, len(marks) + 1)])
			st.table(table)
	else:
		st.warning("Enter your USN and DOB first", icon="⚠️")
	return subject_name, creds


def tab_3(subject_name, dob, credits_each):
	if dob and credits_each:
		st.subheader("Enter your Predicted Grade for each subjects")
		grade_in_each = []
		for j in range(len(subject_name)):
			grade_in_each.append(st.radio(subject_name[j], ["O", "A+", "A", "B+", "B", "C"], horizontal=True))
		grade_point = [
			10 if k == "O" else 9 if k == "A+" else 8 if k == "A" else 7 if k == "B+" else 6 if k == "B" else 0
			for k in grade_in_each
		]
		weighted_gp = [i * j for i, j in zip(grade_point, credits_each)]
		total_credits_final = sum(weighted_gp)
		cgpa = total_credits_final / sum(credits_each)
		st.write("Based on the above grades, this will be your final credits and CGPA")
		table = pd.DataFrame(
			{"Subject": subject_name, "Grade": grade_in_each, "Credits": credits_each,
			 "Grade Points": [f"{w}/{c * 10}" for w, c in zip(weighted_gp, credits_each)]})
		st.table(table)
		cgpa = round(cgpa, 3)
		st.subheader(f"Your CGPA is:\t " f"{cgpa}")
	else:
		st.error("Enter USN and DOB first", icon="🚨")


def main():
	dobs = get_cache(CACHE_NAME)
	with tab1:
		year_, dept_, i_, temp_, dob_ = tab_1()
	with tab2:
		subject_name_, creds_ = tab_2(year_, dept_, i_, temp_, dob_)
	with tab3:
		tab_3(subject_name_, dob_, creds_)
	with tab4:
		st.write("You Dont Have access to this page")
	# st.title("Crack DOB")
	# usn = st.text_input("Enter USN number").upper()
	# if validate_usn(usn):
	# 	year = int(usn[3:5]) + 2000
	# 	dept = usn[5:7]
	# 	i = int(usn[7:10])
	# 	if len(usn) == 10:
	# 		temp = False
	# 	else:
	# 		temp = True
	# 	get = st.button("Get DOB")
	# 	if get:
	# 		m1, m2 = micro(year, dept, i, temp, lite=True)
	# 		if not m1:
	# 			st.error("Invalid USN", icon="🚨")
	# 		else:
	# 			st.success(f"{m1, m2} ", icon="🎉")
	# elif usn:
	# 	st.error('Invalid USN', icon="🚨")
	with tab5:
		st.title("About")
		st.write("This is a simple web app to calculate your GPA based on the marks you scored")


if __name__ == '__main__':
	main()
