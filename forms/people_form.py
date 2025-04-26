import streamlit as st

def render_people_form():
    st.subheader("Add Person")

    with st.form("add_person_form"):
        name = st.text_input("Full Name")
        role = st.selectbox("Role", ["leader", "member"])
        lat = st.number_input("Latitude", format="%.1f")
        lng = st.number_input("Longitude", format="%.1f")
        submitted = st.form_submit_button("Add Person")

        if submitted:
            if "people" not in st.session_state:
                st.session_state.people = []
            st.session_state.people.append({
                "name": name,
                "role": role,
                "latitude": lat,
                "longitude": lng
            })
            st.success(f"{role.capitalize()} '{name}' added!")

    if "people" in st.session_state and len(st.session_state.people) > 0:
        st.subheader("Saved People")
        st.table(st.session_state.people)
    else:
        st.info("No people registered yet.")
