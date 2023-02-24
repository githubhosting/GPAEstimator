import streamlit as st

from common import *

st.set_page_config(page_title="Riddles and Easter Egg", page_icon="🥚", layout="centered")

local_css("styles.css")
local_html("index.html")

st.title("Riddles and Easter Egg")
st.write(
	f"The answer to these easy riddles are designed to be key to unlock the magical powers of this app. <a class='name' href='{st.secrets['link']}'>Click here</a> to read those special powers.",
	unsafe_allow_html=True)
st.write("After Finding the answer to the riddle just append it to any USN by giving space.")
st.caption("Example: '1ms21is000 <answer>' in the USN field")

st.write("<hr/>", unsafe_allow_html=True)

st.markdown(
	"""
	My tune is catchy, and my lyrics are fine,
	But to hear them, you must take the time.
	Click a link, play a game,
	But don't be fooled, it's all the same.

	A prank that's old, but still alive,
	A classic joke, that won't be denied.
	You think you're safe, you think you're sound,
	But with a single click, I'll turn you around.
	"""
)

st.write("<hr/>", unsafe_allow_html=True)

st.markdown(
	"""
	I am a tool that can be used,
	To peek beneath the surface, confused?
	Look closely, for I am your key,
	To hidden treasures, can you see?
	
	With a right-click and a bit of luck,
	You can reveal what's been tucked,
	A secret lies just out of sight,
	But with me, it's just a quick insight.
	"""
)

st.write("<hr/>", unsafe_allow_html=True)

st.markdown(
	"""
	In a world of hidden blades,
	And conspiracies that never fades,
	A hooded figure takes the lead,
	On a quest for justice, so great a need.
	
	With ancient secrets to uncover,
	And enemies to carefully smother,
	The path ahead is dark and unclear.
	
	Who are we?
	"""
)

st.write("<hr/>", unsafe_allow_html=True)

st.markdown(
	"""
	In the world of AI, where data reigns supreme,
	There are tools that can help fulfill your dream.
	TensorFlow is where the normies can be found,
	A powerful tool, but a bit unrefined all around.
	
	Pytorch is the cool kids choice
	Elegant and expressive, it makes your code rejoice.
	But wait there's another way
	??? is where the champions come to play.
	"""
)

st.write("<hr/>", unsafe_allow_html=True)

st.markdown(
	"""
	With this info, you can find your age,
	Counting the years since you were a babe.

	What is the word that helps you see,
	How long you've been on this Earth, free?
	"""
)

st.write("<input hidden value='rookie'/>", unsafe_allow_html=True)
