import datetime
import random
import time

import pandas as pd
import streamlit as st

from common import *
from src.RIRScraping.exam import micro as exam_micro
from src.RIRScraping.scraper import validate_usn
from src.RIRScraping.sis import micro, SisScraper
from src.tools import sub_lists, grade_estimates

st.set_page_config(page_title="Calculla - GPA Calculator", page_icon="📊", layout="centered")

local_css("styles.css")
local_html("index.html")

st.title("Calculla - GPA Calculator")
st.write(
	"""
		<p>
			Follow the instructions and see the how its calculated
			<a class="name" target="_self" href="/Instructions_and_Working">Click Here</a>
		</p>
	""", unsafe_allow_html=True
)
st.write(f'Total Searches: {st.secrets.stats.stat[0]} | Unique Searches: {st.secrets.stats.stat[1]}')

grade_to_gp = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}
tab1, tab2, tab3, tab4 = st.tabs(["Check CIE Marks", "Grades - Score", "Credit - GPA", "Simple - Calculator"])
crack_forbid_msg = """
**💨 Whoa, hold your horses! 🐴 What do you think you're doing? 🧐 Do you really think you can crack the creators' password with THEIR OWN fancy tool? Let's face it, if the creators' password was a piñata, you wouldn't even be able to hit it with a baseball bat 😎. But don't worry, we won't judge you for trying. 🫡"**
"""


@st.cache_data(ttl=60 * 60 * 12)
def get_meta_and_marks(year, dept, i, temp, dob):
	meta, marks, sgpas = micro(year, dept, i, temp, dob=dob, lite=True)
	exam_stuff = exam_micro(year, dept, i, temp)
	return meta, exam_stuff, marks, sgpas


@st.cache_data(ttl=60 * 60 * 12)
def brutes(usn):
	with SisScraper() as SIS: dat = SIS.get_dob(usn)
	return map(int, dat.split("-"))


def log(usn, name, dob, easter, crack):
	with open("data/logs.log" if st.secrets["cloud"] else "logs.txt", "a") as file:
		file.write(
			write :=
			f"[LOG] | {datetime.datetime.now()} | "
			f"{usn} | {dob} | {name} | {f'token-{easter}' if crack else 'dob'}\n"
		)
		print(write)
		usns = st.secrets.stats.usns
		stat = st.secrets.stats.stat
		if "prev_usn" not in st.session_state: st.session_state.prev_usn = ""
		if x := (a := f"{usn} {dob} {name}") not in usns: usns.append(a)
		stat[0] = stat[0] + int(usn != st.session_state.prev_usn)
		stat[1] += int(x)
		stat[2] += int(name == 'CREATOR' and usn != st.session_state.prev_usn)


def deduct(easter):
	eggs_name = st.secrets.easters["easter_eggs"]
	eggs_span = st.secrets.easters["easter_eggs_counter"]
	eggs_span[eggs_name.index(easter)] -= 1


