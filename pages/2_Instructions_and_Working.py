import pandas as pd
import streamlit as st


def local_html(file_name):
	with open(file_name) as f:
		st.markdown(f'{f.read()}', unsafe_allow_html=True)


local_html("index.html")

th_props = [
	('text-align', 'left'),
	('font-weight', 'bold'),
]

td_props = [
	('text-align', 'center'),
]

headers_props = [
	('text-align', 'center'),
]
table_body = [
	('border', '1.5px solid white'),
	('border-radius', '20px'),
]
styles = [
	dict(selector="th", props=th_props),
	dict(selector="td", props=td_props),
]
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
st.markdown(hide_table_row_index, unsafe_allow_html=True)


def local_css(file_name):
	with open(file_name) as f:
		st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


local_css("styles.css")

st.write("# Instruction and Working")
tab1, tab2 = st.tabs(["Instructions", "How its Calculated"])

with tab1:
	st.write("1. Enter your USN and DOB")
	st.write("2. Your CIE and Attendance will be displayed")
	st.write("3. Switch to the Grades-Score tab")
	st.write("4. Note down the expected grades for each subject")
	st.write("5. Switch to the Credit-CGPA tab and select the grades")
	st.write("6. Your SGPA will be displayed")
	st.markdown(
		"""
		Check you CIE Marks 
		<a href="/" >***Click Here*** </a>
		""",
		unsafe_allow_html=True
	)

with tab2:
	st.write("The grading system is as follows:")
	creds = [10, 9, 8, 7, 6, 5, 4, 0]
	df = pd.DataFrame({
		"Marks Range": ["90 - 100", "80 - 89", "70 - 79", "60 - 69", "55 - 59", "50 - 54", "40 - 49", "0 - 39"],
		"Grade": ["O", "A+", "A", "B+", "B", "C", "P", "F"],
		"GPA": creds},
		index=None)
	st.write(df.style.set_table_styles(styles).to_html(), unsafe_allow_html=True)
	st.write("")
	st.subheader("Grade Point Average - GPA")
	st.write(
		"Grade Point Average (CGPA), both of which are important performance indices of the student. SGPA is equal to the sum of all the total points earned by the student in a given semester divided by the number of credits registered by the student in that semester. CGPA gives the sum of all the total points earned in all the previous semesters and the current semester divided by the number of credits registered in all these semesters.")

	st.markdown(
		"""
		#### Semester Grade point average - SGPA is calculated as follows: \n
		
		$$ \\frac{\sum (Course \\ Credits \\times Grade \\ Points) \\ all \\ Courses}{\sum (Course \\ Credits)\\ all \\ Courses} $$ \n
		
		""")
	# st.latex(r'''
	# 	SGPA = \frac{\sum Course Credits \times Grade Points}{\sum Total Course Credits}
	# 	''')
	st.write("#### Cumulative Grade point average - CGPA:", unsafe_allow_html=True)
	# st.latex(r'''
	# 	CGPA = \frac{\sum Course Credits \times Grade Points}{\sum Total Credits}
	# 	''')
	st.latex(r'''
		CGPA = \frac{Sum \ of \ all \ SGPA}{Total \ Credits \ earned}
		''')
	st.write("Note in CGPA : for all courses, excluding those with “F” and transitional grades until that semester")
