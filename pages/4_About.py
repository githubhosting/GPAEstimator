import streamlit as st

from common import *

st.set_page_config(page_title="About this Tool", page_icon="💡", layout="centered")

local_css("styles.css")

st.title("About this Tool")
st.write("This is born out of a need to calculate how much to score in Sem end exams to get a certain GPA.")
st.write("So, if want to check what minimum score you need in SEE to get respective Grades, you can use this tool.")
st.write("<b>We didn't stop there, We over-engineered this app and gave some special powers to this tool.</b>",
         unsafe_allow_html=True)

st.markdown(f"""
    <p>
        Read this <a class="name" href="{st.secrets.link1}" target="_blank">Blog</a> 
        to know them and how we built this tool.
    </p>
    <a href="{st.secrets.link2}"><button class="button">View Blog</button></a>
""", unsafe_allow_html=True)

st.markdown(f"""
    <br/>
    <p>
        For Queries Contact Us:
        <a class="name" href="https://wa.me/917019144708?text=I%20had%20some%20querry%20on%20calculla" target="_blank">Amith M</a>
        or
        <a class="name" href="https://wa.me/919945332995?text=I%20had%20some%20querry%20on%20calculla" target="_blank">Shravan</a>
    </p>
""", unsafe_allow_html=True)
