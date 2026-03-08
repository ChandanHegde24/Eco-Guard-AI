import streamlit as st
import folium
from streamlit_folium import st_folium
import requests # To communicate with your FastAPI backend

# --- Page Configuration ---
st.set_page_config(page_title="Eco-Guard AI Dashboard", layout="wide")
st.title("🌍 Eco-Guard AI: Environmental Monitoring")
st.markdown("Continuous, AI-powered multi-temporal satellite analysis.")

# --- Sidebar Controls ---
st.sidebar.header("Monitoring Parameters")
target_lat = st.sidebar.number_input("Latitude", value=14.5)
target_lon = st.sidebar.number_input("Longitude", value=75.5)
date_t1 = st.sidebar.date_input("Time T1 (Baseline)")
date_t2 = st.sidebar.date_input("Time T2 (Current)")

st.sidebar.markdown("---")
st.sidebar.markdown("**Project Lead:** Chandan Hegde")
st.sidebar.markdown("**System Status:** 🟢 Online")

# --- Main Dashboard Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Interactive Map View & Risk Heatmap")
    # Initialize a Folium map centered on the target coordinates
    m = folium.Map(location=[target_lat, target_lon], zoom_start=12)
    
    # In a fully integrated app, you would overlay your GeoPandas risk heatmap here
    folium.Circle(
        radius=5000,
        location=[target_lat, target_lon],
        color="red",
        fill=True,
        fill_color="red"
    ).add_to(m)
    
    # Render the map in Streamlit
    st_folium(m, width=700, height=500)

with col2:
    st.subheader("Region-wise Sustainability Score")
    # Placeholder for the data fetched from the FastAPI backend
    st.metric(label="Overall Health Index", value="82/100", delta="-3.4%")
    
    st.subheader("Alert Timeline")
    st.error("🔴 2026-03-01: 18% deforestation detected in Zone A.")
    st.warning("🟡 2026-02-15: 8% water body shrinkage in Zone B.")
    st.success("🟢 2026-01-10: Stable vegetation in Zone C.")

st.markdown("---")

# --- Before/After Comparison ---
st.subheader("Multi-Temporal Analysis: Before/After Image Comparison")
# Streamlit has a great ecosystem; you can use community components like 'streamlit-image-comparison'
col_img1, col_img2 = st.columns(2)
with col_img1:
    st.image("https://via.placeholder.com/600x400.png?text=Satellite+Image+T1", caption="Time T1")
with col_img2:
    st.image("https://via.placeholder.com/600x400.png?text=Satellite+Image+T2", caption="Time T2")

# --- Action Button ---
if st.button("Run AI Change Detection Analysis"):
    with st.spinner("Analyzing multi-temporal satellite data..."):
        # Here you would use requests.post() to send data to your FastAPI endpoint
        # e.g., response = requests.post("http://localhost:8000/api/v1/analyze-region", json={...})
        st.success("Analysis Complete! Risk scoring updated.")