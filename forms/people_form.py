# import streamlit as st

# def render_people_form():
#     st.subheader("Add Person")

#     with st.form("add_person_form"):
#         name = st.text_input("Full Name")
#         role = st.selectbox("Role", ["leader", "member"])
#         lat = st.number_input("Latitude", format="%.6f")
#         lng = st.number_input("Longitude", format="%.6f")
#         submitted = st.form_submit_button("Add Person")

#         if submitted:
#             if "people" not in st.session_state:
#                 st.session_state.people = []
#             st.session_state.people.append({
#                 "name": name, "role": role, "latitude": lat, "longitude": lng
#             })
#             st.success(f"{role.capitalize()} '{name}' added!")

#     if "people" in st.session_state:
#         st.subheader("Saved People")
#         st.table(st.session_state.people)









# with db_connection:
import streamlit as st
from data.db import get_connection

def render_people_form():
    st.subheader("Add Person")

    with st.form("add_person_form"):
        name = st.text_input("Full Name")
        role = st.selectbox("Role", ["leader", "member"])
        lat = st.number_input("Latitude", format="%.6f")
        lng = st.number_input("Longitude", format="%.6f")
        submitted = st.form_submit_button("Add Person")

        if submitted:
            if name.strip() == "":
                st.warning("Name cannot be empty.")
            else:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO people (name, role, latitude, longitude) VALUES (?, ?, ?, ?)",
                    (name, role, lat, lng)
                )
                conn.commit()
                conn.close()
                st.success(f"{role.capitalize()} '{name}' added!")

    # 🧾 Display saved people from the DB
    st.subheader("Saved People")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, role, latitude, longitude FROM people")
    people = cursor.fetchall()
    conn.close()

    if people:
        st.table([{"Name": p[0], "Role": p[1], "Lat": p[2], "Lng": p[3]} for p in people])
    else:
        st.info("No people registered yet.")
