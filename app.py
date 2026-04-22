import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Daily Tracker", page_icon="📘")

DATA_FILE = "data.json"

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

st.title("📘 Daily Routine Tracker")

# User
user = st.text_input("👤 Enter your name")

if user:
    if user not in data:
        data[user] = {}

    st.subheader(f"Welcome, {user} 👋")

    # Date input
    selected_date = st.date_input("📅 Select Date")
    date_str = selected_date.strftime("%Y-%m-%d")

    # Inputs
    total = st.number_input("📖 Total Goal", min_value=1)
    completed = st.number_input("✅ Completed", min_value=0)
    note = st.text_area("📝 Notes")

    # Save
    if st.button("💾 Save Data"):
        percent = (completed / total) * 100

        if percent >= 90:
            color = "Green"
        elif percent >= 70:
            color = "Yellow"
        else:
            color = "Red"

        data[user][date_str] = {
            "total": total,
            "completed": completed,
            "percent": percent,
            "color": color,
            "note": note
        }

        save_data(data)
        st.success("Data saved!")

    # Show result
    if date_str in data[user]:
        d = data[user][date_str]
        st.subheader("📊 Result")

        if d["color"] == "Green":
            st.success(f"{d['percent']:.2f}% - Excellent 🟢")
        elif d["color"] == "Yellow":
            st.warning(f"{d['percent']:.2f}% - Average 🟡")
        else:
            st.error(f"{d['percent']:.2f}% - Need Improvement 🔴")

    # 🔘 View History Button
    if st.button("📅 View History"):

        st.subheader("📆 Month-wise History")

        months = {}
        for d in data[user]:
            month = d[:7]
            if month not in months:
                months[month] = []
            months[month].append((d, data[user][d]))

        selected_to_delete = []

        for month in sorted(months):
            st.markdown(f"### 📌 {month}")
            for entry in sorted(months[month]):
                d, info = entry

                col1, col2 = st.columns([1, 6])

                with col1:
                    check = st.checkbox("", key=d)

                with col2:
                    st.write(f"📅 {d} → {info['percent']:.2f}% ({info['color']})")
                    if info["note"]:
                        st.caption(f"📝 {info['note']}")

                if check:
                    selected_to_delete.append(d)

        # 🗑 Delete Button
        if st.button("🗑 Delete Selected"):
            for d in selected_to_delete:
                del data[user][d]

            save_data(data)
            st.success("Selected data deleted!")
