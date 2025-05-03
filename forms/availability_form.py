import streamlit as st
from datetime import date
from data.db import get_connection

def render_availability_form():


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
            if st.checkbox(f"{role.capitalize()} --->  {name}", key=key):
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
    st.subheader("Available People")
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
        import pandas as pd
        table_data = [{"Name": a[0], "Role": a[1]} for a in available_people]
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No one is marked available yet today.")

