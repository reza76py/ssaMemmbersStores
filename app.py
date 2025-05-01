import streamlit as st
from datetime import date
import pandas as pd

# Import your view functions
from views.home_view import render_home_view
from forms.people_form import render_people_form
from forms.store_form import render_store_form
from forms.delivery_form import render_delivery_form
from forms.availability_form import render_availability_form
from core.assign import generate_assignments
from views.visit_plan_view import render_visit_plan
from views.visit_log_view import render_visit_log
from core.priority import calculate_store_priorities
from core.utils import today_str
from data.loaders import save_to_json, load_from_json
from data.db import initialize_database, get_connection

# -------------------------------
# 🟡 Database Fetch Helpers (Moved to Top!)
# -------------------------------

def fetch_people():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role, latitude, longitude FROM people")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "role": r[2], "latitude": r[3], "longitude": r[4]} for r in rows]

def fetch_stores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, latitude, longitude FROM stores")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "latitude": r[2], "longitude": r[3]} for r in rows]

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
    return [{"store_id": r[0], "store": r[1], "goods_value": r[2], "date": r[3]} for r in rows]

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
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[1], "role": r[2], "available": bool(r[3])} for r in rows]

# -------------------------------
# 🛠 Initialize App + DB
# -------------------------------
initialize_database()

with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------------
# 🏠 Sidebar Navigation
# -------------------------------
st.sidebar.title("SSA Assignment Dashboard")
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Home",
        "Register People",
        "Register Stores",
        "Add Deliveries",
        "Set Availability",
        "Generate Plan",
        "Distance Details",
        "Visit History",
        "Reset Database"
    ]
)

# -------------------------------
# 🖥️ Main Page Content
# -------------------------------
if menu == "Home":
    render_home_view()

elif menu == "Register People":
    st.title("👥 Register People (Leader/Member)")
    render_people_form()

elif menu == "Register Stores":
    st.title("🏬 Register Store Locations")
    render_store_form()

elif menu == "Add Deliveries":
    st.title("📦 Goods Delivery Input")
    render_delivery_form()

elif menu == "Set Availability":
    st.title("✅ Mark Available People")
    render_availability_form()

elif menu == "Generate Plan":
    st.title("📅 Generate Assignment Plan")
    if st.button("Generate Assignment Plan"):
        people = fetch_people()
        stores = fetch_stores()
        deliveries = fetch_deliveries_today()
        availability_today = fetch_availability_today()
        visit_log = st.session_state.get("visit_log", [])

        if not (people and stores and deliveries and availability_today):
            st.error("❌ Missing data: Make sure all forms are filled.")
        else:
            st.session_state.visit_plan, st.session_state.visit_plan_details = generate_assignments(
                stores, deliveries, availability_today, people, visit_log
            )
            st.success("✅ Plan created!")

elif menu == "Distance Details":
    st.title("📏 Detailed Distance Information")

    if "visit_plan_details" in st.session_state:
        df = pd.DataFrame(st.session_state.visit_plan_details)

        # ✅ Round all numeric values to integer
        df = df.applymap(lambda x: round(x) if isinstance(x, (int, float)) else x)

        # Apply friendly styling
        styled_df = df.style.set_properties(**{
            'white-space': 'normal',
            'text-align': 'left',
            'font-size': '14px'
        })

        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("ℹ️ No distance information available yet.")


elif menu == "Visit History":
    st.title("📜 Visit History")
    render_visit_log()

elif menu == "Reset Database":
    st.title("🛑 Reset Database")
    if 'reset_confirmed' not in st.session_state:
        st.session_state.reset_confirmed = False

    if st.button("⚠️ Reset Database"):
        st.session_state.reset_confirmed = True

    if st.session_state.reset_confirmed:
        confirm = st.checkbox("I understand this will delete ALL data permanently")

        if st.button("CONFIRM FULL RESET", type="primary"):
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DROP TABLE IF EXISTS people")
                    cursor.execute("DROP TABLE IF EXISTS stores")
                    cursor.execute("DROP TABLE IF EXISTS deliveries")
                    cursor.execute("DROP TABLE IF EXISTS availability")
                    cursor.execute("DROP TABLE IF EXISTS visit_logs")
                    cursor.execute("VACUUM")
                    conn.commit()

                initialize_database()

                keys_to_clear = [
                    "people", "stores", "deliveries", "availability",
                    "visit_plan", "visit_plan_details", "visit_log",
                    "reset_confirmed"
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]

                st.success("✅ Database fully reset to initial state!")
                st.experimental_rerun()

            except Exception as e:
                st.error(f"Error resetting database: {e}")

# -------------------------------
# 🟠 JSON Backup (optional)
# -------------------------------
today = today_str()

if "people" not in st.session_state:
    st.session_state.people = load_from_json("people.json")

if st.button("Save People Data (JSON)"):
    save_to_json("people.json", st.session_state.people)
    st.success("✅ People data saved to JSON!")
