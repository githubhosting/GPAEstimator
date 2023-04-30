import asyncio
import math
import sys
import time
from datetime import datetime, date, timedelta
from random import random

import extra_streamlit_components as stx
import pandas as pd
import streamlit as st

sys.path.append("RITScraping2.0/src")

from tools import sub_lists, grade_estimates

from RITScraping import sis_micro, exam_micro, SisScraper, validate_usn
from common import *

st.set_page_config(page_title="Calculla - GPA Calculator", page_icon="📊", layout="centered")
# st.title("Calculla - GPA Calculator")
# st.caption("""
# Made with Passion by
# <a class="name" href="https://github.com/Amith225" target="_blank">
#     Amith M
# </a> and
# <a class="name" href="https://myselfshravan.github.io/" target="_blank">
#     Shravan Revanna
# </a>
# """, unsafe_allow_html=True)
local_html("header.html")
local_css("styles.css")
st.caption("---")

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
        </p
    """, unsafe_allow_html=True
)
st.write(f'Total Searches: {st.secrets.stats.totals[0]} | Unique Searches: {len(st.secrets.stats.usns)}')
tab1, tab2, tab3, tab4 = st.tabs(["Check SIS", "GPA - Estimator", "Priority - Score", "Simple - Calculator"])

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
Shravan <a class='name' href="https://wa.me/919945332995?text=what%20is%20the%20working%20token%20for%20calculla">here 🚀</a> or 
Amith <a class='name' href="https://wa.me/917019144708?text=what%20is%20the%20working%20token%20for%20calculla">here 🚀</a>
to get new token 😉
"""
rick_roll_msgs = [
    "I'll never give you up, I'll never let you down, I'll always be there, lurking around. 😁",
    "<a href='https://pichost.pics/9FZ3M4'><button>Hurray! see next puzzle here</button></a>"
]
hand_wave_gif = "<img width='30' vertical-align:sub " \
                "src='https://github.com/1999AZZAR/1999AZZAR/blob/main/resources/img/waving.gif?raw=true'>"


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()


@st.cache_data(ttl=60 * 60 * 12)  # 12 hours
def get_stats(usn, dob):
    if dob is None: return {}, {}
    even_sis, odd_sis = sis_micro(usn, dob, odd=False), sis_micro(usn, dob, odd=True)
    sis_stats = even_sis if even_sis["marks"] else odd_sis
    exam_stats = exam_micro(usn, even=True) or exam_micro(usn, even=False)
    return sis_stats, exam_stats


def brutes(usn):
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
        if not easter: cookie_manager.set(sis_stats["usn"], sis_stats["dob"],
                                          expires_at=datetime.now() + timedelta(days=7))
        log(st.session_state.usn, sis_stats["name"], sis_stats["dob"], easter)
    _, sub_names, sub_attds, sub_marks, sub_max_marks, _, _ = sub_lists(sis_stats["marks"])

    welcome = "Hey"
    symbol = hand_wave_gif
    if easter:
        welcome = "Stalking"
        symbol = "🕵️"
    st.text("")
    col1, col2 = st.columns(2)
    col1.image(exam_stats["photo"], width=200, use_column_width=True)
    col2.markdown(
        f"<br/><br/><h3 style='text-align: center; margin-block: auto;'>{welcome} {sis_stats['name']}! {symbol}<h3>",
        unsafe_allow_html=True
    )

    st.text("")
    with st.expander(f"CIE Marks for Semester {sis_stats['sem'][-3:]} : {sum(sub_marks)}/{sum(sub_max_marks)}",
                     expanded=True):
        marks = sis_stats["marks"]
        for i, (code, m) in enumerate(marks.items()):
            name = m["sub"]
            cies, ces = m["cies"], m["ces"]
            with st.container():
                m_dick = {"C-1": "-", "C-2": "-", "A-1": "-", "A-2": "-"}
                m_dick.update({f"C-{i + 1}": [v[0]] for i, v in enumerate(cies)})
                m_dick.update({f"A-{i + 1}": [v[0]] for i, v in enumerate(ces)})
                m_dick["Total"] = m['tot'][0]
                table = pd.DataFrame(m_dick, index=[0])
                st.write(
                    f"<p class='submarks'>{name} - {code}</p>",
                    table.style.hide(axis="index").to_html(), "<hr/>" if i + 1 != len(marks) else "<br/>",
                    unsafe_allow_html=True
                )

    st.text("")
    with st.expander("Show Attendance"):
        st.markdown("""<h5 style='text-align: center;'>Attendance for this semester</h5> """,
                    unsafe_allow_html=True)
        short_attendance = []
        for j in sub_attds:
            if j < 75: short_attendance.append({sub_names[sub_attds.index(j)]})
        attendance = [str(j) + "%" for j in sub_attds]
        table = pd.DataFrame(
            {"Subject": sub_names, "Percentage": attendance},
            index=[k for k in range(1, len(sub_marks) + 1)]
        )
        st.markdown(table.style.set_table_styles(styles_attd).to_html(), unsafe_allow_html=True)

        if short_attendance:
            st.write("")
            st.write("Following Subjects have shortage of attendance")
            for key in short_attendance:
                remove = str(key).replace("{'", "").replace("'}", "")
                st.warning(remove)
        for _ in range(2): st.write("\n")

    st.text("")
    st.markdown("<h5 style='text-align: center;'>The following are the SGPA's</h5>", unsafe_allow_html=True)
    table = pd.DataFrame({
        "SEM": [f"Semester {s}" for s in range(1, len(sis_stats["sgpas"]) + 1)],
        "SGPA": [f"{s:.2f}" for s in sis_stats["sgpas"]]
    })
    st.markdown(table.style.set_table_styles(styles_gp).to_html(), unsafe_allow_html=True)


