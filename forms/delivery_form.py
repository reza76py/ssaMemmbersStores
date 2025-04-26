import streamlit as st
from datetime import date

def render_delivery_form():
    st.subheader("Enter Delivered Goods Value")

    if "stores" in st.session_state and len(st.session_state.stores) > 0:
        store_names = [store["name"] for store in st.session_state.stores]

        with st.form("delivery_form"):
            selected_store = st.selectbox("Select Store", store_names)
            goods_value = st.number_input("Goods Value ($)", min_value=0.0, step=100.0)
            delivery_submitted = st.form_submit_button("Save Delivery Info")

            if delivery_submitted:
                if "deliveries" not in st.session_state:
                    st.session_state.deliveries = []

                st.session_state.deliveries.append({
                    "store": selected_store,
                    "goods_value": goods_value,
                    "date": str(date.today())
                })
                st.success(f"Delivery recorded for {selected_store} (${goods_value:.2f})")

        # Display all deliveries for today
        st.subheader("Today's Deliveries")
        today = str(date.today())
        today_deliveries = [
            d for d in st.session_state.get("deliveries", []) if d["date"] == today
        ]

        if today_deliveries:
            st.table(today_deliveries)
        else:
            st.info("No deliveries recorded yet today.")
    else:
        st.warning("⚠️ Please add at least one store before entering deliveries.")
