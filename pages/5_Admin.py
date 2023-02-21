import streamlit as st

from common import *
from src.RIRScraping.sis import CACHE_NAME

local_css("styles.css")
local_html("index.html")


def check_password():
	"""Returns `True` if the user had the correct password."""

	def password_entered():
		"""Checks whether a password entered by the user is correct."""
		if st.session_state["password"] == st.secrets["passwords"]["password"]:
			st.session_state["password_correct"] = True
			del st.session_state["password"]  # don't store password
		else:
			st.session_state["password_correct"] = False

	if "password_correct" not in st.session_state:
		# First run, show input for password.
		st.text_input(
			"Password", type="password", on_change=password_entered, key="password"
		)
		return False
	elif not st.session_state["password_correct"]:
		# Password not correct, show input + error.
		st.text_input(
			"Password", type="password", on_change=password_entered, key="password"
		)
		st.error("😕 Password incorrect")
		return False
	else:
		# Password correct.
		return True


if check_password():
	st.header("Admin Panel")

	for _ in range(5): st.write("\n")
	st.subheader("Tokens")
	eggs_name = st.secrets.easters["easter_eggs"]
	eggs_span = st.secrets.easters["easter_eggs_counter"]
	temps = st.secrets.easters.temps
	with st.form("Add Token", True):
		name = st.text_input("Token Name")
		span = st.slider("Token Span", 1, 50, 10)
		if st.form_submit_button("Add Token"):
			if name:
				st.success(f"token-{name} Added")
				eggs_name.append(name)
				temps.append(name)
				eggs_span.append(span)
			else:
				st.error("Give Token Name")
	for i, (en, es) in enumerate(zip(eggs_name, eggs_span)):
		c1, c2 = st.columns((10, 1))
		eggs_span[i] = c1.slider(en, 0, 50, es)
		if en in temps:
			c2.button(
				"🗑️", key=i, on_click=lambda _en=en, _i=i: eggs_name.pop(i) and eggs_span.pop(i) and temps.remove(en)
			)

	for _ in range(5): st.write("\n")
	st.subheader("Files")
	with open(f"data/{CACHE_NAME}.cache", "rb") as f:
		st.download_button("Export SIS Cache", f, f"{CACHE_NAME}.cache")
	with open(f"data/{CACHE_NAME}creds.cache", "rb") as f:
		st.download_button("Export SIS creds Cache", f, f"{CACHE_NAME}creds.cache")
	with open("data/logs.log" if st.secrets["cloud"] else "logs.txt", "r") as f:
		st.download_button("Export Logs", f, "logs.txt")
		for _ in range(5): st.write("\n")
		st.subheader("Logs")
		f.seek(0)
		for line in f.readlines(): st.write(line)
