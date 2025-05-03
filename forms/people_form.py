# import streamlit as st
# from data.db import get_connection
# import sqlite3
# import requests
# from streamlit_folium import st_folium
# import folium

# def render_people_form():

#     with st.form("add_person_form"):
#         name = st.text_input("Enter Member's Name")
#         role = st.selectbox("Role", ["leader", "member"])

#         st.markdown("### 🔎 Search Address (or choose from the Map bellow)")

#         address = st.text_input("Enter an address to search:")

#         search_lat = None
#         search_lon = None

#         if st.form_submit_button("Search Address"):
#             if address:
#                 url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
#                 try:
#                     headers = {"User-Agent": "MySSAApp/1.0 (your_email@example.com)"}
#                     response = requests.get(url, headers=headers)

#                     if response.status_code == 200 and response.text:
#                         response_json = response.json()

#                         if response_json:
#                             search_lat = float(response_json[0]["lat"])
#                             search_lon = float(response_json[0]["lon"])
#                             st.success(f"📍 Found: Latitude {search_lat:.6f}, Longitude {search_lon:.6f}")

#                             # 🔥 Save to session
#                             st.session_state.search_lat = search_lat
#                             st.session_state.search_lon = search_lon

#                         else:
#                             st.error("Address not found. Try another address.")
#                     else:
#                         st.error("Failed to fetch data. Server returned empty or error.")

#                 except Exception as e:
#                     st.error(f"Failed to get location. {e}")

#         st.markdown("### 📍 Select Location on the Map")

#         if search_lat is not None and search_lon is not None:
#             m = folium.Map(location=[search_lat, search_lon], zoom_start=14)
#         else:
#             m = folium.Map(location=[-27.4705, 153.0260], zoom_start=10)  # default Brisbane

#         m.add_child(folium.LatLngPopup())
#         output = st_folium(m, width=700, height=500)

#         lat = None
#         lon = None

#         if output and output.get("last_clicked"):
#             lat = output["last_clicked"]["lat"]
#             lon = output["last_clicked"]["lng"]
#             st.success(f"📍 Selected by click: Latitude {lat:.6f}, Longitude {lon:.6f}")

#         submitted = st.form_submit_button("Add Person")

#         if submitted:
#             final_lat = lat if lat is not None else st.session_state.get("search_lat", None)
#             final_lon = lon if lon is not None else st.session_state.get("search_lon", None)

#             if not name or final_lat is None or final_lon is None:
#                 st.error("Please fill all fields and select location!")
#             else:
#                 conn = get_connection()
#                 cursor = conn.cursor()
#                 cursor.execute("""
#                     INSERT INTO people (name, role, latitude, longitude)
#                     VALUES (?, ?, ?, ?)
#                 """, (name, role, final_lat, final_lon))
#                 conn.commit()
#                 conn.close()
#                 st.success(f"✅ {name} ({role}) added successfully!")

#     # 🧾 Display saved people from the DB
#     st.subheader("Saved People")
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT name, role, latitude, longitude FROM people")
#     people = cursor.fetchall()
#     conn.close()

#     if people:
#         st.markdown("### 👤 People List")

#         # Prepare table data (Latitude/Longitude removed from UI table, but kept separately)
#         people_table = []
#         people_with_coords = []  # This stores full data for internal use

#         for person in people:
#             people_table.append({
#                 "Name": person[0],
#                 "Role": person[1],
#                 "Delete": False,
#             })
#             people_with_coords.append({
#                 "Name": person[0],
#                 "Role": person[1],
#                 "Latitude": person[2],
#                 "Longitude": person[3],
#             })


#         # Show data editor
#         edited_people = st.data_editor(
#             people_table,
#             hide_index=True,
#             column_config={
#                 "Delete": st.column_config.CheckboxColumn(
#                     label="Delete Button",  # This removes the header text
#                     default=False
#                 )
#             },
#         )

#         # 🔥 If any Delete checkbox is checked, delete that person
#         for person in edited_people:
#             if person["Delete"]:
#                 conn = get_connection()
#                 cursor = conn.cursor()
#                 cursor.execute("DELETE FROM people WHERE name = ?", (person["Name"],))
#                 conn.commit()
#                 conn.close()
#                 st.success(f"✅ Deleted {person['Name']}")
#                 st.rerun()

#     else:
#         st.info("No people registered yet.")










import streamlit as st
from data.db import get_connection
import sqlite3
import requests
from streamlit_folium import st_folium
import folium

