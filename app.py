import streamlit as st
import folium
import requests
import polyline
from streamlit_folium import st_folium
from datetime import datetime
import uuid

st.set_page_config(
    page_title="Express Siquirres / San José",
    page_icon="🛵",
    layout="wide"
)

# =====================================================
# ESTILOS FIJOS PARA EVITAR PROBLEMAS MODO CLARO/OSCURO
# =====================================================

st.markdown("""
<style>
html, body, .stApp {
    background-color: #f4f6f9 !important;
    color: #111827 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07111f 0%, #101827 100%) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #ffffff !important;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #111827;
}

.card {
    background: #ffffff !important;
    color: #111827 !important;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.10);
    margin-bottom: 18px;
    border: 1px solid #e5e7eb;
}

.card * {
    color: #111827 !important;
}

.card-dark {
    background: #0f172a !important;
    color: #ffffff !important;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 16px;
}

.card-dark * {
    color: #ffffff !important;
}

.estado-pendiente {
    background: #fef3c7;
    color: #92400e !important;
    padding: 8px 14px;
    border-radius: 12px;
    font-weight: 800;
}

.estado-aceptado {
    background: #dbeafe;
    color: #1d4ed8 !important;
    padding: 8px 14px;
    border-radius: 12px;
    font-weight: 800;
}

.estado-realizado {
    background: #dcfce7;
    color: #166534 !important;
    padding: 8px 14px;
    border-radius: 12px;
    font-weight: 800;
}

.precio {
    color: #16a34a !important;
    font-size: 34px;
    font-weight: 900;
}

.rojo {
    color: #ef4444 !important;
    font-weight: 900;
}

.azul {
    color: #2563eb !important;
    font-weight: 900;
}

.stButton > button {
    background-color: #16a34a !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    border: none !important;
}

.stButton > button:hover {
    background-color: #15803d !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

CENTRO_MAPA = [10.0975, -83.5066]

EXPRESS = {
    "Express Siquirres Centro": {
        "lat": 10.0975,
        "lon": -83.5066,
        "direccion": "Siquirres Centro",
        "base": 1000
    },
    "Express Terminal Siquirres": {
        "lat": 10.0968,
        "lon": -83.5078,
        "direccion": "Terminal de Siquirres",
        "base": 1000
    },
    "Express Hospital Siquirres": {
        "lat": 10.1003,
        "lon": -83.5095,
        "direccion": "Sector Hospital de Siquirres",
        "base": 1200
    },
    "Express Ruta 32 Siquirres": {
        "lat": 10.0948,
        "lon": -83.5009,
        "direccion": "Sector Ruta 32, Siquirres",
        "base": 1200
    }
}

# =====================================================
# SESSION STATE
# =====================================================

if "solicitudes" not in st.session_state:
    st.session_state.solicitudes = []

if "cliente_marcado" not in st.session_state:
    st.session_state.cliente_marcado = None

if "ruta_actual" not in st.session_state:
    st.session_state.ruta_actual = None

if "resultado_actual" not in st.session_state:
    st.session_state.resultado_actual = None

# =====================================================
# FUNCIONES
# =====================================================

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
        location=CENTRO_MAPA,
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
            tooltip="Ruta sugerida por calles"
        ).add_to(mapa)

    if cliente:
        folium.Marker(
            location=[cliente["lat"], cliente["lon"]],
            popup="Destino del cliente",
            tooltip="Destino del cliente",
            icon=folium.Icon(color="blue", icon="user", prefix="fa")
        ).add_to(mapa)

    return mapa


def etiqueta_estado(estado):
    if estado == "Pendiente":
        return '<span class="estado-pendiente">⏳ Pendiente</span>'
    elif estado == "Aceptado":
        return '<span class="estado-aceptado">🛵 Aceptado</span>'
    elif estado == "Realizado":
        return '<span class="estado-realizado">✅ Realizado</span>'
    return estado

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.title("🛵 Sistema Express")
    st.write("Solicitud, aceptación y seguimiento del servicio.")

    perfil = st.radio(
        "Seleccione perfil",
        ["Cliente", "Colaborador / Express"]
    )

# =====================================================
# PERFIL CLIENTE
# =====================================================

if perfil == "Cliente":

    st.title("📍 Solicitar un express")

    col_form, col_map = st.columns([1, 2])

    with col_form:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Datos de la solicitud")

        express_seleccionado = st.selectbox(
            "Seleccione el express de salida",
            list(EXPRESS.keys())
        )

        express_data = EXPRESS[express_seleccionado]

        nombre_cliente = st.text_input("Nombre del cliente")
        telefono = st.text_input("Teléfono")
        detalle = st.text_area("Detalle del envío")

        st.info(
            "Marque en el mapa el destino del cliente. "
            "El sistema calculará distancia, ruta y precio."
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_map:
        mapa = crear_mapa(
            express_data=express_data,
            cliente=st.session_state.cliente_marcado,
            ruta=st.session_state.ruta_actual
        )

        resultado_mapa = st_folium(
            mapa,
            width=1200,
            height=550,
            returned_objects=["last_clicked"]
        )

        if resultado_mapa and resultado_mapa.get("last_clicked"):
            st.session_state.cliente_marcado = {
                "lat": resultado_mapa["last_clicked"]["lat"],
                "lon": resultado_mapa["last_clicked"]["lng"]
            }
            st.session_state.ruta_actual = None
            st.session_state.resultado_actual = None
            st.rerun()

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.cliente_marcado:
            st.success("📍 Destino marcado")
        else:
            st.warning("📍 Marque el destino")

    with col2:
        st.info(f"🛵 {express_seleccionado}")

    with col3:
        st.info("⏳ Solicitud sin enviar")

    calcular = st.button("Calcular ruta y precio", use_container_width=True)

    if calcular:
        if not st.session_state.cliente_marcado:
            st.error("Debe marcar el destino del cliente en el mapa.")
        else:
            cliente = st.session_state.cliente_marcado

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

                st.session_state.ruta_actual = geometria
                st.session_state.resultado_actual = {
                    "distancia_km": distancia_km,
                    "duracion_min": duracion_min,
                    "tarifa": tarifa
                }

                st.rerun()

    if st.session_state.resultado_actual:
        resultado = st.session_state.resultado_actual

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(f"""
            <div class="card">
                <h3>📋 Resumen del servicio</h3>
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
                <h3>🧭 Ruta</h3>
                <p><b>🔴 Rojo:</b> salida del express</p>
                <p><b>🔵 Azul:</b> destino del cliente</p>
                <p><b>🟦 Línea azul:</b> ruta sugerida por calles</p>
                <p><b>Estado inicial:</b> {etiqueta_estado("Pendiente")}</p>
            </div>
            """, unsafe_allow_html=True)

        enviar = st.button("Enviar solicitud al colaborador 🛵", use_container_width=True)

        if enviar:
            nueva_solicitud = {
                "id": str(uuid.uuid4())[:8],
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cliente": nombre_cliente if nombre_cliente else "No indicado",
                "telefono": telefono if telefono else "No indicado",
                "detalle": detalle if detalle else "No indicado",
                "express": express_seleccionado,
                "direccion_salida": express_data["direccion"],
                "origen_lat": express_data["lat"],
                "origen_lon": express_data["lon"],
                "destino_lat": st.session_state.cliente_marcado["lat"],
                "destino_lon": st.session_state.cliente_marcado["lon"],
                "distancia_km": resultado["distancia_km"],
                "duracion_min": resultado["duracion_min"],
                "tarifa": resultado["tarifa"],
                "ruta": st.session_state.ruta_actual,
                "estado": "Pendiente"
            }

            st.session_state.solicitudes.append(nueva_solicitud)

            st.success("Solicitud enviada correctamente al colaborador.")

            st.session_state.cliente_marcado = None
            st.session_state.ruta_actual = None
            st.session_state.resultado_actual = None

# =====================================================
# PERFIL COLABORADOR
# =====================================================

else:

    st.title("🛵 Panel del colaborador / express")

    if not st.session_state.solicitudes:
        st.info("No hay solicitudes registradas todavía.")
    else:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todas", "Pendiente", "Aceptado", "Realizado"]
        )

        solicitudes_filtradas = [
            s for s in st.session_state.solicitudes
            if filtro_estado == "Todas" or s["estado"] == filtro_estado
        ]

        for solicitud in solicitudes_filtradas:
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{solicitud["id"]}</h3>
                <p><b>Fecha:</b> {solicitud["fecha"]}</p>
                <p><b>Cliente:</b> {solicitud["cliente"]}</p>
                <p><b>Teléfono:</b> {solicitud["telefono"]}</p>
                <p><b>Detalle:</b> {solicitud["detalle"]}</p>
                <p><b>Express:</b> <span class="rojo">{solicitud["express"]}</span></p>
                <p><b>Desde:</b> {solicitud["direccion_salida"]}</p>
                <p><b>Distancia:</b> {solicitud["distancia_km"]:.2f} km</p>
                <p><b>Tiempo estimado:</b> {solicitud["duracion_min"]:.0f} minutos</p>
                <p><b>Precio:</b> <span class="precio">₡{solicitud["tarifa"]:,.0f}</span></p>
                <p><b>Estado:</b> {etiqueta_estado(solicitud["estado"])}</p>
            </div>
            """, unsafe_allow_html=True)

            mapa_solicitud = crear_mapa(
                express_data={
                    "lat": solicitud["origen_lat"],
                    "lon": solicitud["origen_lon"]
                },
                cliente={
                    "lat": solicitud["destino_lat"],
                    "lon": solicitud["destino_lon"]
                },
                ruta=solicitud["ruta"]
            )

            st_folium(
                mapa_solicitud,
                width=1200,
                height=430
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    f"Aceptar solicitud #{solicitud['id']} 🛵",
                    key=f"aceptar_{solicitud['id']}",
                    use_container_width=True
                ):
                    solicitud["estado"] = "Aceptado"
                    st.rerun()

            with col2:
                if st.button(
                    f"Dejar pendiente #{solicitud['id']} ⏳",
                    key=f"pendiente_{solicitud['id']}",
                    use_container_width=True
                ):
                    solicitud["estado"] = "Pendiente"
                    st.rerun()

            with col3:
                if st.button(
                    f"Marcar realizado #{solicitud['id']} ✅",
                    key=f"realizado_{solicitud['id']}",
                    use_container_width=True
                ):
                    solicitud["estado"] = "Realizado"
                    st.rerun()

            st.divider()
