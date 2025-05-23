import streamlit as st
import pandas as pd
import requests
import pydeck as pdk

# --- Título ---
st.title("🌍 Mapa de Últimos Sismos en el Mundo")
st.caption("Datos en tiempo real desde USGS (United States Geological Survey)")

# --- Cargar datos desde la API ---
@st.cache_data
def cargar_sismos():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    response = requests.get(url)
    data = response.json()
    sismos = []
    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        sismos.append({
            "magnitud": props["mag"],
            "lugar": props["place"],
            "lat": coords[1],
            "lon": coords[0]
        })
    return pd.DataFrame(sismos)

df = cargar_sismos()

# --- Mostrar tabla ---
st.subheader("📋 Tabla de Sismos Recientes")
st.dataframe(df[['magnitud', 'lugar', 'lat', 'lon']])

# --- Mostrar Heatmap ---
st.subheader("🗺️ Mapa Heatmap de Sismos")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position='[lon, lat]',
            aggregation=pdk.types.String("MEAN"),
            get_weight="magnitud",
            opacity=0.9,
        )
    ],
))
