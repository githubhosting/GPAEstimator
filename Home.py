import asyncio
import sys
import time
from datetime import datetime, date
from random import random

import streamlit as st

from tools import sub_lists

sys.path.append("RITScraping2.0/src")

from RITScraping import sis_micro, exam_micro, SisScraper, validate_usn
from common import *

st.set_page_config(page_title="Calculla - GPA Calculator", page_icon="📊", layout="centered")
st.title("Calculla - GPA Calculator")
st.caption("""
Made with Passion by 
<a class="name" href="https://github.com/Amith225" target="_blank">
    Amith M
</a> and
<a class="name" href="https://myselfshravan.github.io/" target="_blank">
    Shravan Revanna
</a>
""", unsafe_allow_html=True)
local_css("styles.css")

st.write(
    f"""
        <p>
            Follow the <a class="name" target="_self" href="/Instructions_and_Working">Instructions</a> 
            and check the <a class="name" target="_self" href="/Terms_and_Disclaimer">Terms</a>
            for the tool. <br/>
            Check our blogs
            <a class="name" href="https://amithm3.hashnode.dev/calculla-the-over-engineered-gpa-calculator">Here</a> and
            <a class="name" href="https://shravanrevanna.hashnode.dev/calculla-the-next-level-gpa-calculator">Here</a>
            to know more about the tool.
        </p>
        <p>
            Repo Link: <a class="name" href={st.secrets.github_link}>Github</a> 
            | 
            <a class="name" href={st.secrets.beta_link}>Join</a> as a beta tester
        </p
    """, unsafe_allow_html=True
)
st.write(f'Total Searches: {st.secrets.stats.totals[0]} | Unique Searches: {len(st.secrets.stats.usns)}')
tab1, tab2, tab3 = st.tabs(["Check SIS", "GPA - Estimator", "Simple - Calculator"])

grade_to_gp = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}
forbidden_usns = ["1MS21IS017", "1MS21CI049"]

crack_forbid_msg = """
**💨 Whoa, hold your horses! 🐴 What do you think you're doing? 
🧐 Do you really think you can crack the creators' password with THEIR OWN fancy tool? 
Let's face it, if the creators' password was a piñata, you wouldn't even be able to hit it with a baseball bat 😎. 
But don't worry, we won't judge you for trying. 🫡"**
"""
crack_expired_msg = """
But unfortunately, the creators has temporarily suspended this token that cracks the DOB. 
How about trying another token?"
"""
creator_contact_msg = """
Contact the creators
Shravan <a class='name' href="https://wa.me/919945332995?text=what%is%the%working%token%for%calculla">here 🚀</a> or 
Amith <a class='name' href="https://wa.me/917019144708?text=what%is%the%working%token%for%calculla">here 🚀</a>
to get new token 😉
"""
rick_roll_msgs = [
    "I'll never give you up, I'll never let you down, I'll always be there, lurking around. 😁",
    "<a href='https://pichost.pics/9FZ3M4'><button>Hurray! see next puzzle here</button></a>"
]
hand_wave_gif = "<img width='30' vertical-align:sub src='https://github.com/1999AZZAR/1999AZZAR/blob/main/resources/img/waving.gif?raw=true'>"


@st.cache_data(ttl=60 * 60 * 12)  # 12 hours
def get_stats(usn, dob):
    sis_stats = sis_micro(usn, dob, st.secrets.ODD)
    exam_stats = exam_micro(usn, st.secrets.EVEN)
    return sis_stats, exam_stats


def brutes(usn) -> str | None:
    async def brute():
        async with SisScraper() as scraper:
            return await scraper.brute_dob(usn)

    return asyncio.run(brute())


def log(usn, name, dob, easter):
    if usn in forbidden_usns:
        name = "CREATOR"
        dob = "huss-hh-hh"
    with open("data/logs.log" if st.secrets["cloud"] else "data/logs.txt", "a") as file:
        file.write(f"[LOG] | {datetime.now()} | {usn} | {dob} | {name} | {f'token-{easter}' if easter else 'dob'}\n")
        usns = st.secrets.stats.usns
        totals = st.secrets.stats.totals
        if (a := f"{usn} {dob} {name}") not in usns: usns.append(a)
        totals[0] += 1
        totals[1] += int(name == 'CREATOR')


def deduct(easter):
    eggs_name = st.secrets.passwords["easter_eggs"]
    eggs_span = st.secrets.passwords["easter_eggs_counter"]
    eggs_span[eggs_name.index(easter)] -= 1


