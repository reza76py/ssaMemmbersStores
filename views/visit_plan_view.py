import streamlit as st

def render_visit_plan():
    if "visit_plan" in st.session_state and st.session_state.visit_plan:
        st.subheader("📅 Visit Plan (Next 3 Days)")
        st.table(st.session_state.visit_plan)
    else:
        st.info("No assignment plan generated yet.")
