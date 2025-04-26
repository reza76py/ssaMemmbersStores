import streamlit as st

def render_store_form():
    st.subheader("Add Store")

    with st.form("add_store_form"):
        store_name = st.text_input("Store Name")
        lat = st.number_input("Store Latitude", format="%.1f", key="store_lat")
        lng = st.number_input("Store Longitude", format="%.1f", key="store_lng")
        submitted = st.form_submit_button("Add Store")

        if submitted:
            if "stores" not in st.session_state:
                st.session_state.stores = []
            st.session_state.stores.append({
                "name": store_name,
                "latitude": lat,
                "longitude": lng
            })
            st.success(f"Store '{store_name}' added!")

    if "stores" in st.session_state and len(st.session_state.stores) > 0:
        st.subheader("Saved Stores")
        st.table(st.session_state.stores)
    else:
        st.info("No stores registered yet.")
