import streamlit as st

def render_home_view():
    st.title("Bunnings SSA Team & Store Assignment Tool")

    st.markdown("""
    This App is Temporary and will be removed from page.

    ---


     ### 📌 What This App Does
    - Assigns **Leaders and Members** to stores using an intelligent logic.
    - Ensures every leader has at least 1 member (up to 3 based on delivery size).
    - Uses **location distance** and **delivery value** to prioritize assignments.
    - Records visit plans and allows future review.
    - Supports **manual override** and **database reset**.

    ### 🧭 How to Use It

    1. **Register People** – Add leaders and members with their coordinates.
    2. **Register Stores** – Input store names and coordinates.
    3. **Add Deliveries** – Enter today’s goods values per store.
    4. **Set Availability** – Mark who is available for today’s tasks.
    5. **Generate Plan** – Create assignment plans based on the above inputs.
    6. **Distance Details** – View detailed distance calculations for each plan.
    7. **Visit History** – Save finalized plans to your visit log.
    8. **Reset Database** – ⚠️ Delete all data and start over if needed.
    9. *(Optional)* Use “Save People Data (JSON)” to back up your people list.

    ---
  
    """)