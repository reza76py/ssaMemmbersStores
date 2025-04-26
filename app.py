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
from data.db import initialize_database

with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


with st.expander("🧑‍💼 Register People (Leader / Member)"):
    render_people_form()


with st.expander("🏬 Register Store Locations"):
    render_store_form()

with st.expander("📦 Goods Delivery Input"):
    render_delivery_form()

with st.expander("✅ Mark Available People"):
    render_availability_form()


if st.button("Generate Assignment Plan"):
    if all(k in st.session_state for k in ["people", "stores", "deliveries", "availability"]):
        st.session_state.visit_plan = generate_assignments(
            st.session_state.stores,
            [d for d in st.session_state.deliveries if d["date"] == str(date.today())],
            st.session_state.availability,
            st.session_state.people
        )
        st.success("✅ Plan created!")

        if st.session_state.visit_plan:
            st.subheader("📅 Visit Plan (Next 3 Days)")
            st.table(st.session_state.visit_plan)
    else:
        st.error("Missing data: make sure all forms are filled.")



if "stores" in st.session_state and "visit_log" in st.session_state:
    priority_data = calculate_store_priorities(
        st.session_state.stores,
        st.session_state.visit_log
    )
    st.table(priority_data)
else:
    st.info("No stores or visit logs to analyze yet.")



# Assignment output (Section 4)
with st.expander("📅 Generated Visit Plan"):
    render_visit_plan()

# Visit history (Section 5)
with st.expander("📜 Visit History"):
    render_visit_log()





today = today_str()

if "people" not in st.session_state:
    st.session_state.people = load_from_json("people.json")

if st.button("Save Data"):
    save_to_json("people.json", st.session_state.people)
    st.success("Data saved to file!")


initialize_database()