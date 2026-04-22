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
    total INTEGER,
    completed INTEGER,
    percent REAL,
    color TEXT,
    note TEXT
)
""")
conn.commit()

# ---------- UI STYLE ----------
st.markdown("""
<style>
body {background-color: #f0f2f6;}
.big-title {color:#2c3e50; text-align:center;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big-title'>📘 Daily Routine Tracker</h1>", unsafe_allow_html=True)

# ---------- NAVIGATION ----------
page = st.sidebar.selectbox("📂 Menu", ["🏠 Main", "📅 History"])

# ---------- USER ----------
user = st.text_input("👤 Enter your name")

# ================= MAIN PAGE =================
if page == "🏠 Main" and user:

    st.subheader(f"Welcome, {user} 👋")

    selected_date = st.date_input("📅 Select Date")
    date_str = selected_date.strftime("%Y-%m-%d")

    # ✍️ Big goal writing
    goal = st.text_area("✍️ Write your full study goal")

    total = st.number_input("📖 Total Target (pages/tasks)", min_value=1)
    completed = st.number_input("✅ Completed", min_value=0)

    note = st.text_area("📝 Notes")

    if st.button("💾 Save Data"):

        percent = (completed / total) * 100

        if percent >= 90:
            color = "Green"
            message = "Excellent! You reached your goal 🎉"
        elif percent >= 70:
            color = "Yellow"
            message = f"You did okay. You completed {percent:.0f}% 👍"
        else:
            color = "Red"
            message = f"You did not reach your goal, you completed only {percent:.0f}% ❗"

        c.execute("INSERT INTO tracker VALUES (?,?,?,?,?,?,?,?)",
                  (user, date_str, goal, total, completed, percent, color, note))
        conn.commit()

        # 🎨 Show result
        if color == "Green":
            st.success(message)
        elif color == "Yellow":
            st.warning(message)
        else:
            st.error(message)

# ================= HISTORY PAGE =================
if page == "📅 History" and user:

    st.subheader("📆 Month-wise History")

    c.execute("SELECT * FROM tracker WHERE user=?", (user,))
    rows = c.fetchall()

    months = {}

    for row in rows:
        date = row[1]
        month = date[:7]

        if month not in months:
            months[month] = []
        months[month].append(row)

    selected_to_delete = []

    for month in sorted(months):
        st.markdown(f"### 📌 {month}")

        for r in months[month]:
            d, goal, total, completed, percent, color, note = r[1], r[2], r[3], r[4], r[5], r[6], r[7]

            col1, col2 = st.columns([1,6])

            with col1:
                check = st.checkbox("", key=d)

            with col2:
                st.write(f"📅 {d} → {percent:.0f}% ({color})")
                st.caption(f"📖 Goal: {goal}")
                st.caption(f"✅ Done: {completed}/{total}")

                if percent < 70:
                    st.error(f"You did not reach your goal, only {percent:.0f}%")

                if note:
                    st.caption(f"📝 {note}")

            if check:
                selected_to_delete.append(d)

    if st.button("🗑 Delete Selected"):
        for d in selected_to_delete:
            c.execute("DELETE FROM tracker WHERE user=? AND date=?", (user, d))
        conn.commit()
        st.success("Deleted successfully!")
