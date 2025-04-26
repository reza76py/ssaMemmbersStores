import streamlit as st

def render_visit_log():
    st.subheader("📜 Past Visit Logs")

    # Save button
    if "visit_plan" in st.session_state and st.session_state.visit_plan:
        if st.button("✅ Finalize & Save Current Plan to History"):
            if "visit_log" not in st.session_state:
                st.session_state.visit_log = []

            for item in st.session_state.visit_plan:
                st.session_state.visit_log.append({
                    "date": item["date"],
                    "store": item["store"],
                    "leader": item["leader"],
                    "members": ", ".join(item["members"])
                })

            st.success("Visit plan saved to history ✅")
            st.session_state.visit_plan = []

    # Show the visit log
    if "visit_log" in st.session_state and st.session_state.visit_log:
        st.table(st.session_state.visit_log)
    else:
        st.info("No visits have been logged yet.")
