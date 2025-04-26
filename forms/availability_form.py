import streamlit as st
from datetime import date

def render_availability_form():
    st.subheader("Select Available People")

    if "people" in st.session_state and len(st.session_state.people) > 0:
        available_today = set()

        with st.form("availability_form"):
            st.write("Tick who is available **today**:")
            for idx, person in enumerate(st.session_state.people):
                key = f"avail_{idx}"
                if st.checkbox(f"{person['role'].capitalize()}: {person['name']}", key=key):
                    available_today.add(person["name"])

            submitted = st.form_submit_button("Save Availability")

            if submitted:
                today = str(date.today())
                st.session_state.availability = [
                    {"name": p["name"], "role": p["role"], "available": p["name"] in available_today, "date": today}
                    for p in st.session_state.people
                ]
                st.success("Today's availability has been saved.")

        # Show today's available people
        if "availability" in st.session_state:
            st.subheader("Today's Available People")
            today_avail = [a for a in st.session_state.availability if a["available"]]
            if today_avail:
                st.table(today_avail)
            else:
                st.info("No one marked available.")
    else:
        st.warning("⚠️ Please register leaders and members first.")
