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
import sqlite3
import requests
from streamlit_folium import st_folium
import folium

def render_people_form():
    st.header("🧑‍💼 Register People (Leader / Member)")

    with st.form("add_person_form"):
        name = st.text_input("Full Name")
        role = st.selectbox("Role", ["leader", "member"])

        st.markdown("### 🔎 Search Address (optional)")

        address = st.text_input("Enter an address to search:")

        search_lat = None
        search_lon = None

        if st.form_submit_button("Search Address"):
            if address:
                url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
                try:
                    headers = {"User-Agent": "MySSAApp/1.0 (your_email@example.com)"}
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200 and response.text:
                        response_json = response.json()

                        if response_json:
                            search_lat = float(response_json[0]["lat"])
                            search_lon = float(response_json[0]["lon"])
                            st.success(f"📍 Found: Latitude {search_lat:.6f}, Longitude {search_lon:.6f}")

                            # 🔥 Save to session
                            st.session_state.search_lat = search_lat
                            st.session_state.search_lon = search_lon

                        else:
                            st.error("Address not found. Try another address.")
                    else:
                        st.error("Failed to fetch data. Server returned empty or error.")

                except Exception as e:
                    st.error(f"Failed to get location. {e}")

        st.markdown("### 📍 Select Location on the Map")

        if search_lat is not None and search_lon is not None:
            m = folium.Map(location=[search_lat, search_lon], zoom_start=14)
        else:
            m = folium.Map(location=[-27.4705, 153.0260], zoom_start=10)  # default Brisbane

        m.add_child(folium.LatLngPopup())
        output = st_folium(m, width=700, height=500)

        lat = None
        lon = None

        if output and output.get("last_clicked"):
            lat = output["last_clicked"]["lat"]
            lon = output["last_clicked"]["lng"]
            st.success(f"📍 Selected by click: Latitude {lat:.6f}, Longitude {lon:.6f}")

        submitted = st.form_submit_button("Add Person")

        if submitted:
            final_lat = lat if lat is not None else st.session_state.get("search_lat", None)
            final_lon = lon if lon is not None else st.session_state.get("search_lon", None)

            if not name or final_lat is None or final_lon is None:
                st.error("Please fill all fields and select location!")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO people (name, role, latitude, longitude)
                    VALUES (?, ?, ?, ?)
                """, (name, role, final_lat, final_lon))
                conn.commit()
                conn.close()
                st.success(f"✅ {name} ({role}) added successfully!")

    # 🧾 Display saved people from the DB
    st.subheader("Saved People")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, role, latitude, longitude FROM people")
    people = cursor.fetchall()
    conn.close()

    if people:
        st.markdown("### 👤 People List with Delete Button")

        # Prepare table data
        people_table = []
        for person in people:
            people_table.append({
                "Name": person[0],
                "Role": person[1],
                "Latitude": round(person[2], 6),
                "Longitude": round(person[3], 6),
                "Delete": False,  # 🔥 New column for delete checkbox
            })

        # Show data editor
        edited_people = st.data_editor(
            people_table,
            hide_index=True,
            column_config={
                "Delete": st.column_config.CheckboxColumn("Delete", default=False)
            }
        )

        # 🔥 If any Delete checkbox is checked, delete that person
        for person in edited_people:
            if person["Delete"]:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM people WHERE name = ?", (person["Name"],))
                conn.commit()
                conn.close()
                st.success(f"✅ Deleted {person['Name']}")
                st.rerun()

    else:
        st.info("No people registered yet.")
