import streamlit as st

from common import *

st.set_page_config(page_title="Terms and Disclaimer", page_icon="👨‍💻", layout="centered")

local_css("styles.css")
local_html("index.html")

st.header("Terms and Disclaimer")
st.write(
	"""
	By using our app, you acknowledge and agree that we may cache certain information entered by you, 
	in order to provide faster access to that information upon subsequent use of the app. 
	We want to assure you that all information entered into our tool is encrypted and secure, 
	so no one can access your personal details.

	Please note that caching is not the same as storing. 
	Caching means that the backend of the website temporarily stores information to enable faster access to that information. 
	We do not permanently store any information entered into our app, 
	and we take great care to ensure that all information is deleted from our cache when it is no longer needed.

	We take the privacy and security of our users very seriously, 
	and we are committed to protecting your personal information. 
	By using our app, you agree to indemnify and hold us harmless from any loss or damage that may result from any unauthorized access to your personal information, 
	whether due to our app's vulnerabilities or your own actions.

	We reserve the right to update these Terms and Conditions at any time, 
	and we encourage you to review them periodically. 
	Your continued use of our app after any changes to these Terms and Conditions will constitute your acceptance of the revised terms.

	The authors have taken all possible measures to ensure that the results provided by our tool are as accurate as possible.
	However, we cannot guarantee the accuracy, completeness, or reliability of the information provided. 
	Therefore, we will not be liable for any damages or losses that may arise from the use of the tool or the information provided by it.
	It is the responsibility of the user to verify the accuracy of the information provided and to use it at their own risk.
	By using the app, you acknowledge and agree to these terms and conditions.
	
	If you have any questions or concerns about our caching policy, please contact the authors 
	<a class='name' href='https://wa.me/919945332995?text=This is regarding Calculla...'>here</a> or 
	<a class='name' href='https://wa.me/917019144708?text=This is regarding Calculla...'>here</a>
	""", unsafe_allow_html=True
)
