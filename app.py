# app.py
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap  # folium backend (leafmap also supports maplibre)
from pathlib import Path

st.set_page_config(layout="wide")
st.title("Riverside, CA — Zones Viewer")

# Path to your file (change if needed)
geojson_path = r"D:\python\webapp_zones\datasets\ca_riverside.geojson"
geojson_file = Path(geojson_path)

if not geojson_file.exists():
    st.error(f"GeoJSON file not found: {geojson_path}")
    st.stop()

# Load GeoJSON with GeoPandas
@st.cache_data(ttl=3600)
def load_gdf(path):
    gdf = gpd.read_file(path)
    # Ensure geometry is valid and has a crs
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326, allow_override=True)
    else:
        gdf = gdf.to_crs(epsg=4326)
    return gdf

gdf = load_gdf(str(geojson_file))
st.write(f"Features: {len(gdf)} — CRS: {gdf.crs}")

# Sidebar filter
st.sidebar.header("Filter zones")
# Guard for field names — adjust if your field names differ
zone_code_field = "zone_code"
zone_name_field = "zone__name"  # you wrote zone__name in first message; adjust if it's zone_name

available_zone_codes = ["All"] + sorted(gdf[zone_code_field].dropna().unique().tolist())
selected_code = st.sidebar.selectbox("Select zone_code", available_zone_codes)

available_zone_names = ["All"] + sorted(gdf[zone_name_field].dropna().unique().tolist()) if zone_name_field in gdf.columns else None
selected_name = None
if available_zone_names:
    selected_name = st.sidebar.selectbox("Select zone_name", available_zone_names)

# Apply filters
filtered = gdf
if selected_code and selected_code != "All":
    filtered = filtered[filtered[zone_code_field] == selected_code]
if selected_name and selected_name != "All":
    filtered = filtered[filtered[zone_name_field] == selected_name]

st.sidebar.markdown(f"Filtered features: {len(filtered)}")

# Create map
center = None
if len(filtered) > 0:
    center = [filtered.geometry.centroid.y.mean(), filtered.geometry.centroid.x.mean()]
else:
    # fallback center to Riverside approx
    center = [33.9806, -117.3755]

m = leafmap.Map(center=center, zoom=11)

# Add all zones as a choropleth-like layer using the zone_code for colors
# add_gdf will color by column if provided
try:
    m.add_gdf(filtered, layer_name="Zones", column=zone_code_field, cmap="Set3", show_legend=True)
except Exception:
    # fallback: convert to geojson and add
    m.add_geojson(filtered.__geo_interface__, layer_name="Zones (geojson)")

# Add layer control and display in Streamlit
m.add_layer_control()
m.to_streamlit(height=700)