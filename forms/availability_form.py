# import streamlit as st
# from datetime import date

# def render_availability_form():
#     st.subheader("Select Available People")

#     if "people" in st.session_state and len(st.session_state.people) > 0:
#         available_today = set()

#         with st.form("availability_form"):
#             st.write("Tick who is available **today**:")
#             for idx, person in enumerate(st.session_state.people):
#                 key = f"avail_{idx}"
#                 if st.checkbox(f"{person['role'].capitalize()}: {person['name']}", key=key):
#                     available_today.add(person["name"])

#             submitted = st.form_submit_button("Save Availability")

#             if submitted:
#                 today = str(date.today())
#                 st.session_state.availability = [
#                     {"name": p["name"], "role": p["role"], "available": p["name"] in available_today, "date": today}
#                     for p in st.session_state.people
#                 ]
#                 st.success("Today's availability has been saved.")

#         # Show today's available people
#         if "availability" in st.session_state:
#             st.subheader("Today's Available People")
#             today_avail = [a for a in st.session_state.availability if a["available"]]
#             if today_avail:
#                 st.table(today_avail)
#             else:
#                 st.info("No one marked available.")
#     else:
#         st.warning("⚠️ Please register leaders and members first.")









# with db_connection:
import streamlit as st
from datetime import date
from data.db import get_connection

def render_availability_form():
    st.subheader("Select Available People")

    # Load people from DB
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role FROM people")
    people = cursor.fetchall()
    conn.close()

    if not people:
        st.warning("⚠️ Please register leaders and members first.")
        return

    available_today_ids = set()

    with st.form("availability_form"):
        st.write("Tick who is available **today**:")
        for person in people:
            person_id, name, role = person
            key = f"avail_{person_id}"
            if st.checkbox(f"{role.capitalize()}: {name}", key=key):
                available_today_ids.add(person_id)

        submitted = st.form_submit_button("Save Availability")

        if submitted:
            today = str(date.today())
            conn = get_connection()
            cursor = conn.cursor()

            for person in people:
                person_id = person[0]
                available = 1 if person_id in available_today_ids else 0

                # First delete any existing availability for today
                cursor.execute("""
                    DELETE FROM availability
                    WHERE person_id = ? AND date = ?
                """, (person_id, today))

                # Insert updated value
                cursor.execute("""
                    INSERT INTO availability (person_id, available, date)
                    VALUES (?, ?, ?)
                """, (person_id, available, today))

            conn.commit()
            conn.close()
            st.success("✅ Availability saved for today!")

    # Show today's available people
    st.subheader("Today's Available People")
    today = str(date.today())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.role
        FROM availability a
        JOIN people p ON a.person_id = p.id
        WHERE a.date = ? AND a.available = 1
    """, (today,))
    available_people = cursor.fetchall()
    conn.close()

    if available_people:
        st.table([{"Name": a[0], "Role": a[1]} for a in available_people])
    else:
        st.info("No one is marked available yet today.")
