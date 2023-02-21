import streamlit as st

from common import *

local_css("styles.css")
local_html("index.html")

st.title("About")
st.write("This is an over-engineered app to calculate your GPA")
