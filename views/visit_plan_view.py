# import streamlit as st

# def render_visit_plan():
#     if "visit_plan" in st.session_state and st.session_state.visit_plan:
#         st.subheader("📅 Visit Plan (Next 3 Days)")
#         st.table(st.session_state.visit_plan)
#     else:
#         st.info("No assignment plan generated yet.")









import streamlit as st
import sqlite3
from data.db import get_connection

def render_visit_plan():
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all assignments
    cursor.execute("""
        SELECT v.person_id, p.name, p.role, v.store_name, v.visit_date
        FROM visit_plan v
        JOIN people p ON v.person_id = p.id
        ORDER BY v.visit_date, p.role DESC
    """)
    assignments = cursor.fetchall()

    if not assignments:
        st.info("No assignment plan generated yet.")
        return

    st.subheader("📅 Visit Plan with Confirmation")
    
    for person_id, name, role, store, visit_date in assignments:
        key = f"{person_id}_{store}_{visit_date}"

        # Check if already confirmed
        cursor.execute("""
            SELECT 1 FROM read_confirmations 
            WHERE person_id = ? AND store_name = ? AND visit_date = ?
        """, (person_id, store, visit_date))
        confirmed = cursor.fetchone() is not None

        with st.form(key=key):
            st.write(f"👤 **{name}** ({role}) → 🏬 **{store}** on 📅 **{visit_date}**")
            if confirmed:
                st.success("✅ Read confirmed")
            else:
                confirm = st.checkbox("I have read this", key=f"cb_{key}")
                if st.form_submit_button("Submit Confirmation"):
                    if confirm:
                        try:
                            cursor.execute("""
                                INSERT INTO read_confirmations (person_id, store_name, visit_date, read)
                                VALUES (?, ?, ?, 1)
                            """, (person_id, store, visit_date))
                            conn.commit()
                            st.success("📩 Confirmation saved!")
                            st.experimental_rerun()
                        except sqlite3.Error as e:
                            st.error(f"❌ Error saving confirmation: {e}")

    conn.close()
