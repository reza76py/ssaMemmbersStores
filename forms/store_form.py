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
from data.db import get_connection

def render_store_form():
    st.subheader("Add Store")

    with st.form("add_store_form"):
        store_name = st.text_input("Store Name")
        lat = st.number_input("Store Latitude", format="%.6f", key="store_lat")
        lng = st.number_input("Store Longitude", format="%.6f", key="store_lng")
        submitted = st.form_submit_button("Add Store")

        if submitted:
            if store_name.strip() == "":
                st.warning("Store name cannot be empty.")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO stores (name, latitude, longitude) VALUES (?, ?, ?)",
                    (store_name, lat, lng)
                )
                conn.commit()
                conn.close()
                st.success(f"Store '{store_name}' added!")

    # 📋 Display saved stores from DB
    st.subheader("Saved Stores")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, latitude, longitude FROM stores")
    stores = cursor.fetchall()
    conn.close()

    if stores:
        st.table([{"Name": s[0], "Lat": s[1], "Lng": s[2]} for s in stores])
    else:
        st.info("No stores registered yet.")
