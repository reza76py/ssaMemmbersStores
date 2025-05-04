# import streamlit as st
# from datetime import date
# import pandas as pd  # If you use any DataFrames or future charts
# from core.utils import today_str  # You already use this in other parts
# from data.db import get_connection  # Your existing DB connector



# def render_dashboard():
#     st.title("📊 Assignment Dashboard")

#     # Fetch data
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT COUNT(*) FROM people")
#     total_people = cursor.fetchone()[0]

#     cursor.execute("SELECT COUNT(*) FROM stores")
#     total_stores = cursor.fetchone()[0]

#     today = today_str()
#     cursor.execute("SELECT COUNT(*) FROM deliveries WHERE date = ?", (today,))
#     deliveries_today = cursor.fetchone()[0]

#     cursor.execute("SELECT COUNT(*) FROM visit_plan WHERE visit_date = ?", (today,))
#     plans_today = cursor.fetchone()[0]

#     cursor.execute("SELECT COUNT(*) FROM read_confirmations WHERE visit_date = ?", (today,))
#     confirmations_today = cursor.fetchone()[0]

#     cursor.execute("""
#         SELECT COUNT(*) 
#         FROM visit_plan 
#         WHERE visit_date = ? 
#           AND person_id NOT IN (
#               SELECT person_id FROM read_confirmations WHERE visit_date = ?
#           )
#     """, (today, today))
#     pending_confirmations = cursor.fetchone()[0]

#     conn.close()

#     # Create columns and display metrics
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("🧍 Total People", total_people)
#         st.metric("🏬 Total Stores", total_stores)

#     with col2:
#         st.metric("📦 Deliveries Today", deliveries_today)
#         st.metric("🗓️ Plans Generated", plans_today)

#     with col3:
#         st.metric("✅ Confirmed", confirmations_today)
#         st.metric("❌ Pending", pending_confirmations)


        






import streamlit as st
from datetime import date
import pandas as pd
from core.utils import today_str
from data.db import get_connection


def render_dashboard():
    st.title("📊 Assignment Dashboard")

    # Fetch data
    conn = get_connection()
    cursor = conn.cursor()

    today = today_str()

    # Metrics
    cursor.execute("SELECT COUNT(*) FROM people")
    total_people = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM stores")
    total_stores = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM deliveries WHERE date = ?", (today,))
    deliveries_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM visit_plan WHERE visit_date = ?", (today,))
    plans_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM read_confirmations WHERE visit_date = ?", (today,))
    confirmations_today = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) 
        FROM visit_plan 
        WHERE visit_date = ? 
          AND person_id NOT IN (
              SELECT person_id FROM read_confirmations WHERE visit_date = ?
          )
    """, (today, today))
    pending_confirmations = cursor.fetchone()[0]

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🧍 Total People", total_people)
        st.metric("🏬 Total Stores", total_stores)

    with col2:
        st.metric("📦 Deliveries Today", deliveries_today)
        st.metric("🗓️ Plans Generated", plans_today)

    with col3:
        st.metric("✅ Confirmed", confirmations_today)
        st.metric("❌ Pending", pending_confirmations)

    # ----------------------------------
    # 🟥 Show Pending Confirmation Table
    # ----------------------------------
    cursor.execute("""
        SELECT p.id, p.name, p.role, vp.store_name
        FROM visit_plan vp
        JOIN people p ON vp.person_id = p.id
        WHERE vp.visit_date = ?
    """, (today,))
    all_assigned = cursor.fetchall()

    cursor.execute("""
        SELECT person_id, store_name
        FROM read_confirmations
        WHERE visit_date = ?
    """, (today,))
    confirmed = set(cursor.fetchall())

    conn.close()

    pending = [
        (person_id, name, role, store)
        for person_id, name, role, store in all_assigned
        if (person_id, store) not in confirmed
    ]

    if pending:
        st.markdown("---")
        st.subheader("❌ Pending Confirmations")
        df = pd.DataFrame(pending, columns=["ID", "Name", "Role", "Store"])
        st.dataframe(df, use_container_width=True)
    else:
        st.success("✅ Everyone has confirmed their assignment today.")
