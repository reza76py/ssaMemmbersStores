import streamlit as st
from streamlit_folium import st_folium
import folium

st.title("Select Location on the Map")

# Create a folium map centered somewhere (e.g., Brisbane)
m = folium.Map(location=[-27.4705, 153.0260], zoom_start=10)

# Add click functionality
m.add_child(folium.LatLngPopup())

# Display the map in Streamlit
output = st_folium(m, width=700, height=500)

# Display clicked location
if output and output.get("last_clicked"):
    lat = output["last_clicked"]["lat"]
    lng = output["last_clicked"]["lng"]
    st.success(f"You clicked at Latitude: {lat:.6f}, Longitude: {lng:.6f}")
