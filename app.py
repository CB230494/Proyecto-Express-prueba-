import streamlit as st
import folium
import requests
import polyline
import pandas as pd
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Express San José Centro",
    page_icon="🛵",
    layout="wide"
)

# ==============================
# ESTILOS
# ==============================

st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07111f 0%, #101827 100%);
}

[data-testid="stSidebar"] * {
    color: white;
}

.titulo {
    font-size: 34px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 5px;
}

.subtitulo {
    font-size: 15px;
    color: #d1d5db;
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 18px;
}

.card h3 {
    margin-top: 0;
    color: #111827;
}

.valor-rojo {
    color: #ef4444;
    font-weight: 800;
}

.valor-azul {
    color: #2563eb;
    font-weight: 800;
}

.valor-verde {
    color: #16a34a;
    font-weight: 900;
    font-size: 28px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# EXPRESS SAN JOSÉ CENTRO
# ==============================

EXPRESS = {
    "Express Parque Central": {
        "lat": 9.93333,
        "lon": -84.08333,
        "direccion": "Parque Central, San José",
        "base": 1000
    },
    "Express Mercado Central": {
        "lat": 9.93510,
        "lon": -84.07860,
        "direccion": "Mercado Central, San José",
        "base": 1000
    },
    "Express Hospital San Juan de Dios": {
        "lat": 9.93270,
        "lon": -84.09020,
        "direccion": "Hospital San Juan de Dios",
        "base": 1200
    },
    "Express Barrio Amón": {
        "lat": 9.93940,
        "lon": -84.07690,
        "direccion": "Barrio Amón, San José",
        "base": 1200
    },
    "Express Norte": {
        "lat": 9.95200,
        "lon": -84.08000,
        "direccion": "Av. 47 con Calle Central, San José",
        "base": 1200
    }
}

# ==============================
# FUNCIONES
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


def obtener_ruta_osrm(origen_lat, origen_lon, destino_lat, destino_lon):
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{origen_lon},{origen_lat};{destino_lon},{destino_lat}"
        "?overview=full&geometries=polyline"
    )

    try:
        respuesta = requests.get(url, timeout=15)
        if respuesta.status_code != 200:
            return None

        data = respuesta.json()

        if data.get("code") != "Ok":
            return None

        ruta = data["routes"][0]

        distancia_km = ruta["distance"] / 1000
        duracion_min = ruta["duration"] / 60
        geometria = polyline.decode(ruta["geometry"])

        return distancia_km, duracion_min, geometria

    except Exception:
        return None


def crear_mapa(express_data, cliente=None, ruta=None):
    mapa = folium.Map(
        location=[9.934739, -84.087502],
        zoom_start=15,
        tiles="CartoDB positron"
    )

    # Marcador del express
    folium.Marker(
        location=[express_data["lat"], express_data["lon"]],
        popup="Salida del express",
        tooltip="Salida del express",
        icon=folium.Icon(color="red", icon="motorcycle", prefix="fa")
    ).add_to(mapa)

    # Ruta
    if ruta:
        folium.PolyLine(
            locations=ruta,
            color="#2563eb",
            weight=7,
            opacity=0.85,
            tooltip="Ruta sugerida por calles"
        ).add_to(mapa)

    # Marcador del cliente
    if cliente:
        folium.Marker(
            location=[cliente["lat"], cliente["lon"]],
            popup="Destino del cliente",
            tooltip="Destino del cliente",
            icon=folium.Icon(color="blue", icon="user", prefix="fa")
        ).add_to(mapa)

    mapa.add_child(folium.LatLngPopup())

    return mapa


# ==============================
# SIDEBAR
# ==============================

