import streamlit as st


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

	st.subheader("Tokens")
	with st.form("Add Token", True):
		name = st.text_input("Token Name")
		span = st.slider("Token Span", 1, 50, 10)
		if st.form_submit_button("Add Token"):
			if name:
				st.success(f"Token {name} Added")
				st.secrets["easters"]["easter_eggs"].append(name)
				st.secrets["easters"]["easter_eggs_counter"].append(span)
			else:
				st.error("Give Token Name")
	eggs_name = st.secrets["easters"]["easter_eggs"]
	eggs_span = st.secrets["easters"]["easter_eggs_counter"]
	for i, (en, es) in enumerate(zip(eggs_name, eggs_span)): eggs_span[i] = st.slider(en, 0, 50, es)

	st.subheader("Files")
	with open("siscacheri92gh45.cache") as f:
		st.download_button("Export SIS Cache", f, "siscacheri92gh45.cache")
	with open("siscacheri92gh45creds.cache") as f:
		st.download_button("Export SIS creds Cache", f, "siscacheri92gh45creds.cache")