def valid_usn(usn, crack, easter, placeholder):
	year = int(usn[3:5]) + 2000
	dept = usn[5:7]
	i = int(usn[7:10])
	if len(usn) == 10:
		temp = False
	else:
		temp = True
	yy, mm, dd = year - 18, 1, 1
	if crack:
		if "easter_usn" not in st.session_state or st.session_state.easter_usn != usn:
			st.session_state.easter_usn = usn
			deduct(easter)
		if usn in ["1MS21IS017", "1MS21CI049"]:
			st.error(crack_forbid_msg)
			log(usn, "CREATOR", "huss-hh-hh", easter, crack)
			crack = False
			placeholder.empty()
			dob = st.date_input("Enter DOB", datetime.date(yy, mm, dd))
		else:
			t = time.time()
			yy, mm, dd = brutes(usn)
			t = time.time() - t
			dobf = datetime.date(yy, mm, dd)
			formatted_dob = dobf.strftime("%d %B %Y")
			if t < 5:
				time.sleep(et := random.random() * 3 + 2)
				t += et
			placeholder.empty()
			st.success(f"Cracked! in {t:.2f} seconds 🎉")
			st.info(f"DOB: **{formatted_dob}**")
			st.caption("Please use this tool with caution. We are not responsible for any misuse of this tool.")
			dob = datetime.date(yy, mm, dd)
	else:
		dob = st.date_input("Enter DOB", datetime.date(yy, mm, dd))

	if crack or st.button("Get Marks"):
		welcome = "Hey"
		symbol = '<img width="30" vertical-align:sub src="https://github.com/1999AZZAR/1999AZZAR/blob/main/resources/img/waving.gif?raw=true">'
		if crack:
			welcome = "Stalking"
			symbol = "🕵️"
		meta, exam_stuff, marks, sgpas = get_meta_and_marks(year, dept, i, temp, dob=dob)
		if not meta:
			st.warning("Invalid USN or DOB", icon="🚨")
		else:
			if usn in ["1MS21IS017", "1MS21CI049"]:
				log(usn, "CREATOR", "huss-hh-hh", easter, crack)
			else:
				log(usn, meta["name"], dob, easter, crack)
			st.session_state.prev_usn = usn

			st.markdown(
				f"""
				&nbsp;
				<h3 align="left">{welcome} {meta['name']} ! {symbol} <h3> 
				""", unsafe_allow_html=True
			)
			st.write(f"##### CIE Marks for Semester {meta['sem']}", unsafe_allow_html=True)
			sub_codes, sub_names, sub_attds, sub_marks, sub_creds = sub_lists(marks)

			table = pd.DataFrame(
				{"Subject": sub_names, "Marks": sub_marks},
				index=[j for j in range(1, len(sub_marks) + 1)]
			)
			st.markdown(table.style.set_table_styles(styles).to_html(), unsafe_allow_html=True)
			total_cie_marks = sum(sub_marks)
			st.write(
				f"""
				<h3 class="mt">Total CIE Marks: {total_cie_marks}/{len(sub_marks) * 50}<h3>
				""", unsafe_allow_html=True
			)

			st.markdown(""" ###### Attendance for this semester """)
			short_attendance = []
			for j in sub_attds:
				if j < 75: short_attendance.append({sub_names[sub_attds.index(j)]})
			attendance = [str(j) + "%" for j in sub_attds]
			table = pd.DataFrame(
				{"Subject": sub_names, "Percentage": attendance},
				index=[k for k in range(1, len(sub_marks) + 1)]
			)
			st.markdown(table.style.set_table_styles(styles_attd).to_html(), unsafe_allow_html=True)

			if short_attendance:
				st.write("")
				st.write("Following Subjects have shortage of attendance")
				for key in short_attendance:
					remove = str(key).replace("{'", "").replace("'}", "")
					st.warning(remove)

			for _ in range(5): st.write("\n")
			if exam_stuff:
				st.image(exam_stuff["photo"], exam_stuff["name"], use_column_width=True)
			for _ in range(2): st.write("\n")
			st.subheader("The following are the SGPA's")
			table = pd.DataFrame({
				"SEM": [f"SEM {s}" for s in range(1, len(sgpas) + 1)],
				"SGPA": [f"{s:.2f}" for s in sgpas]
			})
			st.markdown(table.style.set_table_styles(styles_gp).to_html(), unsafe_allow_html=True)

	return year, dept, i, temp, dob


def tab_1():
	year = dept = i = temp = dob = placeholder = None

	st.subheader("Check Internal Marks")
	usn = st.text_input("Enter Valid USN", placeholder="1ms21is000").strip().upper()
	easter = None
	if " " in usn:
		usn, easter = usn.split(maxsplit=1)
		easter = easter.lower()
	eggs_name = st.secrets["easters"]["easter_eggs"]
	eggs_span = st.secrets["easters"]["easter_eggs_counter"]
	crack = False
	if easter in eggs_name:
		if eggs_span[eggs_name.index(easter)]:
			placeholder = st.empty()
			with placeholder.container():
				st.success(f"Yay! token-{easter} has been applied! 🎊")
				st.info("Have a coffee while we try cracking the DOB")
			crack = True
		else:
			st.success(f"Yay! **{easter}** is correct ! 🎉")
			st.warning(
				f"But unfortunately, the creator has temporarily suspended this token that cracks the DOB. "
				f"How about trying another token?"
			)
			st.info("Please contact the **Admin** or try again later")
			st.markdown(
				"Contact the creators "
				"Shravan <a class='name' href='https://wa.me/919945332995?text=Hey whats the working token?'>here 🚀</a>"
				"or Amith <a class='name' href='https://wa.me/917019144708?text=Hey whats the working token?'>here 🚀</a>"
				" to get new token 😉",
				unsafe_allow_html=True
			)
	elif easter:
		if "rick" in easter and "roll" in easter:
			st.info("""
			I'll never give you up, I'll never let you down,
			I'll always be there, lurking around. 😁
			""")
			time.sleep(3)
			st.write(f'''
				<a href="https://pichost.pics/9FZ3M4">
					<button>
						Hurray! see next puzzle here
					</button>
				</a>
			''', unsafe_allow_html=True)
		else:
			st.error("Nah ah ha ha")
			st.warning("You didn't get the magic word!")

	if validate_usn(usn):
		year, dept, i, temp, dob = valid_usn(usn, crack, easter, placeholder)
	elif usn:
		st.error('Invalid USN', icon="🚨")

	return year, dept, i, temp, dob