def render_people_form():
    with st.form("add_person_form", clear_on_submit=True):
        # Personal Information
        name = st.text_input("Enter Member's Name")
        role = st.selectbox("Role", ["leader", "member"])

        # Address Search Section
        st.markdown("### 🔎 Search Address")
        address = st.text_input("Enter an address to search:", key="address_search")

        # Create columns for buttons
        col1, col2 = st.columns([2, 1])
        with col1:
            search_clicked = st.form_submit_button(
                "🔍 Search Address",
                help="Search for coordinates using an address",
                type="secondary"
            )
        
        # Map Section
        st.markdown("### 📍 Select Location on the Map")
        
        # Initialize map with either searched location or Brisbane default
        if "search_lat" in st.session_state and "search_lon" in st.session_state:
            m = folium.Map(
                location=[st.session_state.search_lat, st.session_state.search_lon],
                zoom_start=14
            )
        else:
            m = folium.Map(location=[-27.4705, 153.0260], zoom_start=10)  # Brisbane default

        m.add_child(folium.LatLngPopup())
        output = st_folium(m, width=700, height=500)

        # Handle Address Search
        if search_clicked and address:
            try:
                url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
                headers = {"User-Agent": "MySSAApp/1.0 (contact@example.com)"}
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    results = response.json()
                    if results:
                        st.session_state.search_lat = float(results[0]["lat"])
                        st.session_state.search_lon = float(results[0]["lon"])
                        st.success("📍 Address found! Zoom to location on map.")
                    else:
                        st.error("Address not found. Please try another search.")
                else:
                    st.error("Failed to retrieve coordinates. Please try again.")
            except Exception as e:
                st.error(f"Search error: {str(e)}")

        # Handle Map Selection
        lat = None
        lon = None
        if output and output.get("last_clicked"):
            lat = output["last_clicked"]["lat"]
            lon = output["last_clicked"]["lng"]
            st.success(f"📍 Selected: Latitude {lat:.6f}, Longitude {lon:.6f}")

        # Add Person Button
        with col2:
            add_clicked = st.form_submit_button(
                "➕ Add Person",
                help="Add this person to the database",
                type="primary"
            )

        # Form Submission Handling
        if add_clicked:
            final_lat = lat or st.session_state.get("search_lat")
            final_lon = lon or st.session_state.get("search_lon")

            if not name or not final_lat or not final_lon:
                st.error("❌ Please complete all fields and select a location!")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO people (name, role, latitude, longitude)
                        VALUES (?, ?, ?, ?)
                    """, (name, role, final_lat, final_lon))
                    conn.commit()
                    st.success(f"✅ {name} ({role}) added successfully!")
                    # Clear search session state after successful addition
                    if "search_lat" in st.session_state:
                        del st.session_state.search_lat
                    if "search_lon" in st.session_state:
                        del st.session_state.search_lon
                except sqlite3.Error as e:
                    st.error(f"Database error: {str(e)}")
                finally:
                    if conn:
                        conn.close()

    # Display Existing Entries
    st.markdown("---")
    st.subheader("Registered People")
    
    conn = get_connection()
    try:
        people = conn.execute("""
            SELECT name, role, latitude, longitude 
            FROM people
            ORDER BY role DESC, name ASC
        """).fetchall()
    except sqlite3.Error as e:
        st.error(f"Error loading people: {str(e)}")
        people = []
    finally:
        conn.close()

    if people:
        # Create editable table with delete functionality
        people_data = [
            {
                "Name": p[0],
                "Role": p[1],
                "Coordinates": f"{p[2]:.4f}, {p[3]:.4f}",
                "Delete": False
            } 
            for p in people
        ]

        edited_people = st.data_editor(
            people_data,
            column_config={
                "Delete": st.column_config.CheckboxColumn(
                    "Delete",
                    help="Select to delete this entry",
                    default=False
                )
            },
            hide_index=True,
            use_container_width=True
        )

        # Process deletions
        for entry in edited_people:
            if entry["Delete"]:
                try:
                    conn = get_connection()
                    conn.execute("DELETE FROM people WHERE name = ?", (entry["Name"],))
                    conn.commit()
                    st.success(f"🗑️ Deleted {entry['Name']}")
                    st.rerun()
                except sqlite3.Error as e:
                    st.error(f"Delete error: {str(e)}")
                finally:
                    if conn:
                        conn.close()
    else:
        st.info("No people registered yet. Add your first member above!")