import streamlit as st
import sqlite3
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

# ---------- BLUE BACKGROUND ----------
st.markdown("""
<style>
body {
    background-color: #87CEEB;
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
    completion = st.text_area(" ")

    if st.button("Save Data"):

        # 👉 Auto percentage (simple logic)
        if len(goal) == 0:
            percent = 0
        else:
            percent = min((len(completion) / len(goal)) * 100, 100)

        # 👉 Color logic
        if percent >= 90:
            color = "Green"
        elif percent >= 70:
            color = "Yellow"
        else:
            color = "Red"

        c.execute("INSERT INTO tracker VALUES (?,?,?,?,?,?)",
                  (user, date_str, goal, completion, percent, color))
        conn.commit()

        st.success("Saved successfully!")

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
        selected_month = st.selectbox("Choose Month", sorted(months.keys()))

        st.markdown(f"### 📌 {selected_month}")

        for r in sorted(months[selected_month]):
            percent = r[4]
            color = r[5]

            # 👉 SHOW color + percentage HERE
            if color == "Green":
                st.success(f"{r[1]} → {percent:.0f}% 🟢")
            elif color == "Yellow":
                st.warning(f"{r[1]} → {percent:.0f}% 🟡")
            else:
                st.error(f"{r[1]} → {percent:.0f}% 🔴")

            st.write("Goal:", r[2])
            st.write("Completion:", r[3])
            st.markdown("---")
    else:
        st.info("No data available yet.")
