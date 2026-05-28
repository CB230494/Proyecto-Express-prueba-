import streamlit as st
from datetime import datetime
import uuid

st.set_page_config(
    page_title="Servicios Locales",
    page_icon="🚕",
    layout="wide"
)

# ======================================================
# ESTILOS FIJOS
# ======================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%) !important;
    color: #111827 !important;
}

h1, h2, h3, h4, p, label, span, div {
    color: #111827 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.card {
    background: white;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.12);
    border: 1px solid #e5e7eb;
    margin-bottom: 18px;
}

.card-color {
    border-radius: 24px;
    padding: 28px;
    color: white !important;
    min-height: 180px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.18);
}

.card-color * {
    color: white !important;
}

.express { background: linear-gradient(135deg, #ef4444, #f97316); }
.taxi { background: linear-gradient(135deg, #facc15, #f59e0b); }
.carga { background: linear-gradient(135deg, #2563eb, #06b6d4); }
.camion { background: linear-gradient(135deg, #16a34a, #22c55e); }
.ayuda { background: linear-gradient(135deg, #7c3aed, #ec4899); }

.estado-disponible {
    background: #dcfce7;
    color: #166534 !important;
    padding: 7px 12px;
    border-radius: 999px;
    font-weight: 800;
}

.estado-ocupado {
    background: #fee2e2;
    color: #991b1b !important;
    padding: 7px 12px;
    border-radius: 999px;
    font-weight: 800;
}

.estado-fuera {
    background: #e5e7eb;
    color: #374151 !important;
    padding: 7px 12px;
    border-radius: 999px;
    font-weight: 800;
}

.chat-user {
    background: #dbeafe;
    padding: 12px;
    border-radius: 16px;
    margin-bottom: 8px;
}

.chat-worker {
    background: #dcfce7;
    padding: 12px;
    border-radius: 16px;
    margin-bottom: 8px;
}

.precio {
    color: #16a34a !important;
    font-size: 26px;
    font-weight: 900;
}

.stButton > button {
    border-radius: 14px !important;
    font-weight: 800 !important;
    min-height: 45px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# DATOS TEMPORALES
# ======================================================

CODIGO_TRABAJADOR = "12345"

SERVICIOS = {
    "Express": {
        "icono": "🛵",
        "clase": "express",
        "descripcion": "Mandados, compras rápidas, documentos, comida y entregas pequeñas.",
        "tarifas": "Base ₡1.000 / 0-2 km. Luego aumenta según distancia."
    },
    "Taxi": {
        "icono": "🚕",
        "clase": "taxi",
        "descripcion": "Traslado de personas dentro y fuera del centro.",
        "tarifas": "Base ₡1.500 / precio variable según distancia."
    },
    "Carga": {
        "icono": "📦",
        "clase": "carga",
        "descripcion": "Traslado de paquetes medianos, compras grandes o artículos.",
        "tarifas": "Base ₡2.000 / depende del peso, volumen y distancia."
    },
    "Camión": {
        "icono": "🚚",
        "clase": "camion",
        "descripcion": "Mudanzas, carga pesada o transporte de materiales.",
        "tarifas": "Desde ₡5.000 / depende del viaje y carga."
    },
    "Ayuda": {
        "icono": "🤝",
        "clase": "ayuda",
        "descripcion": "Apoyo para trámites, compras, acompañamientos o asistencia local.",
        "tarifas": "Precio acordado según servicio."
    }
}

TRABAJADORES_BASE = [
    {
        "id": "T001",
        "nombre": "Carlos Méndez",
        "cedula": "101110111",
        "telefono": "8888-1111",
        "servicio": "Express",
        "estado": "Disponible",
        "detalle": "Hace mandados, compras y entregas pequeñas.",
        "precio": "₡1.000 base + distancia"
    },
    {
        "id": "T002",
        "nombre": "María Solano",
        "cedula": "202220222",
        "telefono": "8888-2222",
        "servicio": "Taxi",
        "estado": "Disponible",
        "detalle": "Servicio de taxi local y viajes programados.",
        "precio": "₡1.500 base"
    },
    {
        "id": "T003",
        "nombre": "José Vargas",
        "cedula": "303330333",
        "telefono": "8888-3333",
        "servicio": "Carga",
        "estado": "Ocupado",
        "detalle": "Carga liviana y paquetes medianos.",
        "precio": "Desde ₡2.000"
    },
    {
        "id": "T004",
        "nombre": "Luis Ramírez",
        "cedula": "404440444",
        "telefono": "8888-4444",
        "servicio": "Camión",
        "estado": "Fuera de servicio",
        "detalle": "Camión para carga y mudanzas.",
        "precio": "Desde ₡5.000"
    },
    {
        "id": "T005",
        "nombre": "Ana Rodríguez",
        "cedula": "505550555",
        "telefono": "8888-5555",
        "servicio": "Ayuda",
        "estado": "Disponible",
        "detalle": "Apoyo en trámites, compras y asistencia.",
        "precio": "Precio acordado"
    },
]

# ======================================================
# SESSION STATE
# ======================================================

if "trabajadores" not in st.session_state:
    st.session_state.trabajadores = TRABAJADORES_BASE.copy()

if "usuarios" not in st.session_state:
    st.session_state.usuarios = []

if "solicitudes" not in st.session_state:
    st.session_state.solicitudes = []

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "servicio_actual" not in st.session_state:
    st.session_state.servicio_actual = None

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if "trabajador_actual" not in st.session_state:
    st.session_state.trabajador_actual = None

# ======================================================
# FUNCIONES
# ======================================================

def estado_html(estado):
    if estado == "Disponible":
        return '<span class="estado-disponible">🟢 Disponible</span>'
    if estado == "Ocupado":
        return '<span class="estado-ocupado">🔴 Ocupado</span>'
    return '<span class="estado-fuera">⚫ Fuera de servicio</span>'


def crear_solicitud(servicio, trabajador, cliente, detalle, lugar_compra, lugar_entrega):
    solicitud_id = str(uuid.uuid4())[:8]

    solicitud = {
        "id": solicitud_id,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "servicio": servicio,
        "trabajador_id": trabajador["id"],
        "trabajador": trabajador["nombre"],
        "telefono_trabajador": trabajador["telefono"],
        "cliente": cliente,
        "detalle": detalle,
        "lugar_compra": lugar_compra,
        "lugar_entrega": lugar_entrega,
        "estado": "Pendiente"
    }

    st.session_state.solicitudes.append(solicitud)
    st.session_state.chats[solicitud_id] = []

    return solicitud_id


def cambiar_estado_trabajador(trabajador_id, nuevo_estado):
    for t in st.session_state.trabajadores:
        if t["id"] == trabajador_id:
            t["estado"] = nuevo_estado


# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.title("🚕 Plataforma Local")
    st.write("Express, taxi, carga, camión y ayuda.")

    perfil = st.radio(
        "Ingresar como:",
        ["Inicio", "Usuario", "Trabajador", "Coordinador"]
    )

# ======================================================
# INICIO
# ======================================================

if perfil == "Inicio":
    st.title("🌈 Servicios Locales")

    st.markdown("""
    <div class="card">
        <h3>Bienvenido</h3>
        <p>Seleccione un servicio para ver información, trabajadores disponibles, precios y solicitar atención.</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)

    for i, (servicio, data) in enumerate(SERVICIOS.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="card-color {data['clase']}">
                <h2>{data['icono']} {servicio}</h2>
                <p>{data['descripcion']}</p>
                <p><b>{data['tarifas']}</b></p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Información sobre {servicio}", key=f"info_{servicio}", use_container_width=True):
                st.session_state.servicio_actual = servicio
                st.rerun()

    if st.session_state.servicio_actual:
        servicio = st.session_state.servicio_actual
        data = SERVICIOS[servicio]

        st.subheader(f"{data['icono']} {servicio}")

        st.markdown(f"""
        <div class="card">
            <h3>Información sobre el servicio</h3>
            <p>{data['descripcion']}</p>
            <p><b>Precio por distancia:</b> {data['tarifas']}</p>
            <p>Para solicitar este servicio, ingrese como <b>Usuario</b>.</p>
        </div>
        """, unsafe_allow_html=True)

# ======================================================
# USUARIO
# ======================================================

elif perfil == "Usuario":
    st.title("👤 Perfil de usuario")

    with st.expander("Registrar usuario", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            nombre_usuario = st.text_input("Nombre completo del usuario")
        with col2:
            cedula_usuario = st.text_input("Número de cédula del usuario")

        if st.button("Registrar usuario", use_container_width=True):
            if not nombre_usuario or not cedula_usuario:
                st.error("Debe completar nombre y cédula.")
            else:
                st.session_state.usuario_actual = {
                    "nombre": nombre_usuario,
                    "cedula": cedula_usuario
                }
                st.success("Usuario registrado correctamente.")

    if st.session_state.usuario_actual:
        st.markdown(f"""
        <div class="card">
            <h3>Usuario activo</h3>
            <p><b>Nombre:</b> {st.session_state.usuario_actual['nombre']}</p>
            <p><b>Cédula:</b> {st.session_state.usuario_actual['cedula']}</p>
        </div>
        """, unsafe_allow_html=True)

        servicio = st.selectbox("Seleccione el servicio", list(SERVICIOS.keys()))

        data = SERVICIOS[servicio]

        st.markdown(f"""
        <div class="card-color {data['clase']}">
            <h2>{data['icono']} {servicio}</h2>
            <p>{data['descripcion']}</p>
            <p><b>Precio:</b> {data['tarifas']}</p>
        </div>
        """, unsafe_allow_html=True)

        trabajadores_servicio = [
            t for t in st.session_state.trabajadores
            if t["servicio"] == servicio
        ]

        st.subheader("Trabajadores disponibles")

        for t in trabajadores_servicio:
            st.markdown(f"""
            <div class="card">
                <h3>{t['nombre']}</h3>
                <p><b>Teléfono:</b> {t['telefono']}</p>
                <p><b>Servicio:</b> {t['servicio']}</p>
                <p><b>Detalle:</b> {t['detalle']}</p>
                <p><b>Precio:</b> <span class="precio">{t['precio']}</span></p>
                <p><b>Estado:</b> {estado_html(t['estado'])}</p>
            </div>
            """, unsafe_allow_html=True)

            if t["estado"] == "Disponible":
                with st.expander(f"Solicitar servicio a {t['nombre']}"):
                    lugar_compra = st.text_input("¿Dónde debe comprar o recoger?", key=f"compra_{t['id']}")
                    lugar_entrega = st.text_input("¿Dónde debe entregar o llegar?", key=f"entrega_{t['id']}")
                    detalle = st.text_area("¿Qué necesita?", key=f"detalle_{t['id']}")

                    if st.button(f"Enviar solicitud a {t['nombre']}", key=f"solicitar_{t['id']}", use_container_width=True):
                        solicitud_id = crear_solicitud(
                            servicio=servicio,
                            trabajador=t,
                            cliente=st.session_state.usuario_actual["nombre"],
                            detalle=detalle,
                            lugar_compra=lugar_compra,
                            lugar_entrega=lugar_entrega
                        )

                        cambiar_estado_trabajador(t["id"], "Ocupado")

                        st.success(f"Solicitud enviada. Código: {solicitud_id}")
                        st.info("El trabajador fue marcado como ocupado hasta finalizar el servicio.")
                        st.rerun()
            else:
                st.warning("Este trabajador no está disponible en este momento.")

        st.subheader("Mis solicitudes y chat")

        mis_solicitudes = [
            s for s in st.session_state.solicitudes
            if s["cliente"] == st.session_state.usuario_actual["nombre"]
        ]

        if not mis_solicitudes:
            st.info("No tiene solicitudes registradas.")
        else:
            for s in mis_solicitudes:
                st.markdown(f"""
                <div class="card">
                    <h3>Solicitud #{s['id']}</h3>
                    <p><b>Servicio:</b> {s['servicio']}</p>
                    <p><b>Trabajador:</b> {s['trabajador']}</p>
                    <p><b>Estado:</b> {s['estado']}</p>
                    <p><b>Comprar / recoger:</b> {s['lugar_compra']}</p>
                    <p><b>Entregar / llegar:</b> {s['lugar_entrega']}</p>
                </div>
                """, unsafe_allow_html=True)

                st.write("💬 Chat interno")

                for msg in st.session_state.chats.get(s["id"], []):
                    clase = "chat-user" if msg["de"] == "Usuario" else "chat-worker"
                    st.markdown(f"""
                    <div class="{clase}">
                        <b>{msg['de']}:</b> {msg['texto']}<br>
                        <small>{msg['hora']}</small>
                    </div>
                    """, unsafe_allow_html=True)

                texto = st.text_input("Escribir mensaje", key=f"msg_user_{s['id']}")

                if st.button("Enviar mensaje", key=f"send_user_{s['id']}"):
                    if texto:
                        st.session_state.chats[s["id"]].append({
                            "de": "Usuario",
                            "texto": texto,
                            "hora": datetime.now().strftime("%H:%M")
                        })
                        st.toast("Mensaje enviado al trabajador.")
                        st.rerun()

# ======================================================
# TRABAJADOR
# ======================================================

elif perfil == "Trabajador":
    st.title("🛠️ Perfil de trabajador")

    with st.expander("Registrar trabajador", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            nombre = st.text_input("Nombre completo")
            cedula = st.text_input("Número de cédula")
        with col2:
            telefono = st.text_input("Teléfono")
            servicio = st.selectbox("Servicio que brinda", list(SERVICIOS.keys()))
        with col3:
            codigo = st.text_input("Código de trabajador de 5 dígitos", type="password")
            detalle = st.text_area("Descripción del servicio")

        if st.button("Registrar como trabajador", use_container_width=True):
            if codigo != CODIGO_TRABAJADOR:
                st.error("Código incorrecto. Solo el coordinador puede autorizar trabajadores.")
            elif not nombre or not cedula or not telefono:
                st.error("Debe completar nombre, cédula y teléfono.")
            else:
                nuevo = {
                    "id": str(uuid.uuid4())[:5],
                    "nombre": nombre,
                    "cedula": cedula,
                    "telefono": telefono,
                    "servicio": servicio,
                    "estado": "Disponible",
                    "detalle": detalle if detalle else "Servicio disponible.",
                    "precio": SERVICIOS[servicio]["tarifas"]
                }

                st.session_state.trabajadores.append(nuevo)
                st.session_state.trabajador_actual = nuevo
                st.success("Trabajador registrado correctamente.")

    trabajador_nombres = [t["nombre"] for t in st.session_state.trabajadores]

    nombre_login = st.selectbox("Ingresar como trabajador registrado", trabajador_nombres)

    trabajador = next(
        t for t in st.session_state.trabajadores
        if t["nombre"] == nombre_login
    )

    st.session_state.trabajador_actual = trabajador

    st.markdown(f"""
    <div class="card">
        <h3>{trabajador['nombre']}</h3>
        <p><b>Servicio:</b> {trabajador['servicio']}</p>
        <p><b>Teléfono:</b> {trabajador['telefono']}</p>
        <p><b>Estado actual:</b> {estado_html(trabajador['estado'])}</p>
    </div>
    """, unsafe_allow_html=True)

    nuevo_estado = st.selectbox(
        "Cambiar estado",
        ["Disponible", "Ocupado", "Fuera de servicio"],
        index=["Disponible", "Ocupado", "Fuera de servicio"].index(trabajador["estado"])
    )

    if st.button("Actualizar estado", use_container_width=True):
        cambiar_estado_trabajador(trabajador["id"], nuevo_estado)
        st.success("Estado actualizado.")
        st.rerun()

    st.subheader("Solicitudes asignadas")

    solicitudes_trabajador = [
        s for s in st.session_state.solicitudes
        if s["trabajador_id"] == trabajador["id"]
    ]

    if not solicitudes_trabajador:
        st.info("No tiene solicitudes asignadas.")
    else:
        for s in solicitudes_trabajador:
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['id']}</h3>
                <p><b>Cliente:</b> {s['cliente']}</p>
                <p><b>Servicio:</b> {s['servicio']}</p>
                <p><b>Estado:</b> {s['estado']}</p>
                <p><b>Comprar / recoger:</b> {s['lugar_compra']}</p>
                <p><b>Entregar / llegar:</b> {s['lugar_entrega']}</p>
                <p><b>Detalle:</b> {s['detalle']}</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"Aceptar #{s['id']}", key=f"aceptar_{s['id']}", use_container_width=True):
                    s["estado"] = "Aceptado"
                    cambiar_estado_trabajador(trabajador["id"], "Ocupado")
                    st.toast("Solicitud aceptada.")
                    st.rerun()

            with col2:
                if st.button(f"Pendiente #{s['id']}", key=f"pendiente_{s['id']}", use_container_width=True):
                    s["estado"] = "Pendiente"
                    st.toast("Solicitud pendiente.")
                    st.rerun()

            with col3:
                if st.button(f"Finalizar #{s['id']}", key=f"finalizar_{s['id']}", use_container_width=True):
                    s["estado"] = "Finalizado"
                    cambiar_estado_trabajador(trabajador["id"], "Disponible")
                    st.toast("Servicio finalizado. Trabajador disponible.")
                    st.rerun()

            st.write("💬 Chat con el cliente")

            for msg in st.session_state.chats.get(s["id"], []):
                clase = "chat-worker" if msg["de"] == "Trabajador" else "chat-user"
                st.markdown(f"""
                <div class="{clase}">
                    <b>{msg['de']}:</b> {msg['texto']}<br>
                    <small>{msg['hora']}</small>
                </div>
                """, unsafe_allow_html=True)

            texto = st.text_input("Responder mensaje", key=f"msg_worker_{s['id']}")

            if st.button("Enviar respuesta", key=f"send_worker_{s['id']}"):
                if texto:
                    st.session_state.chats[s["id"]].append({
                        "de": "Trabajador",
                        "texto": texto,
                        "hora": datetime.now().strftime("%H:%M")
                    })
                    st.toast("Mensaje enviado al usuario.")
                    st.rerun()

            st.divider()

# ======================================================
# COORDINADOR
# ======================================================

elif perfil == "Coordinador":
    st.title("📊 Panel del coordinador")

    st.markdown("""
    <div class="card">
        <h3>Código actual para registrar trabajadores</h3>
        <p class="precio">12345</p>
        <p>Este código se puede cambiar luego cuando conectemos base de datos.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Trabajadores registrados")

    for t in st.session_state.trabajadores:
        st.markdown(f"""
        <div class="card">
            <h3>{t['nombre']}</h3>
            <p><b>Cédula:</b> {t['cedula']}</p>
            <p><b>Teléfono:</b> {t['telefono']}</p>
            <p><b>Servicio:</b> {t['servicio']}</p>
            <p><b>Estado:</b> {estado_html(t['estado'])}</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Solicitudes")

    if not st.session_state.solicitudes:
        st.info("No hay solicitudes todavía.")
    else:
        for s in st.session_state.solicitudes:
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['id']}</h3>
                <p><b>Fecha:</b> {s['fecha']}</p>
                <p><b>Cliente:</b> {s['cliente']}</p>
                <p><b>Trabajador:</b> {s['trabajador']}</p>
                <p><b>Servicio:</b> {s['servicio']}</p>
                <p><b>Estado:</b> {s['estado']}</p>
            </div>
            """, unsafe_allow_html=True)
