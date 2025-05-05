import streamlit as st
from datetime import date
import pandas as pd
import time  # Added for cache busting
import hashlib  # Added for cache busting
from urllib.parse import unquote
import sqlite3

# Import your view functions
from views.home_view import render_home_view
from forms.people_form import render_people_form
from forms.store_form import render_store_form
from forms.delivery_form import render_delivery_form
from forms.availability_form import render_availability_form
from views.dashboard_view import render_dashboard
from core.assign import generate_assignments
from views.visit_plan_view import render_visit_plan
from views.visit_log_view import render_visit_log
from core.priority import calculate_store_priorities
from core.utils import today_str
from data.loaders import save_to_json, load_from_json
from data.db import initialize_database, get_connection
from notifications.email_assignment import send_assignment_emails

# -------------------------------
# 🟡 Database Fetch Helpers
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
# 🎨 CSS Injection with Cache Busting
# -------------------------------
def inject_css():
    with open("styles/styles.css") as f:
        css = f.read()
        cache_buster = hashlib.md5(css.encode()).hexdigest()[:8]

    st.markdown(
        f"<style>{css}</style>?v={cache_buster}",
        unsafe_allow_html=True
    )

inject_css()


# -------------------------------
# ✅ Handle Read Confirmation Token
# -------------------------------
from urllib.parse import unquote

confirm_token = st.query_params.get("confirm_read")

if confirm_token:
    st.title("📬 Assignment Read Confirmation")
    parts = unquote(confirm_token).split("-", 2)
    if len(parts) == 3:
        person_id, store, visit_date = parts
        try:
            person_id = int(person_id)
        except ValueError:
            st.error("Invalid person_id in confirmation link.")
            st.stop()

        st.write(f"ℹ️ Saving confirmation: person_id={person_id}, store={store}, date={visit_date}")

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO read_confirmations (person_id, store_name, visit_date)
                VALUES (?, ?, ?)
            """, (person_id, store, visit_date))
            conn.commit()
            st.success(f"✅ Confirmed! You have read your assignment to {store} on {visit_date}.")
        except sqlite3.IntegrityError:
            st.warning("⚠️ You have already confirmed this assignment.")
        finally:
            conn.close()
            st.stop()


    else:
        st.error("⚠️ Invalid confirmation token format.")
        st.stop()


# -------------------------------
# 🏠 Sidebar Navigation
# -------------------------------
st.sidebar.title("SSA Assignment Dashboard")
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Home",
        "Dashboard",
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

elif menu == "Dashboard":
    render_dashboard()


elif menu == "Register People":
    st.title("👥 Register People (Leader/Member)")
    render_people_form()

elif menu == "Register Stores":
    st.title("🏪 Register Stores Locations")
    render_store_form()

elif menu == "Add Deliveries":
    st.title("📦 Goods Delivery Input")
    render_delivery_form()

elif menu == "Set Availability":
    st.title("✅ Mark Available People")
    render_availability_form()

elif menu == "Generate Plan":
    st.title("🗕️ Generate Assignment Plan")

    #     # 📨 Sender Input
    # with st.expander("✉️ Email Sender Configuration"):
    #     sender_email = st.text_input("Sender Gmail Address", value=st.session_state.get("sender_email", "reza761co@gmail.com"))
    #     sender_password = st.text_input("App Password", type="password", value=st.session_state.get("sender_password", ""), help="Use your Gmail App Password")
    #     st.session_state.sender_email = sender_email
    #     st.session_state.sender_password = sender_password

    # Build name-to-id mapping
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM people")
    name_to_id = {name: person_id for person_id, name in cursor.fetchall()}
    conn.close()

    # Step 1: Button to trigger assignment generation
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

            # Save assignments to DB
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM visit_plan")
            conn.commit()
            for row in st.session_state.visit_plan:
                store = row["store"]
                visit_date = row["date"]

                leader_id = name_to_id.get(row["leader"])
                if leader_id:
                    cursor.execute("""
                        INSERT INTO visit_plan (person_id, store_name, visit_date)
                        VALUES (?, ?, ?)
                    """, (leader_id, store, visit_date))

                for member_name in row["members"]:
                    member_id = name_to_id.get(member_name)
                    if member_id:
                        cursor.execute("""
                            INSERT INTO visit_plan (person_id, store_name, visit_date)
                            VALUES (?, ?, ?)
                        """, (member_id, store, visit_date))

            conn.commit()
            conn.close()

            # ✅ Assignment plan generated
            st.session_state.assignment_generated = True

    # Step 2: Show email option *after* generating the plan
    if st.session_state.get("assignment_generated", False):
        send_email_now = st.radio(
            "📧 Do you want to send assignment emails now?",
            ["Yes", "No"], index=1, horizontal=True,
            key="email_decision"
        )

        if st.button("Confirm Email Decision"):
            if send_email_now == "Yes":
                send_assignment_emails(
                    st.secrets["sender_email"],
                    st.secrets["app_password"]
                )
                st.success("✅ Plan created and emails sent!")
            else:
                st.success("✅ Plan created. Emails were not sent.")
            # Reset trigger
            del st.session_state["assignment_generated"]
            del st.session_state["email_decision"]



elif menu == "Distance Details":
    st.title("📏 Distance from Home to the chosen Store (km)")

    if "visit_plan_details" in st.session_state:
        df = pd.DataFrame(st.session_state.visit_plan_details)
        df = df.apply(lambda col: col.map(lambda x: round(x) if isinstance(x, (int, float)) else x))
        styled_df = df.style.set_properties(**{
            'white-space': 'normal',
            'text-align': 'left',
            'font-size': '14px'
        })
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No distance information available yet.")

elif menu == "Visit History":
    st.title("📜 Visit History")
    render_visit_log()

    st.markdown("---")
    st.subheader("✅ Assignment Read Confirmations")

    show_confirmations = st.checkbox("Show who confirmed their assignments")

    if show_confirmations:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT rc.visit_date, p.name, p.role, rc.store_name
            FROM read_confirmations rc
            JOIN people p ON rc.person_id = p.id
            ORDER BY rc.visit_date DESC
        """)
        confirmations = cursor.fetchall()
        conn.close()

        if confirmations:
            df = pd.DataFrame(confirmations, columns=["Date", "Name", "Role", "Store"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ No one has confirmed their assignment yet.")


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
                    cursor.execute("DROP TABLE IF EXISTS visit_plan")
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
                st.rerun()

            except Exception as e:
                st.error(f"Error resetting database: {e}")

# -------------------------------
# 🟠 JSON Backup (optional)
# -------------------------------
today = today_str()

if "people" not in st.session_state:
    st.session_state.people = load_from_json("people.json")