def crack(usn, easter):
    if st.session_state.prev_usn == usn and st.session_state.prev_easter == easter:
        st.info(f"DOB: **{datetime.strptime(st.session_state.dob, '%Y-%m-%d').strftime('%d %B %Y')}**")
        return st.session_state.dob
    if usn in forbidden_usns:
        st.error(crack_forbid_msg)
        log(usn, "", "", easter)
        return
    t = time.time()
    dob = brutes(usn)
    t = time.time() - t
    if t < 5:
        time.sleep(et := random() * 3 + 2)
        t += et
    if dob is not None:
        st.success(f"Cracked! in {t:.2f} seconds 🎉")
        st.info(f"DOB: **{datetime.strptime(dob, '%Y-%m-%d').strftime('%d %B %Y')}**")
        st.session_state.prev_easter = easter
        deduct(easter)
    else:
        st.error(f"Couldn't crack. 😔")
    st.caption("Please use this tool with caution. We are not responsible for any misuse of this tool.")
    return dob


def tab_1_valid(sis_stats, exam_stats, easter):
    if st.session_state.prev_usn != st.session_state.usn:
        log(st.session_state.usn, sis_stats["name"], sis_stats["dob"], easter)

    welcome = "Hey"
    symbol = hand_wave_gif
    if easter:
        welcome = "Stalking"
        symbol = "🕵️"
    st.text("")
    col1, col2 = st.columns(2)
    col1.markdown(
        f"<br/><br/><h3 style='text-align: center; margin-block: auto;'>{welcome} {sis_stats['name']}! {symbol}<h3>",
        unsafe_allow_html=True
    )
    col2.image(exam_stats["photo"], width=200, use_column_width=True)

    sub_codes, sub_names, sub_attds, sub_marks, sub_max_marks = sub_lists(sis_stats["marks"])
    st.write(f"<br/><h4 style='text-align: center'>CIE Marks for Semester {sis_stats['sem']}</h4>", unsafe_allow_html=True)


def tab_1():
    crack_msg_div = st.empty()
    easter = None

    st.subheader("Check Internal Marks")
    usn = st.text_input("Enter Valid USN", placeholder="1ms21is000").strip().upper()
    if " " in usn:
        usn, easter = usn.split(maxsplit=1)
        easter = easter.lower()

    eggs_name = st.secrets.passwords["easter_eggs"]
    eggs_span = st.secrets.passwords["easter_eggs_counter"]
    if easter in eggs_name:
        if eggs_span[eggs_name.index(easter)] > 0:
            crack_msg_div = st.empty()
            with crack_msg_div.container():
                st.success(f"Yay! token-{easter} has been applied! 🎊")
                st.info("Have a coffee while we try cracking the DOB")
        else:
            st.success(f"Yay! **{easter}** is correct ! 🎉")
            st.warning(crack_expired_msg)
            st.info("Please contact the **Admin** or try again later")
            st.markdown(creator_contact_msg, unsafe_allow_html=True)
            easter = None
    elif easter:
        if "rick" in easter or "roll" in easter:
            st.info(rick_roll_msgs[0])
            time.sleep(3)
            st.write(rick_roll_msgs[1], unsafe_allow_html=True)
        else:
            st.error("Nah ah ha ha")
            st.warning("You didn't get the magic word!")
        easter = None

    if validate_usn(usn):
        st.session_state.usn = usn
        if "prev_usn" not in st.session_state: st.session_state.prev_usn = None
        if "prev_easter" not in st.session_state: st.session_state.prev_easter = None
        if "dob" not in st.session_state: st.session_state.dob = None
        yyyy, mm, dd = int(usn[3:5]) - 18 + 2000, 1, 1
        if easter:
            dob = crack(usn, easter)
        else:
            dob = st.date_input("Enter DOB", date(yyyy, mm, dd)).strftime("%Y-%m-%d")
        crack_msg_div.empty()
        if easter or st.button("Check"):
            sis_stats, exam_stats = get_stats(usn, dob)
            if not sis_stats:
                st.warning("Invalid USN or DOB", icon="🚨")
            else:
                tab_1_valid(sis_stats, exam_stats, easter)
                st.session_state.prev_usn = usn
                st.session_state.dob = dob
    elif usn:
        st.error('Invalid USN', icon="🚨")


def tab_2():
    pass


def home():
    with tab1: tab_1()
    with tab2: tab_2()
    with tab3: pass


if __name__ == '__main__':
    home()
