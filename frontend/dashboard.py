import streamlit as st
import folium
from streamlit_folium import st_folium
import requests # To communicate with your FastAPI backend


RECENT_ANALYSES_URL = "http://localhost:8000/api/v1/analysis/recent?limit=5"


def fetch_recent_analyses():
    try:
        response = requests.get(RECENT_ANALYSES_URL, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return []
    return []

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
    recent_runs = fetch_recent_analyses()

    if recent_runs:
        latest = recent_runs[0]
        health_index = max(0, 100 - latest.get("change_percentage", 0))
        st.metric(
            label="Overall Health Index",
            value=f"{health_index:.1f}/100",
            delta=f"-{latest.get('change_percentage', 0):.2f}%",
        )
    else:
        st.metric(label="Overall Health Index", value="N/A", delta="No data")
    
    st.subheader("Alert Timeline")
    if recent_runs:
        for run in recent_runs:
            ts = run.get("created_at", "")[:19].replace("T", " ")
            risk = run.get("risk_level", "N/A")
            pct = run.get("change_percentage", 0)
            coords = f"({run.get('latitude'):.3f}, {run.get('longitude'):.3f})"
            message = f"{ts}: {pct:.2f}% change at {coords}."
            if risk == "Red":
                st.error(f"🔴 {message}")
            elif risk == "Yellow":
                st.warning(f"🟡 {message}")
            else:
                st.success(f"🟢 {message}")
    else:
        st.info("No recent analysis runs available yet.")

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
BACKEND_URL = "http://localhost:8000/api/v1/analyze-region"

if st.button("Run AI Change Detection Analysis"):
    with st.spinner("Analyzing multi-temporal satellite data..."):
        payload = {
            "latitude": target_lat,
            "longitude": target_lon,
            "time_t1": str(date_t1),
            "time_t2": str(date_t2),
        }
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                st.success("Analysis Complete! Risk scoring updated.")
                st.subheader("Analysis Results")
                risk = result.get("risk_assessment", {})
                st.metric(
                    label="Change Detected",
                    value=f"{result.get('change_percentage', 0):.2f}%",
                )
                st.metric(
                    label="Risk Level",
                    value=f"{risk.get('indicator', '')} {risk.get('risk_level', 'N/A')}",
                )
                st.info(f"Recommended Action: **{risk.get('action', 'N/A')}**")
            else:
                st.error(f"Backend returned error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend. Make sure the FastAPI server is running on http://localhost:8000")
        except Exception as e:
            st.error(f"An error occurred: {e}")