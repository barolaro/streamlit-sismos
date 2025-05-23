import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime

st.set_page_config(page_title="Mapa de Sismos", layout="wide")

# --- Título principal ---
st.title("🌍 Mapa de Últimos Sismos en el Mundo")
st.caption("Datos en tiempo real desde USGS (United States Geological Survey)")

# --- Forzar recarga manual ---
if "forzar_recarga" not in st.session_state:
    st.session_state.forzar_recarga = False

def resetear_cache():
    st.session_state.forzar_recarga = True

# --- Botón para actualizar manualmente ---
st.button("🔃 Actualizar ahora", on_click=resetear_cache)

# --- Cargar datos (con cache automático de 20 minutos) ---
@st.cache_data(ttl=1200)  # 20 minutos = 1200 segundos
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

# --- Cargar con o sin forzar ---
if st.session_state.forzar_recarga:
    st.cache_data.clear()
    st.session_state.forzar_recarga = False

df = cargar_sismos()

# --- Última actualización ---
st.caption(f"🕒 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- Mostrar tabla ---
st.subheader("📋 Tabla de Sismos Recientes")
st.dataframe(df[['magnitud', 'lugar', 'lat', 'lon']], use_container_width=True)

# --- Mapa Heatmap ---
st.subheader("🗺️ Mapa Heatmap de Sismos")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1.2,
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
