import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import pandas as pd

st.set_page_config(
    page_title="Calculadora de Express",
    page_icon="🏍️",
    layout="wide"
)

# ==============================
# CONFIGURACIÓN DE EXPRESS
# ==============================

EXPRESS = {
    "Express Centro": {
        "lat": 9.934739,
        "lon": -84.087502,
        "base": 1000
    },
    "Express Norte": {
        "lat": 9.960000,
        "lon": -84.080000,
        "base": 1200
    },
    "Express Sur": {
        "lat": 9.900000,
        "lon": -84.100000,
        "base": 1000
    }
}

# ==============================
# FUNCIÓN PARA CALCULAR TARIFA
# ==============================

def calcular_tarifa(km, tarifa_base):
    if km <= 2:
        return tarifa_base
    elif km <= 5:
        return tarifa_base + 1000
    elif km <= 10:
        return tarifa_base + 2000
    elif km <= 15:
        return tarifa_base + 3500
    else:
        return tarifa_base + 5000


# ==============================
# INTERFAZ
# ==============================

st.title("🏍️ Calculadora de Distancia y Precio de Express")

st.info(
    "Marque en el mapa la ubicación del cliente, seleccione un express "
    "y el sistema calculará la distancia y el precio estimado."
)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Datos del servicio")

    express_seleccionado = st.selectbox(
        "Seleccione el express",
        list(EXPRESS.keys())
    )

    nombre_cliente = st.text_input("Nombre del cliente")

    telefono = st.text_input("Teléfono")

    detalle_entrega = st.text_area("Detalle del pedido o entrega")

    st.divider()

    st.write("Tarifas actuales:")
    tarifas = pd.DataFrame({
        "Distancia": [
            "0 a 2 km",
            "2 a 5 km",
            "5 a 10 km",
            "10 a 15 km",
            "Más de 15 km"
        ],
        "Aumento": [
            "Tarifa base",
            "+ ₡1.000",
            "+ ₡2.000",
            "+ ₡3.500",
            "+ ₡5.000"
        ]
    })

    st.dataframe(tarifas, use_container_width=True)

with col2:
    st.subheader("Mapa de ubicación")

    express_data = EXPRESS[express_seleccionado]
    punto_express = (express_data["lat"], express_data["lon"])

    mapa = folium.Map(
        location=[express_data["lat"], express_data["lon"]],
        zoom_start=13
    )

    folium.Marker(
        location=[express_data["lat"], express_data["lon"]],
        popup=f"Punto de salida: {express_seleccionado}",
        tooltip=express_seleccionado,
        icon=folium.Icon(color="red", icon="motorcycle", prefix="fa")
    ).add_to(mapa)

    mapa.add_child(folium.LatLngPopup())

    resultado_mapa = st_folium(
        mapa,
        width=900,
        height=500
    )

# ==============================
# CÁLCULO
# ==============================

st.divider()

if resultado_mapa and resultado_mapa.get("last_clicked"):
    lat_cliente = resultado_mapa["last_clicked"]["lat"]
    lon_cliente = resultado_mapa["last_clicked"]["lng"]

    punto_cliente = (lat_cliente, lon_cliente)

    distancia_km = geodesic(punto_express, punto_cliente).km
    tarifa = calcular_tarifa(distancia_km, express_data["base"])

    st.success("Ubicación marcada correctamente.")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Distancia aproximada", f"{distancia_km:.2f} km")

    with col_b:
        st.metric("Express seleccionado", express_seleccionado)

    with col_c:
        st.metric("Precio estimado", f"₡{tarifa:,.0f}")

    st.subheader("Resumen del servicio")

    resumen = {
        "Cliente": nombre_cliente,
        "Teléfono": telefono,
        "Express": express_seleccionado,
        "Latitud cliente": lat_cliente,
        "Longitud cliente": lon_cliente,
        "Distancia km": round(distancia_km, 2),
        "Precio estimado": tarifa,
        "Detalle": detalle_entrega
    }

    st.json(resumen)

else:
    st.warning("Haga clic en el mapa para marcar la ubicación del cliente.")


