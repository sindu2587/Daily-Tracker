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
    completed INTEGER,
    percent REAL,
    color TEXT
)
""")
conn.commit()

# ---------- UI STYLE ----------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #8360c3, #2ebf91);
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📘 Daily Routine Tracker")

# ---------- NAVIGATION ----------
page = st.sidebar.selectbox("📂 Menu", ["🏠 Main", "📅 History"])

# ---------- USER ----------
user = st.text_input("👤 Enter your name")

# ================= MAIN =================
if page == "🏠 Main" and user:

    st.subheader(f"Welcome, {user} 👋")

    date = st.date_input("📅 Select Date")
    date_str = date.strftime("%Y-%m-%d")

    st.write("### ✍️ Write Your Study Goals")

    goal1 = st.text_area("1️⃣ Goal 1")
    goal2 = st.text_area("2️⃣ Goal 2")
    goal3 = st.text_area("3️⃣ Goal 3")

    completed = st.number_input("✅ How many goals completed?", min_value=0, max_value=3)

    if st.button("💾 Save Data"):

        total_goals = 3
        percent = (completed / total_goals) * 100

        if percent >= 90:
            color = "Green"
            msg = f"Excellent! You reached your goal ({percent:.0f}%) 🎉"
        elif percent >= 70:
            color = "Yellow"
            msg = f"You completed {percent:.0f}% 👍"
        else:
            color = "Red"
            msg = f"You did not reach your goal, only {percent:.0f}% ❗"

        full_goal = f"{goal1} | {goal2} | {goal3}"

        c.execute("INSERT INTO tracker VALUES (?,?,?,?,?,?)",
                  (user, date_str, full_goal, completed, percent, color))
        conn.commit()

        # ⏱ Temporary message
        placeholder = st.empty()

        if color == "Green":
            placeholder.success(msg)
        elif color == "Yellow":
            placeholder.warning(msg)
        else:
            placeholder.error(msg)

        time.sleep(2)
        placeholder.empty()

# ================= HISTORY =================
if page == "📅 History" and user:

    st.subheader("📆 Month-wise History")

    c.execute("SELECT * FROM tracker WHERE user=?", (user,))
    rows = c.fetchall()

    months = {}

    for r in rows:
        month = r[1][:7]
        months.setdefault(month, []).append(r)

    for m in sorted(months):
        st.markdown(f"### 📌 {m}")

        for r in months[m]:
            percent = r[4]
            color = r[5]

            # 🎨 Show color + percentage
            if color == "Green":
                st.success(f"📅 {r[1]} → {percent:.0f}% 🟢 Completed Fully")
            elif color == "Yellow":
                st.warning(f"📅 {r[1]} → {percent:.0f}% 🟡 Average")
            else:
                st.error(f"📅 {r[1]} → {percent:.0f}% 🔴 Not Completed")

            st.caption(f"📖 Goals: {r[2]}")

            # Extra message for low performance
            if percent < 70:
                st.error(f"You did not reach your goal ({percent:.0f}%)")
