import streamlit as st
import folium
import requests
import polyline
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

.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 18px;
}

.precio {
    color: #16a34a;
    font-size: 32px;
    font-weight: 900;
}

.rojo {
    color: #ef4444;
    font-weight: 800;
}

.azul {
    color: #2563eb;
    font-weight: 800;
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

    folium.Marker(
        location=[express_data["lat"], express_data["lon"]],
        popup="Salida del express",
        tooltip="Salida del express",
        icon=folium.Icon(color="red", icon="motorcycle", prefix="fa")
    ).add_to(mapa)

    if ruta:
        folium.PolyLine(
            locations=ruta,
            color="#2563eb",
            weight=8,
            opacity=0.9,
            tooltip="Ruta del express por calles"
        ).add_to(mapa)

    if cliente:
        folium.Marker(
            location=[cliente["lat"], cliente["lon"]],
            popup="Destino del cliente",
            tooltip="Destino del cliente",
            icon=folium.Icon(color="blue", icon="user", prefix="fa")
        ).add_to(mapa)

    return mapa


# ==============================
# SESSION STATE
# ==============================

if "cliente" not in st.session_state:
    st.session_state.cliente = None

if "ruta" not in st.session_state:
    st.session_state.ruta = None

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if "express_listo" not in st.session_state:
    st.session_state.express_listo = False

if "servicio_realizado" not in st.session_state:
    st.session_state.servicio_realizado = False


# ==============================
# SIDEBAR
# ==============================

with st.sidebar:
    st.title("🛵 Express San José Centro")
    st.write("Calcula la ruta y el costo del envío.")

    st.subheader("1. Express de salida")

    express_seleccionado = st.selectbox(
        "Seleccione el express",
        list(EXPRESS.keys())
    )

    express_data = EXPRESS[express_seleccionado]

    st.info(
        f"🔴 **{express_seleccionado}**\n\n"
        f"📍 {express_data['direccion']}"
    )

    st.subheader("2. Estado del express")

    if st.button("Estoy listo para hacer el express 🛵", use_container_width=True):
        st.session_state.express_listo = True
        st.session_state.servicio_realizado = False

    if st.session_state.express_listo:
        st.success("Express listo para recibir ruta.")
    else:
        st.warning("El express aún no está listo.")

    st.subheader("3. Datos del cliente")

    nombre_cliente = st.text_input("Cliente opcional")
    telefono = st.text_input("Teléfono opcional")
    detalle = st.text_area("Detalle del envío opcional")

    st.info(
        "🔴 Rojo: salida del express\n\n"
        "🔵 Azul: destino del cliente\n\n"
        "🟦 Línea azul: ruta por calles"
    )


# ==============================
# APP PRINCIPAL
# ==============================

st.title("Ruta del express")

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
    st.session_state.ruta = None
    st.session_state.resultado = None
    st.session_state.servicio_realizado = False
    st.rerun()

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.express_listo:
        st.success("🛵 Express listo")
    else:
        st.warning("🛵 Express no listo")

with col2:
    if st.session_state.cliente:
        st.success("📍 Cliente marcado")
    else:
        st.warning("📍 Marque el destino del cliente")

with col3:
    if st.session_state.servicio_realizado:
        st.success("✅ Express realizado")
    else:
        st.info("⏳ Servicio pendiente")


# ==============================
# BOTÓN CALCULAR
# ==============================

calcular = st.button(
    "Calcular ruta y precio",
    use_container_width=True,
    disabled=not st.session_state.express_listo
)

if calcular:
    if not st.session_state.cliente:
        st.error("Primero debe marcar el destino del cliente en el mapa.")
    else:
        cliente = st.session_state.cliente

        ruta = obtener_ruta_osrm(
            express_data["lat"],
            express_data["lon"],
            cliente["lat"],
            cliente["lon"]
        )

        if ruta is None:
            st.error("No se pudo calcular la ruta por calles.")
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
# RESUMEN DEL SERVICIO
# ==============================

if st.session_state.resultado:
    resultado = st.session_state.resultado

    st.subheader("Resumen del servicio")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"""
        <div class="card">
            <h3>📋 Información del envío</h3>
            <p><b>Express:</b> <span class="rojo">{express_seleccionado}</span></p>
            <p><b>Desde:</b> {express_data["direccion"]}</p>
            <p><b>Hasta:</b> <span class="azul">Destino marcado por el cliente</span></p>
            <p><b>Distancia:</b> {resultado["distancia_km"]:.2f} km</p>
            <p><b>Tiempo estimado:</b> {resultado["duracion_min"]:.0f} minutos</p>
            <p><b>Precio estimado:</b></p>
            <p class="precio">₡{resultado["tarifa"]:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="card">
            <h3>🧾 Datos adicionales</h3>
            <p><b>Cliente:</b> {nombre_cliente if nombre_cliente else "No indicado"}</p>
            <p><b>Teléfono:</b> {telefono if telefono else "No indicado"}</p>
            <p><b>Detalle:</b> {detalle if detalle else "No indicado"}</p>
            <p><b>Estado:</b> {"✅ Realizado" if st.session_state.servicio_realizado else "⏳ Pendiente"}</p>
        </div>
        """, unsafe_allow_html=True)

    if not st.session_state.servicio_realizado:
        if st.button("Marcar express como realizado ✅", use_container_width=True):
            st.session_state.servicio_realizado = True
            st.rerun()
    else:
        st.success("El express fue marcado como realizado correctamente.")

else:
    st.info(
        "Para iniciar: seleccione el express, presione "
        "'Estoy listo para hacer el express', marque el destino del cliente "
        "en el mapa y luego calcule la ruta."
    )
