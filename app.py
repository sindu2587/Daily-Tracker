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

# ---------- COLORFUL BACKGROUND ----------
st.markdown("""
<style>

/* Full background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a2a6c, #b21f1f, #fdbb2d);
    color: white;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Title */
h1 {
    color: #00f5d4;
    text-align: center;
}

/* Subheaders */
h2, h3 {
    color: #ffd166;
}

/* Inputs */
input, textarea {
    background-color: #2e2e3e !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Selectbox & number input */
.stSelectbox, .stNumberInput {
    background-color: #2e2e3e !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(45deg, #00f5d4, #9b5de5);
    color: black;
    border-radius: 10px;
    font-weight: bold;
}

/* Messages */
.stSuccess {
    background-color: #1b5e20 !important;
}
.stWarning {
    background-color: #ff8f00 !important;
}
.stError {
    background-color: #b71c1c !important;
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

    # -------- GOAL SYSTEM --------
    st.subheader("📌 How many goals today?")
    total_goals = st.number_input("Select number of goals", 1, 10, 1)

    goals = []
    completions = []

    for i in range(int(total_goals)):
        st.markdown(f"### Goal {i+1}")

        goal = st.text_area(f"Write Goal {i+1}", key=f"goal_{i}")

        status = st.selectbox(
            f"Status of Goal {i+1}",
            ["Not Done (0)", "Half Done (0.5)", "Fully Done (1)"],
            key=f"status_{i}"
        )

        if "Fully" in status:
            value = 1
        elif "Half" in status:
            value = 0.5
        else:
            value = 0

        goals.append(goal)
        completions.append(value)

    if st.button("Save Data"):

        percent = (sum(completions) / len(completions)) * 100

        if percent >= 90:
            color = "Green"
        elif percent >= 70:
            color = "Yellow"
        else:
            color = "Red"

        c.execute("INSERT INTO tracker VALUES (?,?,?,?,?,?)",
                  (user, date_str, str(goals), str(completions), percent, color))
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
