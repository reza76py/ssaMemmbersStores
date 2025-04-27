# import streamlit as st
# from datetime import date
# from forms.people_form import render_people_form
# from forms.store_form import render_store_form
# from forms.delivery_form import render_delivery_form
# from forms.availability_form import render_availability_form
# from core.assign import generate_assignments
# from core.priority import calculate_store_priorities
# from views.visit_plan_view import render_visit_plan
# from views.visit_log_view import render_visit_log
# from core.utils import today_str
# from data.loaders import save_to_json, load_from_json
# from data.db import initialize_database
# from data.db import get_connection

# with open("styles/styles.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# with st.expander("🧑‍💼 Register People (Leader / Member)"):
#     render_people_form()


# with st.expander("🏬 Register Store Locations"):
#     render_store_form()

# with st.expander("📦 Goods Delivery Input"):
#     render_delivery_form()

# with st.expander("✅ Mark Available People"):
#     render_availability_form()


# if st.button("Generate Assignment Plan"):
#     conn = get_connection()
#     cursor = conn.cursor()

#     # Load people from DB
#     cursor.execute("SELECT id, name, role, latitude, longitude FROM people")
#     people = cursor.fetchall()

#     # Load stores from DB
#     cursor.execute("SELECT id, name, latitude, longitude FROM stores")
#     stores = cursor.fetchall()

#     # Load deliveries from DB
#     today = str(date.today())
#     cursor.execute("""
#         SELECT d.store_id, s.name, d.goods_value, d.date
#         FROM deliveries d
#         JOIN stores s ON d.store_id = s.id
#         WHERE d.date = ?
#     """, (today,))
#     deliveries = cursor.fetchall()

#     # Load availability from DB
#     cursor.execute("""
#         SELECT a.person_id, p.name, p.role, a.available
#         FROM availability a
#         JOIN people p ON a.person_id = p.id
#         WHERE a.date = ?
#     """, (today,))
#     availability = cursor.fetchall()

#     conn.close()

#     # Check that data exists
#     if not (people and stores and deliveries and availability):
#         st.error("Missing data: make sure all forms are filled.")
#     else:
#         st.session_state.visit_plan = generate_assignments(
#             stores,
#             deliveries,
#             availability,
#             people
#         )
#         st.success("✅ Plan created!")

#         if st.session_state.visit_plan:
#             st.subheader("📅 Visit Plan (Next 3 Days)")
#             st.table(st.session_state.visit_plan)


#         else:
#             st.error("Missing data: make sure all forms are filled.")



# if "stores" in st.session_state and "visit_log" in st.session_state:
#     priority_data = calculate_store_priorities(
#         st.session_state.stores,
#         st.session_state.visit_log
#     )
#     st.table(priority_data)
# else:
#     st.info("No stores or visit logs to analyze yet.")



# # Assignment output (Section 4)
# with st.expander("📅 Generated Visit Plan"):
#     render_visit_plan()

# # Visit history (Section 5)
# with st.expander("📜 Visit History"):
#     render_visit_log()





# today = today_str()

# if "people" not in st.session_state:
#     st.session_state.people = load_from_json("people.json")

# if st.button("Save Data"):
#     save_to_json("people.json", st.session_state.people)
#     st.success("Data saved to file!")


# initialize_database()









import streamlit as st
from datetime import date
from forms.people_form import render_people_form
from forms.store_form import render_store_form
from forms.delivery_form import render_delivery_form
from forms.availability_form import render_availability_form
from core.assign import generate_assignments
from core.priority import calculate_store_priorities
from views.visit_plan_view import render_visit_plan
from views.visit_log_view import render_visit_log
from core.utils import today_str
from data.loaders import save_to_json, load_from_json
from data.db import initialize_database, get_connection

# Initialize the database when the app starts
initialize_database()

# Load custom CSS
with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------------
# 🟢 Forms Section
# -------------------------------

with st.expander("🧑‍💼 Register People (Leader / Member)"):
    render_people_form()

with st.expander("🏬 Register Store Locations"):
    render_store_form()

with st.expander("📦 Goods Delivery Input"):
    render_delivery_form()

with st.expander("✅ Mark Available People"):
    render_availability_form()

with st.expander("📏 Detailed Distance Info"):
    if "visit_plan_details" in st.session_state:
        st.table(st.session_state.visit_plan_details)
    else:
        st.info("No detailed distance data available yet.")


# -------------------------------
# 🟡 Fetch Database Helpers
# -------------------------------

def fetch_people():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role, latitude, longitude FROM people")
    rows = cursor.fetchall()
    conn.close()

    # Convert to dictionaries
    people = []
    for row in rows:
        people.append({
            "id": row[0],
            "name": row[1],
            "role": row[2],
            "latitude": row[3],
            "longitude": row[4]
        })
    return people

def fetch_stores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, latitude, longitude FROM stores")
    rows = cursor.fetchall()
    conn.close()

    # Convert to dictionaries
    stores = []
    for row in rows:
        stores.append({
            "id": row[0],
            "name": row[1],
            "latitude": row[2],
            "longitude": row[3]
        })
    return stores

def fetch_deliveries_today():
    today = today_str()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.store_id, s.name, d.goods_value, d.date
        FROM deliveries d
        JOIN stores s ON d.store_id = s.id
        WHERE d.date = ?
    """, (today,))
    rows = cursor.fetchall()
    conn.close()

    # Convert to dictionaries
    deliveries = []
    for row in rows:
        deliveries.append({
            "store_id": row[0],
            "store": row[1],
            "goods_value": row[2],
            "date": row[3]
        })
    return deliveries


def fetch_availability_today():
    today = today_str()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.person_id, p.name, p.role, a.available
        FROM availability a
        JOIN people p ON a.person_id = p.id
        WHERE a.date = ?
    """, (today,))
    results = cursor.fetchall()
    conn.close()
    availability = [
        {"name": row[1], "role": row[2], "available": bool(row[3])}
        for row in results
    ]
    return availability

# -------------------------------
# 🟣 Assignment Generator Button
# -------------------------------

if st.button("Generate Assignment Plan"):
    people = fetch_people()
    stores = fetch_stores()
    deliveries = fetch_deliveries_today()
    availability_today = fetch_availability_today()
    visit_log = st.session_state.get("visit_log", [])  # 🟡 NEW: Get visit log

    if not (people and stores and deliveries and availability_today):
        st.error("❌ Missing data: Make sure all forms are filled.")
    else:
        st.session_state.visit_plan, st.session_state.visit_plan_details = generate_assignments(
            stores,
            deliveries,
            availability_today,
            people,
            visit_log  # 🟡 NEW: Pass visit log
        )
        st.success("✅ Plan created!")

# -------------------------------
# 🟤 Priority Display
# -------------------------------

if "stores" in st.session_state and "visit_log" in st.session_state:
    priority_data = calculate_store_priorities(
        st.session_state.stores,
        st.session_state.visit_log
    )
    st.table(priority_data)
else:
    st.info("ℹ️ No stores or visit logs to analyze yet.")

# -------------------------------
# 🔵 Visit Plan and History
# -------------------------------

with st.expander("📅 Generated Visit Plan"):
    render_visit_plan()

with st.expander("📜 Visit History"):
    render_visit_log()

# -------------------------------
# 🟠 JSON Backup (optional)
# -------------------------------

today = today_str()

if "people" not in st.session_state:
    st.session_state.people = load_from_json("people.json")

if st.button("Save People Data (JSON)"):
    save_to_json("people.json", st.session_state.people)
    st.success("Data saved to JSON!")

