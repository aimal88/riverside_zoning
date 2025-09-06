# app.py
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Riverside Zoning Viewer")

# GitHub raw GeoJSON link
geojson_url = "https://raw.githubusercontent.com/aimal88/riverside_zoning/refs/heads/main/datasets/ca_riverside.geojson"

@st.cache_data(ttl=3600)
def load_data(url):
    gdf = gpd.read_file(url)
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326, allow_override=True)
    else:
        gdf = gdf.to_crs(epsg=4326)
    return gdf

gdf = load_data(geojson_url)

# Sidebar filters
st.sidebar.header("Filter Zones")
zone_options = sorted(gdf["zone_name"].unique())
selected_zones = st.sidebar.multiselect("Select Zone(s)", zone_options, default=zone_options)

# Filtered data
filtered_gdf = gdf[gdf["zone_name"].isin(selected_zones)]

# Create map
m = leafmap.Map(center=[33.9533, -117.3961], zoom=11)  # Riverside coordinates
m.add_gdf(
    filtered_gdf,
    layer_name="Riverside Zones",
    info_mode="on_hover",
    popup=["zone_code", "zone_name"],
)

# Show map
m.to_streamlit(height=700)
