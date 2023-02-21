import streamlit as _st

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
	('background-color', '#000'),
	("display", "inline-block")
]

tr_props = [
	("display", "none"),
]

styles = [
	dict(selector="th", props=th_props),
	dict(selector="td:nth-child(3)", props=td_props),
]

styles_attd = [
	dict(selector="td:nth-child(3)", props=td_props),
	dict(selector="td:nth-child(4)", props=td_props),
]

styles_gp = [
	dict(selector="td:nth-child(3)", props=td_props),
	dict(selector="td:nth-child(4)", props=td_props),
	dict(selector="td:nth-child(5)", props=td_props),
	dict(selector="thead tr th:first-child", props=tr_props),
	dict(selector="tbody tr th:first-child", props=tr_props),
]


def local_html(file_name):
	with open(file_name) as f:
		_st.markdown(f'{f.read()}', unsafe_allow_html=True)


def local_css(file_name):
	with open(file_name) as f:
		_st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