def tab_1():
    crack_msg_div = st.empty()
    easter = None

    st.subheader("Check Internals")
    usn = st.text_input("Enter Valid USN", placeholder="1ms21is000",
                        on_change=lambda: st.session_state.update(checked=False)).strip().upper()
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
        yyyy, mm, dd = int(usn[3:5]) - 18 + 2000, 1, 1
        cookie_dob = cookie_manager.get(cookie=usn)
        if cookie_dob is not None:
            yyyy, mm, dd = map(int, cookie_dob.split("-"))
            st.session_state.update(checked=True)
        if easter:
            dob = crack(usn, easter)
        else:
            dob = st.date_input("Enter DOB", date(yyyy, mm, dd),
                                on_change=lambda: st.session_state.update(checked=False)).strftime("%Y-%m-%d")
        crack_msg_div.empty()
        if easter or st.session_state.checked or \
                st.button("Check", on_click=lambda: st.session_state.update(checked=True)):
            st.session_state.checked = True
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
    if st.session_state.checked:
        sis_stats, exam_stats = get_stats(st.session_state.usn, st.session_state.dob)
        if not sis_stats or not st.session_state.checked:
            st.warning("Invalid USN or DOB", icon="🚨")
            return
    else:
        st.warning("First Check SIS", icon="🚨")
        return

    st.subheader("Grade & GPA Estimator")
    st.caption("Mark your predicted/expected grades for each subject, and then scroll down to see the estimated GPA.")
    sub_codes, sub_names, _, sub_marks, sub_max_marks, sub_avg_cie, _ = sub_lists(sis_stats["marks"])
    sub_creds = [sis_stats["creds"][k] for k in sub_codes]

    with st.container():
        sgpas = sis_stats["sgpas"]
        grade_in_each = []
        estimates = grade_estimates(
            sub_marks, sub_names, sub_max_marks,
            **{"O": 90, "A+": 80, "A": 70, "B+": 60, "B": 55, "C": 50, "P": 40}
        )
        for m, mm, sn, e, c in zip(sub_marks, sub_max_marks, sub_names, estimates, sub_creds):
            if c > 1:
                for ee in e: e[ee] *= 2
            def_gi = 0
            if mm != 0: def_gi = 10 - math.ceil(m / mm * 10)
            grade_in_each.append(st.radio(f"{sn} - {m}", ["O", "A+", "A", "B+", "B", "C", "P", "F"],
                                          index=def_gi if def_gi >= 0 else 7, horizontal=True))
            table = pd.DataFrame(e, index=[sn])
            st.write(
                table.style.hide(axis="index").to_html(), "<hr/>",
                unsafe_allow_html=True
            )
        grade_point = [grade_to_gp[g] for g in grade_in_each]
        weighted_gp = [i * j for i, j in zip(grade_point, sub_creds)]
        total_gp_final = sum(weighted_gp)
        st.write("")
        with st.expander("Show Grade Point Table"):
            st.write("<p class='mt'>Based on the above grades, this will be your final credits and SGPA</p>",
                     unsafe_allow_html=True)
            table = pd.DataFrame({
                "Subject": sub_names, "Credits": sub_creds,
                "Grade Points": [f"{w}/{c * 10}" for w, c in zip(weighted_gp, sub_creds)]
            })
            st.write(table.style.set_table_styles(styles_gp).to_html(), "<br/>", unsafe_allow_html=True)
        sgpa = total_gp_final / sum(sub_creds)
        sgpa = round(sgpa, 3)
        st.write(f"<h3 class='mt'>Your Estimated SGPA is: {sgpa:.3f}</h2>", unsafe_allow_html=True)
        st.write(
            f"<h3 class='mt'>Your Estimated CGPA is: {((sgpa + sum(sgpas)) / (1 + len(sgpas))):.3f}</h2>",
            unsafe_allow_html=True
        )


