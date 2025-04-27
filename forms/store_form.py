# import streamlit as st

# def render_store_form():
#     st.subheader("Add Store")

#     with st.form("add_store_form"):
#         store_name = st.text_input("Store Name")
#         lat = st.number_input("Store Latitude", format="%.1f", key="store_lat")
#         lng = st.number_input("Store Longitude", format="%.1f", key="store_lng")
#         submitted = st.form_submit_button("Add Store")

#         if submitted:
#             if "stores" not in st.session_state:
#                 st.session_state.stores = []
#             st.session_state.stores.append({
#                 "name": store_name,
#                 "latitude": lat,
#                 "longitude": lng
#             })
#             st.success(f"Store '{store_name}' added!")

#     if "stores" in st.session_state and len(st.session_state.stores) > 0:
#         st.subheader("Saved Stores")
#         st.table(st.session_state.stores)
#     else:
#         st.info("No stores registered yet.")







# with db_connection:
import streamlit as st
import sqlite3
import requests
from streamlit_folium import st_folium
import folium
from data.db import get_connection

def render_store_form():
    st.header("🏬 Register Store Location")

    with st.form("add_store_form"):
        store_name = st.text_input("Store Name")

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
                            st.session_state.search_lat_store = search_lat
                            st.session_state.search_lon_store = search_lon

                        else:
                            st.error("Address not found. Try another address.")
                    else:
                        st.error("Failed to fetch data. Server returned empty or error.")

                except Exception as e:
                    st.error(f"Failed to get location. {e}")

        st.markdown("### 📍 Select Location on the Map")

        # Show map centered on searched address if available
        if "search_lat_store" in st.session_state and "search_lon_store" in st.session_state:
            m = folium.Map(location=[st.session_state.search_lat_store, st.session_state.search_lon_store], zoom_start=14)
        else:
            m = folium.Map(location=[-27.4705, 153.0260], zoom_start=10)  # Default Brisbane center

        m.add_child(folium.LatLngPopup())
        output = st_folium(m, width=700, height=500, key="store_map")


        lat = None
        lon = None

        if output and output.get("last_clicked"):
            lat = output["last_clicked"]["lat"]
            lon = output["last_clicked"]["lng"]
            st.success(f"📍 Selected by click: Latitude {lat:.6f}, Longitude {lon:.6f}")

        submitted = st.form_submit_button("Add Store")

        if submitted:
            final_lat = lat if lat is not None else st.session_state.get("search_lat_store", None)
            final_lon = lon if lon is not None else st.session_state.get("search_lon_store", None)

            if not store_name or final_lat is None or final_lon is None:
                st.error("Please fill all fields and select location!")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO stores (name, latitude, longitude)
                    VALUES (?, ?, ?)
                """, (store_name, final_lat, final_lon))
                conn.commit()
                conn.close()
                st.success(f"✅ {store_name} added successfully!")

    # 🟡 After form: Show current list of stores
    st.markdown("### 📋 Current Saved Stores:")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, latitude, longitude FROM stores")
    stores = cursor.fetchall()
    conn.close()

    if stores:
        st.table(stores)
    else:
        st.info("No stores registered yet.")
