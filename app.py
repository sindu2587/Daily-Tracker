import streamlit as st
import sqlite3
import time
from datetime import datetime

st.set_page_config(page_title="Daily Tracker", page_icon="📘")

# ---------- DATABASE ----------
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS tracker (
    user TEXT,
    date TEXT,
    goal TEXT,
    completion TEXT,
    percent REAL,
    color TEXT
)
""")
conn.commit()

# ---------- LIGHT BLUE UI ----------
st.markdown("""
<style>
body {
    background-color: #cce7ff;
}
</style>
""", unsafe_allow_html=True)

st.title("📘 Daily Routine Tracker")

# ---------- NAV ----------
page = st.sidebar.selectbox("Menu", ["Main", "History"])

user = st.text_input("Enter your name")

# ================= MAIN =================
if page == "Main" and user:

    date = st.date_input("Select Date")
    date_str = date.strftime("%Y-%m-%d")

    st.subheader("✍️ Write Your Goal")
    goal = st.text_area("")

    st.subheader("✅ Write Your Completion")
    completion_text = st.text_area(" ")

    total = st.number_input("Total (for %)", min_value=1)
    completed = st.number_input("Completed (for %)", min_value=0)

    if st.button("Save Data"):

        percent = (completed / total) * 100

        if percent >= 90:
            color = "Green"
            msg = f"Excellent! {percent:.0f}%"
        elif percent >= 70:
            color = "Yellow"
            msg = f"You completed {percent:.0f}%"
        else:
            color = "Red"
            msg = f"You did not reach goal ({percent:.0f}%)"

        c.execute("INSERT INTO tracker VALUES (?,?,?,?,?,?)",
                  (user, date_str, goal, completion_text, percent, color))
        conn.commit()

        box = st.empty()
        if color == "Green":
            box.success(msg)
        elif color == "Yellow":
            box.warning(msg)
        else:
            box.error(msg)

        time.sleep(2)
        box.empty()

# ================= HISTORY =================
if page == "History" and user:

    st.subheader("📅 Select Month")

    c.execute("SELECT * FROM tracker WHERE user=?", (user,))
    rows = c.fetchall()

    months = {}

    for r in rows:
        month = datetime.strptime(r[1], "%Y-%m-%d").strftime("%B %Y")
        months.setdefault(month, []).append(r)

    if months:
        # 👉 Only user-created months appear
        selected_month = st.selectbox("Choose Month", sorted(months.keys()))

        st.markdown(f"### 📌 {selected_month}")

        for r in sorted(months[selected_month]):
            percent = r[4]
            color = r[5]

            if color == "Green":
                st.success(f"{r[1]} → {percent:.0f}% 🟢")
            elif color == "Yellow":
                st.warning(f"{r[1]} → {percent:.0f}% 🟡")
            else:
                st.error(f"{r[1]} → {percent:.0f}% 🔴")

            st.write("Goal:", r[2])
            st.write("Completion:", r[3])
    else:
        st.info("No data available yet.")
