# import streamlit as st
# from datetime import date

# def render_delivery_form():
#     st.subheader("Enter Delivered Goods Value")

#     if "stores" in st.session_state and len(st.session_state.stores) > 0:
#         store_names = [store["name"] for store in st.session_state.stores]

#         with st.form("delivery_form"):
#             selected_store = st.selectbox("Select Store", store_names)
#             goods_value = st.number_input("Goods Value ($)", min_value=0.0, step=100.0)
#             delivery_submitted = st.form_submit_button("Save Delivery Info")

#             if delivery_submitted:
#                 if "deliveries" not in st.session_state:
#                     st.session_state.deliveries = []

#                 st.session_state.deliveries.append({
#                     "store": selected_store,
#                     "goods_value": goods_value,
#                     "date": str(date.today())
#                 })
#                 st.success(f"Delivery recorded for {selected_store} (${goods_value:.2f})")

#         # Display all deliveries for today
#         st.subheader("Today's Deliveries")
#         today = str(date.today())
#         today_deliveries = [
#             d for d in st.session_state.get("deliveries", []) if d["date"] == today
#         ]

#         if today_deliveries:
#             st.table(today_deliveries)
#         else:
#             st.info("No deliveries recorded yet today.")
#     else:
#         st.warning("⚠️ Please add at least one store before entering deliveries.")













import streamlit as st
from datetime import date
from data.db import get_connection

def render_delivery_form():
    st.subheader("Enter Delivered Goods Value")

    # Load stores from database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM stores")
    stores = cursor.fetchall()
    conn.close()

    if not stores:
        st.warning("⚠️ Please register at least one store before entering deliveries.")
        return

    store_names = [s[1] for s in stores]
    store_id_map = {s[1]: s[0] for s in stores}

    # Form to enter goods
    with st.form("delivery_form"):
        selected_store_name = st.selectbox("Select Store", store_names)
        goods_value = st.number_input("Goods Value ($)", min_value=0.0, step=100.0)
        submitted = st.form_submit_button("Save Delivery Info")

        if submitted:
            store_id = store_id_map[selected_store_name]
            today = str(date.today())

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO deliveries (store_id, goods_value, date) VALUES (?, ?, ?)",
                (store_id, goods_value, today)
            )
            conn.commit()
            conn.close()
            st.success(f"Delivery recorded for {selected_store_name} (${goods_value:.2f})")

    # Show today's deliveries
    st.subheader("Today's Deliveries")
    today = str(date.today())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, d.goods_value, d.date
        FROM deliveries d
        JOIN stores s ON d.store_id = s.id
        WHERE d.date = ?
    """, (today,))
    deliveries_today = cursor.fetchall()
    conn.close()

    if deliveries_today:
        st.table([
            {"Store": d[0], "Goods Value": d[1], "Date": d[2]} for d in deliveries_today
        ])
    else:
        st.info("No deliveries recorded yet today.")
