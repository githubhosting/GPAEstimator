import streamlit as st

from common import *

st.set_page_config(page_title="Terms and Disclaimer", page_icon="👨‍💻", layout="centered")

local_css("styles.css")
local_html("index.html")

st.header("Terms and Disclaimer")
st.write(
	"""
	This tool was built to help students in their scoring with some fun elements and educational intent,
	to ensure reliability and speed, we cache the details once entered.

	Please note that the authors have taken all possible measures to ensure that the results provided by our tool are as accurate as possible.
	However, we cannot guarantee the accuracy, completeness, or reliability of the information provided. 
	Therefore, we will not be liable for any damages or losses that may arise from the use of the tool or the information provided by it.
	It is the responsibility of the user to verify the accuracy of the information provided and to use it at their own risk.
	By using the app, you acknowledge and agree to these terms and conditions.
	"""
)
