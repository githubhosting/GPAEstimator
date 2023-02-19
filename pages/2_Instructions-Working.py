import pandas as pd
import streamlit as st

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
	df = pd.DataFrame({"Grade": ["O", "A+", "A", "B+", "B", "C", "P", "F"],
	                   "Marks Range": ["90 - 100", "80-89", "70-79", "60-69", "50-59", "40-49", "30-39", "0-29"],
	                   "GPA": creds},
	                  index=None)
	st.markdown(df.style.set_table_styles(styles).to_html(), unsafe_allow_html=True)

	st.markdown(
		"""
		&nbsp;
		#### Semester Grade point average - SGPA is calculated as follows: \n
		""")
	st.latex(r'''
		SGPA = \frac{\sum Course Credits \times Grade Points}{\sum Total Course Credits}
		''')
	st.markdown(
		"""
		&nbsp;
		#### Cumulative Grade point average - CGPA \n
		$$CGPA = \\frac{\\sum Course Credits \\times Grade Points}{\\sum Total Credits}$$\n
		_Note in CGPA_ : for all courses, excluding those with “F” and transitional grades until that semester 
		"""
	)