def tab_2(year, dept, i, temp, dob):
	st.title("Each Subject Scoring Criteria")
	st.write("You will need to score the following minimum marks in SEE to get respective grades")
	st.caption(
		"Example: If you scored 46 in Internals then you need 88 in SEE to get O Grade. "
		"Coz half of SEE is added to internals. Now 46 + 44 = 90 which is minimum to get O grade"
	)
	sub_codes = sub_names = sub_attds = sub_marks = sub_creds = sgpas = None
	if dob:
		meta, exam_stuff, marks, sgpas = get_meta_and_marks(year, dept, i, temp, dob=dob)
		if not meta:
			st.error("Invalid USN or DOB", icon="🚨")
		else:
			sub_codes, sub_names, sub_attds, sub_marks, sub_creds = sub_lists(marks)
			grade_lists = grade_estimates(
				sub_marks, sub_names,
				**{"O": 90, "A+": 80, "A": 70, "B+": 60, "B": 55, "C": 50, "P": 40}
			)
			st.write("<hr/>", unsafe_allow_html=True)
			for i, sn in enumerate(sub_names):
				with st.container():
					table = pd.DataFrame({k: [v[i]] for k, v in grade_lists.items()})
					st.write(
						f" **{sn}** : {sub_marks[i]}", table.style.hide(axis="index").to_html(), "<hr/>",
						unsafe_allow_html=True
					)
			st.info("Note down the expected grades from above and enter them in the next tab")
	else:
		st.warning("Enter your USN and DOB first", icon="⚠️")
	return sub_names, sub_codes, sub_creds, sgpas


def tab_3(sub_names, dob, sub_creds, sgpas):
	if dob and sub_creds:
		st.subheader("Enter your Predicted Grade for each subjects")
		st.caption(
			"Mark the expected grades according to the previous tab and click on calculate to get your final credits and SGPA"
		)
		grade_in_each = []
		with st.form("Find GPA"):
			for name in sub_names:
				grade_in_each.append(st.radio(name, ["O", "A+", "A", "B+", "B", "C", "P", "F"], horizontal=True))
			if st.form_submit_button("Calculate"):
				grade_point = [grade_to_gp[g] for g in grade_in_each]
				weighted_gp = [i * j for i, j in zip(grade_point, sub_creds)]
				total_credits_final = sum(weighted_gp)
				st.write("")
				st.write("Based on the above grades, this will be your final credits and SGPA")
				table = pd.DataFrame({
					"Subject": sub_names, "Grade": grade_in_each, "Credits": sub_creds,
					"Grade Points": [f"{w}/{c * 10}" for w, c in zip(weighted_gp, sub_creds)]
				})
				st.write(table.style.set_table_styles(styles_gp).to_html(), unsafe_allow_html=True)
				sgpa = total_credits_final / sum(sub_creds)
				sgpa = round(sgpa, 3)
				st.write(f"<h2 class='mt'>Your SGPA is: {sgpa:.3f}</h2>", unsafe_allow_html=True)
				st.write(
					f"<h2 class='mt'>Your CGPA is: {((sgpa + sum(sgpas)) / (1 + len(sgpas))):.3f}</h2>",
					unsafe_allow_html=True
				)
	else:
		st.error("Enter USN and DOB first", icon="🚨")


def home():
	with tab1:
		year_, dept_, i_, temp_, dob_ = tab_1()
	with tab2:
		subject_name_, subject_code_, creds_, exam_stuff_ = tab_2(year_, dept_, i_, temp_, dob_)
	with tab3:
		tab_3(subject_name_, dob_, creds_, exam_stuff_)
	with tab4:
		st.subheader("How much is average CIE marks for 50?")
		avg = st.slider("Average CIE marks", 0, 50, step=1)
		to_score = (90 - avg) * 2
		st.write("Following is the minimum marks you need to score in SEE to get respective grades")
		grades = [to_score, to_score - 20, to_score - 40, to_score - 60, to_score - 80, to_score - 100]
		for i in range(len(grades)):
			if grades[i] > 100:
				grades[i] = " "
		grade_letter = ["O", "A+", "A", "B+", "B", "C"]
		table_1 = pd.DataFrame({"Grade": grade_letter, "Marks": grades})
		st.write(table_1.style.hide(axis="index").set_table_styles(styles).to_html(), unsafe_allow_html=True)
		st.write("")
		st.write("Here is how its calculated :")
		st.write(
			f"You scored {avg}, then you need {to_score} in SEE to get O Grade. "
			f"Because half of {to_score} which is {to_score / 2} is added to {avg} equals to {(to_score / 2) + avg} "
			f"and that is minimum to get O Grade"
		)


if __name__ == '__main__':
	home()