with st.sidebar:
    st.markdown('<div class="titulo">🛵 Express San José Centro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Calcula la ruta y el costo del envío.</div>', unsafe_allow_html=True)

    st.markdown("### 1. Selecciona el express de salida")
    express_seleccionado = st.selectbox(
        "Express",
        list(EXPRESS.keys()),
        label_visibility="collapsed"
    )

    express_data = EXPRESS[express_seleccionado]

    st.info(
        f"🔴 **{express_seleccionado}**\n\n"
        f"📍 {express_data['direccion']}"
    )

    st.markdown("### 2. Marca el destino del cliente")
    st.write("Haz clic en el mapa sobre la calle donde está el cliente.")

    st.info(
        "🔵 La marca azul representa al cliente.\n\n"
        "🔴 La marca roja representa el punto de salida del express."
    )

    st.markdown("### 3. Información adicional")
    nombre_cliente = st.text_input("Cliente opcional", placeholder="Nombre del cliente")
    telefono = st.text_input("Teléfono opcional", placeholder="Número de teléfono")
    detalle = st.text_area("Detalle del envío opcional", placeholder="Ej. documentos, paquete pequeño, comida, etc.")

# ==============================
# APP PRINCIPAL
# ==============================

st.title("Ruta del express")

if "cliente" not in st.session_state:
    st.session_state.cliente = None

if "ruta" not in st.session_state:
    st.session_state.ruta = None

if "resultado" not in st.session_state:
    st.session_state.resultado = None

mapa = crear_mapa(
    express_data=express_data,
    cliente=st.session_state.cliente,
    ruta=st.session_state.ruta
)

resultado_mapa = st_folium(
    mapa,
    width=1400,
    height=560,
    returned_objects=["last_clicked"]
)

if resultado_mapa and resultado_mapa.get("last_clicked"):
    st.session_state.cliente = {
        "lat": resultado_mapa["last_clicked"]["lat"],
        "lon": resultado_mapa["last_clicked"]["lng"]
    }

st.divider()

col_btn, col_msg = st.columns([1, 2])

with col_btn:
    calcular = st.button("Calcular ruta y precio 🚀", use_container_width=True)

with col_msg:
    if st.session_state.cliente:
        st.success("Destino del cliente marcado correctamente.")
    else:
        st.warning("Primero marca el destino del cliente en el mapa.")

if calcular:
    if not st.session_state.cliente:
        st.error("Debes marcar el destino del cliente en el mapa.")
    else:
        cliente = st.session_state.cliente

        ruta = obtener_ruta_osrm(
            express_data["lat"],
            express_data["lon"],
            cliente["lat"],
            cliente["lon"]
        )

        if ruta is None:
            st.error("No se pudo calcular la ruta por calles. Revisa la conexión a internet.")
        else:
            distancia_km, duracion_min, geometria = ruta
            tarifa = calcular_tarifa(distancia_km, express_data["base"])

            st.session_state.ruta = geometria
            st.session_state.resultado = {
                "distancia_km": distancia_km,
                "duracion_min": duracion_min,
                "tarifa": tarifa
            }

            st.rerun()

# ==============================
# RESUMEN
# ==============================

if st.session_state.resultado:
    resultado = st.session_state.resultado

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>📋 Resumen del servicio</h3>
            <p><b>Express:</b> <span class="valor-rojo">{express_seleccionado}</span></p>
            <p><b>Desde:</b> {express_data["direccion"]}</p>
            <p><b>Hasta:</b> <span class="valor-azul">Destino marcado por el cliente</span></p>
            <p><b>Distancia:</b> {resultado["distancia_km"]:.2f} km</p>
            <p><b>Tiempo estimado:</b> {resultado["duracion_min"]:.0f} min</p>
            <p><b>Precio estimado:</b> <span class="valor-verde">₡{resultado["tarifa"]:,.0f}</span></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>🧭 Ruta</h3>
            <p>🔴 Punto de salida del express</p>
            <p>🔵 Destino del cliente</p>
            <p>🔵 Línea azul: ruta sugerida por calles</p>
            <hr>
            <p><b>Cliente:</b> {nombre_cliente if nombre_cliente else "No indicado"}</p>
            <p><b>Teléfono:</b> {telefono if telefono else "No indicado"}</p>
            <p><b>Detalle:</b> {detalle if detalle else "No indicado"}</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="card">
        <h3>📍 Instrucciones</h3>
        <p>1. Selecciona el express en el panel izquierdo.</p>
        <p>2. Haz clic en el mapa sobre la ubicación del cliente.</p>
        <p>3. Presiona <b>Calcular ruta y precio</b>.</p>
    </div>
    """, unsafe_allow_html=True)

