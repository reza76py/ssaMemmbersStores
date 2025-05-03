import streamlit as st
from datetime import date
from data.db import get_connection
import pandas as pd

def render_delivery_form():

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
        goods_value = int(st.number_input("Goods Value ($)", min_value=0.0, step=100.0))
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
            st.success(f"Delivery recorded for {selected_store_name} (${int(goods_value)})")
    # Show today's deliveries
    st.subheader("Deliveries Value")
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
        # st.table([
        #     {"Store": d[0], "Goods Value": f"$ {int(d[1]):,}", "Date": d[2]} for d in deliveries_today
        # Build the table
        table_data = [
            {"Store": d[0], "Goods Value": f"$ {int(d[1]):,}", "Date": d[2]}
            for d in deliveries_today
        ]
        df = pd.DataFrame(table_data)

        # Show the table without index
        st.dataframe(df, use_container_width=True, hide_index=True)



        
    else:
        st.info("No deliveries recorded yet today.")
