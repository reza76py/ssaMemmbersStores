# import streamlit as st
# from data.db import get_connection

# def render_visit_log():
#     st.subheader("📜 Past Visit Logs")

#     if "visit_plan" in st.session_state and st.session_state.visit_plan:
#         plan_copy = st.session_state.visit_plan.copy()  # 🔥 Protect data copy

#         if st.button("✅ Finalize & Save Current Plan to History"):
#             # 🔥 Always create and close connection inside the button block
#             conn = get_connection()
#             cursor = conn.cursor()

#             try:
#                 for plan in plan_copy:
#                     date_str = plan["date"]
#                     store_name = plan["store"]
#                     leader_name = plan["leader"]
#                     members = ",".join(plan["members"])

#                     # Get store ID
#                     cursor.execute("SELECT id FROM stores WHERE name = ?", (store_name,))
#                     store_row = cursor.fetchone()
#                     if store_row:
#                         store_id = store_row[0]
#                     else:
#                         continue

#                     # Get leader ID
#                     cursor.execute("SELECT id FROM people WHERE name = ?", (leader_name,))
#                     leader_row = cursor.fetchone()
#                     if leader_row:
#                         leader_id = leader_row[0]
#                     else:
#                         continue

#                     # Insert visit log
#                     cursor.execute("""
#                         INSERT INTO visit_logs (date, store_id, leader_id, members)
#                         VALUES (?, ?, ?, ?)
#                     """, (date_str, store_id, leader_id, members))

#                 conn.commit()
#                 st.success("Visit plan saved to history ✅")
#                 st.session_state.visit_plan = []

#             except Exception as e:
#                 st.error(f"Error saving visit log: {e}")

#             finally:
#                 conn.close()  # 💥 Always close connection immediately after save

#     # 📋 Always open a new connection to read logs
#     conn = get_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute("""
#             SELECT v.date, s.name AS store, p.name AS leader, v.members
#             FROM visit_logs v
#             JOIN stores s ON v.store_id = s.id
#             JOIN people p ON v.leader_id = p.id
#             ORDER BY v.date DESC
#         """)
#         logs = cursor.fetchall()

#         if logs:
#             st.table([
#                 {"Date": log[0], "Store": log[1], "Leader": log[2], "Members": log[3]}
#                 for log in logs
#             ])
#         else:
#             st.info("No visit history yet.")

#     except Exception as e:
#         st.error(f"Error loading visit logs: {e}")

#     finally:
#         conn.close()  # 💥 Always close connection after reading logs













import streamlit as st
from data.db import get_connection
import sqlite3

def render_visit_log():
    st.subheader("📜 Past Visit Logs")

    if "visit_plan" in st.session_state and st.session_state.visit_plan:
        if st.button("✅ Finalize & Save Current Plan to History"):
            conn = None
            try:
                conn = get_connection()
                cursor = conn.cursor()
                total_saved = 0
                errors = []

                # Use a transaction
                with conn:
                    for idx, item in enumerate(st.session_state.visit_plan):
                        # Fetch store_id
                        cursor.execute("SELECT id FROM stores WHERE name = ?", (item["store"],))
                        store_id_result = cursor.fetchone()
                        store_id = store_id_result[0] if store_id_result else None

                        # Fetch leader_id
                        cursor.execute("SELECT id FROM people WHERE name = ?", (item["leader"],))
                        leader_id_result = cursor.fetchone()
                        leader_id = leader_id_result[0] if leader_id_result else None

                        if not store_id:
                            errors.append(f"Row {idx+1}: Store '{item['store']}' not found")
                        if not leader_id:
                            errors.append(f"Row {idx+1}: Leader '{item['leader']}' not found")

                        if store_id and leader_id:
                            cursor.execute("""
                                INSERT INTO visit_logs (date, store_id, leader_id, members)
                                VALUES (?, ?, ?, ?)
                            """, (
                                item["date"],
                                store_id,
                                leader_id,
                                ",".join(item["members"])
                            ))
                            total_saved += 1

                    if total_saved > 0:
                        st.success(f"Successfully saved {total_saved} visits to history! ✅")
                        st.session_state.visit_plan = []
                    else:
                        st.warning("No visits were saved")

                    if errors:
                        st.error("Validation errors occurred:")
                        for error in errors:
                            st.write(f"• {error}")

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    st.error("Database busy - please wait a moment and try again")
                else:
                    st.error(f"Database error: {str(e)}")
                if conn:
                    conn.rollback()

            except Exception as e:
                st.error(f"Error: {str(e)}")
                if conn:
                    conn.rollback()

            finally:
                if conn:
                    conn.close()

    # Visit log table (READING PART)
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.date, s.name AS store, p.name AS leader, v.members
            FROM visit_logs v
            JOIN stores s ON v.store_id = s.id
            JOIN people p ON v.leader_id = p.id
            ORDER BY v.date DESC
        """)
        visit_logs = cursor.fetchall()

        if visit_logs:
            st.table([{
                "Date": v[0],
                "Store": v[1],
                "Leader": v[2],
                "Members": v[3]
            } for v in visit_logs])
        else:
            st.info("No visits logged yet.")

    except Exception as e:
        st.error(f"Error loading visit logs: {e}")
    finally:
        if conn:
            conn.close()