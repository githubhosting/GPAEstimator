import streamlit as st

from common import *

st.set_page_config(page_title="About this Tool", page_icon="💡", layout="centered")

local_css("styles.css")
local_html("index.html")

st.title("About this Tool")
st.write("This is born out of a need to calculate how much to score in Sem end exams to get a certain GPA.")
st.write("So, if want to check what minimum score you need in SEE to get respective Grades, you can use this tool.")
st.write("<b>We didn't stop there, We over-engineered this app and gave some special powers to this tool.</b>",
         unsafe_allow_html=True)
link = st.secrets["link"]

st.markdown(f"""
	<p>
		Read this <a class="name" href="https://shravanrevanna.hashnode.dev/the-next-level-gpa-calculator-with-special-powers" target="_blank">Blog</a> to know them and how we built this tool.
	</p>
	<a href="{link}"><button class="button">View Blog</button></a>
""", unsafe_allow_html=True)
