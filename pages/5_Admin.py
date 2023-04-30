from datetime import datetime
from datetime import timedelta

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

from RITScraping import CACHE_NAME

from common import *

st.set_page_config(page_title="Admin Panel", page_icon="👨‍💻", layout="centered")

local_css("styles.css")

st.write("<br/>", unsafe_allow_html=True)


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


def get_stats(_usns, _stat):
    return f"{_usns} | {_stat}"


if check_password():
    st.header("Admin Panel")

    for _ in range(5): st.write("\n")
    st.subheader("Tokens")
    eggs_name = st.secrets.passwords["easter_eggs"]
    eggs_span = st.secrets.passwords["easter_eggs_counter"]
    temps = st.secrets.passwords.temps
    with st.form("Add Token", True):
        name = st.text_input("Token Name")
        span = st.number_input("Token Span", 1, 50, 10)
        if st.form_submit_button("Add Token"):
            if name:
                st.success(f"token-{name} Added")
                eggs_name.append(name)
                temps.append(name)
                eggs_span.append(span)
            else:
                st.error("Give Token Name")
    for i, (en, es) in enumerate(zip(eggs_name, eggs_span)):
        c2, c1 = st.columns((1, 10))
        eggs_span[i] = c1.number_input(en, 0, 50, es)
        if en in temps:
            c2.button(
                "🗑️", key=i, on_click=lambda _en=en, _i=i: eggs_name.pop(i) and eggs_span.pop(i) and temps.remove(en)
            )

    for _ in range(5): st.write("\n")
    st.subheader("Files")
    with open(f"RITScraping2.0/__async_cache__/{CACHE_NAME}.cache", "rb") as f:
        st.download_button("Export Cache", f, f"{CACHE_NAME}.cache")
    with open(f"RITScraping2.0/__async_cache__/{CACHE_NAME}.creds.cache", "rb") as f:
        st.download_button("Export Creds Cache", f, f"{CACHE_NAME}.creds.cache")
    st.download_button("Export Stats", get_stats(st.secrets.stats.usns, st.secrets.stats.totals), f"stats.txt")
    with open("data/logs.log" if st.secrets["cloud"] else "data/logs.txt", "r") as f:
        st.download_button("Export Logs", f, "logs.log")
        for _ in range(5): st.write("\n")
        st.subheader("Logs")
        f.seek(0)
        lines = f.read().replace("\n", "<br/><br/>")
        html(f"<p style='color: #b5afaf'>{lines}<p/>", height=400, scrolling=True)
    current_date = datetime.now().strftime("%d-%m-%Y")
    time_diff = datetime.strptime(f"5:29:53.000000", '%H:%M:%S.%f')
    time_frame = []
    all_usns = []
    tokens = []
    names = []
    formatted_times = []
    actual_times = []

    with open("data/logs.log", 'r') as f:
        for _ in range(5): st.write("\n")
        for _ in range(5): st.write("\n")
        line = f.readline()
        for line in f:
            if "|" in line:
                line = line.split("|")
                time_line = line[1]
                usn = line[2]
                token = line[5]
                name = line[4]
                names.append(name)
                tokens.append(token)
                all_usns.append(usn)
                time_line = time_line.strip()
                time_ = datetime.strptime(time_line, '%Y-%m-%d %H:%M:%S.%f')
                new_time = time_ + timedelta(hours=5, minutes=29, seconds=53)
                actual_times.append(new_time)
                formatted_time = new_time.strftime("%d %B %I:%M %p")
                formatted_times.append(formatted_time)
                time_frame.append(time_)
        time_data = {"Actual Time": formatted_times, "Name": names, "USN": all_usns, "Token": tokens}
        df = pd.DataFrame(time_data)
        Data_frame = df.iloc[::-1]
        st.dataframe(Data_frame, use_container_width=True)
        unique_token = list(set(tokens))
        search = st.radio("Select type of search", ["Search by Name", "Search by USN", "By Token"], horizontal=True)
        if search == "Search by Name":
            search_name = st.text_input("Search by Name").upper()
            if search_name:
                st.dataframe(Data_frame[Data_frame["Name"].str.contains(search_name)], use_container_width=True)
        if search == "Search by USN":
            search_usn = st.text_input("Search by USN").upper()
            if search_usn:
                st.dataframe(Data_frame[Data_frame["USN"].str.contains(search_usn)], use_container_width=True)
        if search == "By Token":
            search_token = st.multiselect("Search by Token", unique_token)
            if search_token:
                st.dataframe(Data_frame[Data_frame["Token"].isin(search_token)], use_container_width=True)

        total_views = list(range(1, len(time_frame) + 1))
        dept = []
        dept_ = []
        unique_usn = list(set(all_usns))
        st.write("Total number of Requests ", len(all_usns))
        st.write("Total number of unique USNs: ", len(unique_usn))
        graph = st.radio("Select type of graph", ["request vs time", "time vs request"], horizontal=True)
        if graph == "request vs time":
            df = pd.DataFrame({'Number of Requests': total_views}, index=time_frame)
            y = "Number of Requests"
        if graph == "time vs request":
            df = pd.DataFrame({"Time": time_frame}, index=range(1, len(time_frame) + 1))
            y = "Time"
        for usn in all_usns:
            dept.append(usn[4:8])
        for usn in unique_usn:
            dept_.append(usn[4:8])
        unique_dept = list(set(dept))
        dept_count = []
        dept_count_ = []
        for i in unique_dept:
            dept_count.append(dept.count(i))
        for j in unique_dept:
            dept_count_.append(dept_.count(j))

        dept_count, dept_count_, unique_dept = zip(*sorted(zip(dept_count, dept_count_, unique_dept), reverse=True))
        dept_counts = pd.DataFrame({"Dept": unique_dept, "Count Rep": dept_count, "Count Unique": dept_count_})

        st.subheader("Performance Analysis")
        st.line_chart(data=df, y=y, use_container_width=True)
        st.subheader("Department wise count")
        st.write(dept_counts)
        st.subheader("Token wise count")
        st.write(pd.DataFrame({"Token": tokens}).value_counts())
        st.subheader("USN wise count")
        df_usn = pd.DataFrame({"USN": all_usns, "Name": names}).value_counts()
        df_usn_most = df_usn.iloc[::1]
        st.write(df_usn_most)

    for _ in range(5): st.write("\n")
    st.subheader("Stats")
    usns = st.secrets.stats.usns
    stat = st.secrets.stats.totals
    st.write(f"Unique Searches: {len(usns)}")
    st.write(f"Total Searches: {stat[0]}")
    st.write(f"Creator Searches: {stat[1]}")
    st.write(usns)
