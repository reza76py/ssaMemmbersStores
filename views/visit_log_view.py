# import streamlit as st

# def render_visit_log():
#     st.subheader("📜 Past Visit Logs")

#     # Save button
#     if "visit_plan" in st.session_state and st.session_state.visit_plan:
#         if st.button("✅ Finalize & Save Current Plan to History"):
#             if "visit_log" not in st.session_state:
#                 st.session_state.visit_log = []

#             for item in st.session_state.visit_plan:
#                 st.session_state.visit_log.append({
#                     "date": item["date"],
#                     "store": item["store"],
#                     "leader": item["leader"],
#                     "members": ", ".join(item["members"])
#                 })

#             st.success("Visit plan saved to history ✅")
#             st.session_state.visit_plan = []

#     # Show the visit log
#     if "visit_log" in st.session_state and st.session_state.visit_log:
#         st.table(st.session_state.visit_log)
#     else:
#         st.info("No visits have been logged yet.")










# with db_connection:
import streamlit as st
from data.db import get_connection

def render_visit_log():
    st.subheader("📜 Past Visit Logs")

    if "visit_plan" in st.session_state and st.session_state.visit_plan:
        plan_copy = st.session_state.visit_plan.copy()  # 🛡️ Protect before reset

        if st.button("✅ Finalize & Save Current Plan to History"):
            conn = get_connection()
            cursor = conn.cursor()

            for plan in plan_copy:
                date_str = plan["date"]
                store_name = plan["store"]
                leader_name = plan["leader"]
                members = ",".join(plan["members"])

                # Get IDs
                cursor.execute("SELECT id FROM stores WHERE name = ?", (store_name,))
                store_row = cursor.fetchone()
                if store_row:
                    store_id = store_row[0]
                else:
                    continue

                cursor.execute("SELECT id FROM people WHERE name = ?", (leader_name,))
                leader_row = cursor.fetchone()
                if leader_row:
                    leader_id = leader_row[0]
                else:
                    continue

                cursor.execute("""
                    INSERT INTO visit_logs (date, store_id, leader_id, members)
                    VALUES (?, ?, ?, ?)
                """, (date_str, store_id, leader_id, members))

            conn.commit()
            conn.close()
            st.success("Visit plan saved to history ✅")

            # Clear AFTER saving
            st.session_state.visit_plan = []

    # Always display logs
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.date, s.name AS store, p.name AS leader, v.members
        FROM visit_logs v
        JOIN stores s ON v.store_id = s.id
        JOIN people p ON v.leader_id = p.id
        ORDER BY v.date DESC
    """)
    logs = cursor.fetchall()
    conn.close()

    if logs:
        st.table([
            {"Date": log[0], "Store": log[1], "Leader": log[2], "Members": log[3]}
            for log in logs
        ])
    else:
        st.info("No visit history yet.")