@st.cache_resource(ttl=60 * 60 * 12)  # 12 hours
def get_priority_params(sub_creds, sub_marks, sub_max_marks, sub_avg_cie):
    difficulty = []
    next_dist = []
    c1, c2 = [], []
    for cred, mark, max_mark, avg in zip(sub_creds, sub_marks, sub_max_marks, sub_avg_cie):
        if max_mark == 0:
            difficulty.append(0)
            next_dist.append(0)
            c1.append(0)
            c2.append(0)
            continue
        frac_mark = mark / max_mark
        dist_next = math.ceil(frac_mark * 10) / 10 - frac_mark
        avg_frac = avg / 30
        diff = (1 - avg_frac) * 0.25 + (1 - frac_mark) * 0.75
        difficulty.append(diff)
        next_dist.append(dist_next)
        c1.append(diff / frac_mark)
        c2.append((1 - diff) * frac_mark)
    return difficulty, next_dist, c1, c2


def home():
    if "usn" not in st.session_state: st.session_state.usn = None
    if "prev_usn" not in st.session_state: st.session_state.prev_usn = None
    if "prev_easter" not in st.session_state: st.session_state.prev_easter = None
    if "dob" not in st.session_state: st.session_state.dob = None
    if "checked" not in st.session_state: st.session_state.checked = False

    with tab1:
        tab_1()
    with tab2:
        tab_2()
    with tab3:
        if st.session_state.checked:
            sis_stats, exam_stats = get_stats(st.session_state.usn, st.session_state.dob)
            if not sis_stats or not st.session_state.checked:
                st.warning("Invalid USN or DOB", icon="🚨")
                return
        else:
            st.warning("First Check SIS", icon="🚨")
            return

        st.subheader("Prioritize and Conquer")
        sub_codes, sub_names, _, sub_marks, sub_max_marks, sub_avg_cie, _ = sub_lists(sis_stats["marks"])
        sub_creds = [sis_stats["creds"][k] for k in sub_codes]

        difficulty, next_dist, c1, c2 = get_priority_params(sub_creds, sub_marks, sub_max_marks, sub_avg_cie)
        st.caption(
            "Lesser the criterion value, easier the ability to score without much effort. "
            "Higher the value, requires some effort but still possible to score well. "
            "Use optimal value close to 0.75 for best results.",
            unsafe_allow_html=False)
        cr = st.slider("Select Criterion [0 - Easy Next Grade, 1 - Difficult Next Grade]",
                       0., 1., 0.75, 0.01, key="criterion", format="%.2f")
        priority = [cred * (c1i * cr + c2i * (1 - cr)) * (1 - nd) for cred, c1i, c2i, nd in
                    zip(sub_creds, c1, c2, next_dist)]
        zip_list = sorted(zip(sub_marks, sub_creds, sub_codes, sub_names, priority), key=lambda k: k[4], reverse=True)
        sub_marks, sub_creds, sub_codes, sub_names, priority = zip(*zip_list)

        priority_score = [f"{m:.1f}" for m in priority]
        table = pd.DataFrame({
            "Subject": sub_names,
            "CIE": sub_marks,
            "Priority": priority_score,
        }, index=[i for i in range(1, len(sub_marks) + 1)])
        st.write(table.style.hide(axis="index").set_table_styles(styles).to_html(), "<br/>",
                 unsafe_allow_html=True)
        with st.expander("How its Calculated"):
            st.latex(r"Priority = \frac{Credits \times (C1 \times CR + C2 \times (1 - CR)) \times (1 - NextDist)}{100}")
            st.markdown("where")
            st.latex(rf"CR = Criterion = {cr}")
            st.latex(r"C1 = Toughness = \frac{Difficulty}{MaxMarks}")
            st.latex(r"C2 = Easiness = (1 - Difficulty)) \times MaxMarks")
            st.latex(r"NextDist = NextGradePoint = \frac{MaxMarks - CIE}{MaxMarks}")
            st.latex(r"Difficulty = \frac{(1 - \frac{AvgMarks}{MaxMarks}) \times 0.25 + (1 - \frac{CIEMarks}{MaxMarks}) \times 0.75}{MaxMarks}")

    with tab4:
        st.subheader("How much is average CIE marks for 50?")
        avg = st.slider("Average CIE marks", 0, 50, value=35, step=1)
        to_score = (90 - avg) * 2
        st.write("Following is the minimum marks you need to score in SEE to get respective grades")
        grades = [to_score, to_score - 20, to_score - 40, to_score - 60, to_score - 80, to_score - 100]
        for i in range(len(grades)):
            if grades[i] > 100:
                grades[i] = " "
        grade_letter = ["O", "A+", "A", "B+", "B", "C"]
        table_1 = pd.DataFrame({"Grade": grade_letter, "Marks": grades})
        st.write(table_1.style.hide(axis="index").set_table_styles(styles).to_html(), unsafe_allow_html=True)
        st.write("")
        st.write("Here is how its calculated :")
        st.write(
            f"You scored {avg}, then you need {to_score} in SEE to get O Grade. "
            f"Because half of {to_score} which is {to_score / 2} is added to {avg} equals to {(to_score / 2) + avg} "
            f"and that is minimum to get O Grade"
        )


if __name__ == '__main__':
    home()
