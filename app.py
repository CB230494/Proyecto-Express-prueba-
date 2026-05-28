import streamlit as st
from datetime import datetime
import uuid

st.set_page_config(
    page_title="Servicios Locales",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================
# CONFIGURACIÓN
# ======================================================

CODIGO_TRABAJADOR = "12345"
NUMERO_AYUDA = "50660793746"
LINK_WHATSAPP = (
    f"https://wa.me/{NUMERO_AYUDA}"
    "?text=Hola,%20necesito%20ayuda%20con%20la%20plataforma%20de%20servicios."
)

# ======================================================
# ESTILOS FIJOS
# ======================================================

st.markdown("""
<style>
:root {
    color-scheme: light !important;
}

html, body, .stApp {
    background: #f3f6fb !important;
    color: #111827 !important;
}

* {
    color-scheme: light !important;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #111827 !important;
}

[data-testid="stSidebar"] {
    background: #0f172a !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

input, textarea, select {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
}

button {
    color: #111827 !important;
}

.stButton > button {
    width: 100% !important;
    height: 48px !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #cbd5e1 !important;
}

.stButton > button:hover {
    background: #e5e7eb !important;
    color: #111827 !important;
}

.stLinkButton > a {
    width: 100% !important;
    height: 48px !important;
    border-radius: 14px !important;
    font-weight: 900 !important;
    background: #16a34a !important;
    color: #ffffff !important;
    border: none !important;
}

.main-title {
    font-size: 46px;
    font-weight: 900;
    color: #0f172a !important;
    margin-bottom: 4px;
}

.main-subtitle {
    font-size: 18px;
    color: #475569 !important;
    margin-bottom: 24px;
}

.card {
    background: #ffffff !important;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.10);
    border: 1px solid #e5e7eb;
    margin-bottom: 18px;
}

.card * {
    color: #111827 !important;
}

.card-login {
    background: #ffffff !important;
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 14px 34px rgba(15, 23, 42, 0.12);
    border: 1px solid #e5e7eb;
    min-height: 240px;
}

.service-card {
    border-radius: 24px;
    padding: 24px;
    height: 190px;
    min-height: 190px;
    max-height: 190px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.16);
    margin-bottom: 12px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
}

.service-card * {
    color: #ffffff !important;
}

.service-card h2 {
    font-size: 30px !important;
    line-height: 1.1 !important;
    margin: 0 !important;
}

.service-card p {
    display: none !important;
}

.express { background: linear-gradient(135deg, #ef4444, #f97316); }
.taxi { background: linear-gradient(135deg, #ca8a04, #f59e0b); }
.carga { background: linear-gradient(135deg, #2563eb, #0891b2); }
.camion { background: linear-gradient(135deg, #15803d, #22c55e); }

.estado-disponible {
    background: #dcfce7;
    color: #166534 !important;
    padding: 7px 13px;
    border-radius: 999px;
    font-weight: 800;
}

.estado-ocupado {
    background: #fee2e2;
    color: #991b1b !important;
    padding: 7px 13px;
    border-radius: 999px;
    font-weight: 800;
}

.estado-fuera {
    background: #e5e7eb;
    color: #374151 !important;
    padding: 7px 13px;
    border-radius: 999px;
    font-weight: 800;
}

.estado-pendiente {
    background: #fef3c7;
    color: #92400e !important;
    padding: 7px 13px;
    border-radius: 999px;
    font-weight: 800;
}

.estado-aceptado {
    background: #dbeafe;
    color: #1d4ed8 !important;
    padding: 7px 13px;
    border-radius: 999px;
    font-weight: 800;
}

.estado-finalizado {
    background: #dcfce7;
    color: #166534 !important;
    padding: 7px 13px;
    border-radius: 999px;
    font-weight: 800;
}

.precio {
    color: #16a34a !important;
    font-size: 24px;
    font-weight: 900;
}

.chat-user {
    background: #dbeafe !important;
    padding: 13px;
    border-radius: 16px;
    margin-bottom: 8px;
}

.chat-worker {
    background: #dcfce7 !important;
    padding: 13px;
    border-radius: 16px;
    margin-bottom: 8px;
}

.help-box {
    background: #052e16 !important;
    border-radius: 18px;
    padding: 18px;
    margin-top: 25px;
    margin-bottom: 15px;
}

.help-box * {
    color: #ffffff !important;
}

@media (max-width: 768px) {
    .main-title {
        font-size: 34px !important;
    }

    .main-subtitle {
        font-size: 16px !important;
    }

    .service-card {
        height: 135px !important;
        min-height: 135px !important;
        max-height: 135px !important;
        padding: 18px !important;
    }

    .service-card h2 {
        font-size: 26px !important;
    }

    .card-login {
        min-height: auto !important;
        padding: 22px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# DATOS TEMPORALES
# ======================================================

SERVICIOS = {
    "Express": {
        "icono": "🛵",
        "clase": "express",
        "descripcion": "Mandados, compras rápidas, documentos, comida y entregas pequeñas.",
        "tarifas": "Base ₡1.000 de 0 a 2 km. De 2 a 5 km: +₡1.000. De 5 a 10 km: +₡2.000."
    },
    "Taxi": {
        "icono": "🚕",
        "clase": "taxi",
        "descripcion": "Traslado de personas dentro y fuera del centro.",
        "tarifas": "Base ₡1.500. El precio aumenta según distancia, horario y destino."
    },
    "Carga": {
        "icono": "📦",
        "clase": "carga",
        "descripcion": "Traslado de paquetes medianos, compras grandes o artículos.",
        "tarifas": "Desde ₡2.000. Varía según peso, volumen y distancia."
    },
    "Camión": {
        "icono": "🚚",
        "clase": "camion",
        "descripcion": "Mudanzas, materiales, carga pesada o transporte especial.",
        "tarifas": "Desde ₡5.000. Precio según carga, distancia y tiempo."
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
        "detalle": "Mandados, compras y entregas pequeñas.",
        "precio": "₡1.000 base + distancia"
    },
    {
        "id": "T002",
        "nombre": "María Solano",
        "cedula": "202220222",
        "telefono": "8888-2222",
        "servicio": "Taxi",
        "estado": "Disponible",
        "detalle": "Taxi local y viajes programados.",
        "precio": "Desde ₡1.500"
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
]

# ======================================================
# SESSION STATE
# ======================================================

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "inicio"

if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = None

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if "trabajador_actual" not in st.session_state:
    st.session_state.trabajador_actual = None

if "trabajadores" not in st.session_state:
    st.session_state.trabajadores = TRABAJADORES_BASE.copy()

if "usuarios" not in st.session_state:
    st.session_state.usuarios = []

if "solicitudes" not in st.session_state:
    st.session_state.solicitudes = []

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "servicio_cliente" in st.session_state:
    if st.session_state.servicio_cliente not in SERVICIOS:
        del st.session_state.servicio_cliente

# ======================================================
# FUNCIONES
# ======================================================

def soporte_whatsapp():
    st.markdown("""
    <div class="help-box">
        <h3>¿Necesita ayuda?</h3>
        <p>Puede contactar al encargado de la plataforma por WhatsApp.</p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "💬 Contactar soporte por WhatsApp",
        LINK_WHATSAPP,
        use_container_width=True
    )


def volver_inicio():
    st.session_state.pantalla = "inicio"
    st.session_state.tipo_usuario = None
    st.session_state.usuario_actual = None
    st.session_state.trabajador_actual = None


def estado_html(estado):
    if estado == "Disponible":
        return '<span class="estado-disponible">🟢 Disponible</span>'
    if estado == "Ocupado":
        return '<span class="estado-ocupado">🔴 Ocupado</span>'
    if estado == "Fuera de servicio":
        return '<span class="estado-fuera">⚫ Fuera de servicio</span>'
    if estado == "Pendiente":
        return '<span class="estado-pendiente">⏳ Pendiente</span>'
    if estado == "Aceptado":
        return '<span class="estado-aceptado">🛵 Aceptado</span>'
    if estado == "Finalizado":
        return '<span class="estado-finalizado">✅ Finalizado</span>'
    return estado


def cambiar_estado_trabajador(trabajador_id, nuevo_estado):
    for t in st.session_state.trabajadores:
        if t["id"] == trabajador_id:
            t["estado"] = nuevo_estado


def crear_solicitud(servicio, trabajador, cliente, telefono_cliente, detalle, lugar_compra, lugar_entrega):
    solicitud_id = str(uuid.uuid4())[:8]

    solicitud = {
        "id": solicitud_id,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "servicio": servicio,
        "trabajador_id": trabajador["id"],
        "trabajador": trabajador["nombre"],
        "telefono_trabajador": trabajador["telefono"],
        "cliente": cliente,
        "telefono_cliente": telefono_cliente,
        "detalle": detalle,
        "lugar_compra": lugar_compra,
        "lugar_entrega": lugar_entrega,
        "estado": "Pendiente"
    }

    st.session_state.solicitudes.append(solicitud)
    st.session_state.chats[solicitud_id] = []
    cambiar_estado_trabajador(trabajador["id"], "Ocupado")

    return solicitud_id

# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.title("Servicios Locales")

    if st.session_state.tipo_usuario:
        st.success(f"Perfil activo: {st.session_state.tipo_usuario}")

    if st.button("Volver al inicio", use_container_width=True):
        volver_inicio()
        st.rerun()

    st.markdown("---")
    st.write("Código colaborador de prueba:")
    st.code(CODIGO_TRABAJADOR)

# ======================================================
# PANTALLA INICIO
# ======================================================

if st.session_state.pantalla == "inicio":

    st.markdown('<div class="main-title">Servicios Locales</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Ingrese como cliente o colaborador para continuar.</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card-login">
            <h2>👤 Cliente</h2>
            <p>Solicite servicios de express, taxi, carga o camión.</p>
            <p>Podrá ver colaboradores disponibles, precios, estados y usar el chat interno.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("registro_cliente"):
            nombre = st.text_input("Nombre completo")
            cedula = st.text_input("Número de cédula")
            telefono = st.text_input("Teléfono")
            entrar = st.form_submit_button("Ingresar como cliente")

            if entrar:
                if not nombre or not cedula or not telefono:
                    st.error("Debe completar nombre, cédula y teléfono.")
                else:
                    st.session_state.usuario_actual = {
                        "nombre": nombre,
                        "cedula": cedula,
                        "telefono": telefono
                    }
                    st.session_state.usuarios.append(st.session_state.usuario_actual)
                    st.session_state.tipo_usuario = "Cliente"
                    st.session_state.pantalla = "cliente"
                    st.rerun()

    with col2:
        st.markdown("""
        <div class="card-login">
            <h2>🛠️ Colaborador</h2>
            <p>Registre su servicio y administre su estado.</p>
            <p>El registro requiere un código de 5 dígitos.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("registro_trabajador"):
            nombre_t = st.text_input("Nombre completo", key="nombre_t")
            cedula_t = st.text_input("Número de cédula", key="cedula_t")
            telefono_t = st.text_input("Teléfono", key="telefono_t")
            servicio_t = st.selectbox("Servicio que brinda", list(SERVICIOS.keys()))
            codigo_t = st.text_input("Código de trabajador", type="password")
            detalle_t = st.text_area("Descripción breve del servicio")
            entrar_t = st.form_submit_button("Ingresar como colaborador")

            if entrar_t:
                if codigo_t != CODIGO_TRABAJADOR:
                    st.error("Código incorrecto. Solicite el código al coordinador.")
                elif not nombre_t or not cedula_t or not telefono_t:
                    st.error("Debe completar nombre, cédula y teléfono.")
                else:
                    existente = next(
                        (t for t in st.session_state.trabajadores if t["cedula"] == cedula_t),
                        None
                    )

                    if existente:
                        st.session_state.trabajador_actual = existente
                    else:
                        nuevo = {
                            "id": str(uuid.uuid4())[:5],
                            "nombre": nombre_t,
                            "cedula": cedula_t,
                            "telefono": telefono_t,
                            "servicio": servicio_t,
                            "estado": "Disponible",
                            "detalle": detalle_t if detalle_t else "Servicio disponible.",
                            "precio": SERVICIOS[servicio_t]["tarifas"]
                        }
                        st.session_state.trabajadores.append(nuevo)
                        st.session_state.trabajador_actual = nuevo

                    st.session_state.tipo_usuario = "Colaborador"
                    st.session_state.pantalla = "trabajador"
                    st.rerun()

    soporte_whatsapp()

# ======================================================
# PANEL CLIENTE
# ======================================================

elif st.session_state.pantalla == "cliente":

    usuario = st.session_state.usuario_actual

    st.title("Panel del cliente")

    st.markdown(f"""
    <div class="card">
        <h3>Bienvenido, {usuario['nombre']}</h3>
        <p><b>Cédula:</b> {usuario['cedula']}</p>
        <p><b>Teléfono:</b> {usuario['telefono']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Seleccione un servicio")

    cols = st.columns(4)

    for i, (servicio, data) in enumerate(SERVICIOS.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="service-card {data['clase']}">
                <h2>{data['icono']}<br>{servicio}</h2>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Ingresar", key=f"btn_{servicio}", use_container_width=True):
                st.session_state.servicio_cliente = servicio
                st.rerun()

    if "servicio_cliente" in st.session_state:
        if st.session_state.servicio_cliente not in SERVICIOS:
            del st.session_state.servicio_cliente
            st.rerun()

        servicio_elegido = st.session_state.servicio_cliente
        data = SERVICIOS[servicio_elegido]

        st.divider()

        st.markdown(f"""
        <div class="card">
            <h2>{data['icono']} {servicio_elegido}</h2>
            <p><b>Información del servicio:</b> {data['descripcion']}</p>
            <p><b>Precio:</b> <span class="precio">{data['tarifas']}</span></p>
        </div>
        """, unsafe_allow_html=True)

        trabajadores_servicio = [
            t for t in st.session_state.trabajadores
            if t["servicio"] == servicio_elegido
        ]

        st.subheader("Colaboradores disponibles")

        if not trabajadores_servicio:
            st.warning("No hay colaboradores registrados para este servicio.")
        else:
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
                        lugar_compra = st.text_input("Lugar de compra / recogida", key=f"compra_{t['id']}")
                        lugar_entrega = st.text_input("Lugar de entrega / destino", key=f"entrega_{t['id']}")
                        detalle = st.text_area("Detalle de lo que necesita", key=f"detalle_{t['id']}")

                        if st.button(f"Enviar solicitud", key=f"solicitar_{t['id']}", use_container_width=True):
                            solicitud_id = crear_solicitud(
                                servicio=servicio_elegido,
                                trabajador=t,
                                cliente=usuario["nombre"],
                                telefono_cliente=usuario["telefono"],
                                detalle=detalle,
                                lugar_compra=lugar_compra,
                                lugar_entrega=lugar_entrega
                            )
                            st.success(f"Solicitud enviada. Código: {solicitud_id}")
                            st.rerun()
                else:
                    st.warning("Este colaborador no está disponible actualmente.")

    st.divider()
    st.subheader("Mis solicitudes y chat")

    mis_solicitudes = [
        s for s in st.session_state.solicitudes
        if s["cliente"] == usuario["nombre"]
    ]

    if not mis_solicitudes:
        st.info("Todavía no tiene solicitudes.")
    else:
        for s in mis_solicitudes:
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['id']}</h3>
                <p><b>Servicio:</b> {s['servicio']}</p>
                <p><b>Colaborador:</b> {s['trabajador']}</p>
                <p><b>Teléfono colaborador:</b> {s['telefono_trabajador']}</p>
                <p><b>Estado:</b> {estado_html(s['estado'])}</p>
                <p><b>Recoger / comprar:</b> {s['lugar_compra']}</p>
                <p><b>Entregar / destino:</b> {s['lugar_entrega']}</p>
            </div>
            """, unsafe_allow_html=True)

            st.write("Chat interno")

            for msg in st.session_state.chats.get(s["id"], []):
                clase = "chat-user" if msg["de"] == "Cliente" else "chat-worker"
                st.markdown(f"""
                <div class="{clase}">
                    <b>{msg['de']}:</b> {msg['texto']}<br>
                    <small>{msg['hora']}</small>
                </div>
                """, unsafe_allow_html=True)

            texto = st.text_input("Escribir mensaje", key=f"msg_cliente_{s['id']}")

            if st.button("Enviar mensaje", key=f"send_cliente_{s['id']}"):
                if texto:
                    st.session_state.chats[s["id"]].append({
                        "de": "Cliente",
                        "texto": texto,
                        "hora": datetime.now().strftime("%H:%M")
                    })
                    st.toast("Mensaje enviado.")
                    st.rerun()

    soporte_whatsapp()

# ======================================================
# PANEL COLABORADOR
# ======================================================

elif st.session_state.pantalla == "trabajador":

    trabajador = st.session_state.trabajador_actual

    st.title("Panel del colaborador")

    st.markdown(f"""
    <div class="card">
        <h3>{trabajador['nombre']}</h3>
        <p><b>Cédula:</b> {trabajador['cedula']}</p>
        <p><b>Teléfono:</b> {trabajador['telefono']}</p>
        <p><b>Servicio:</b> {trabajador['servicio']}</p>
        <p><b>Estado actual:</b> {estado_html(trabajador['estado'])}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        nuevo_estado = st.selectbox(
            "Cambiar mi estado",
            ["Disponible", "Ocupado", "Fuera de servicio"],
            index=["Disponible", "Ocupado", "Fuera de servicio"].index(trabajador["estado"])
        )

    with col2:
        if st.button("Actualizar estado", use_container_width=True):
            cambiar_estado_trabajador(trabajador["id"], nuevo_estado)
            st.session_state.trabajador_actual["estado"] = nuevo_estado
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
                <p><b>Fecha:</b> {s['fecha']}</p>
                <p><b>Cliente:</b> {s['cliente']}</p>
                <p><b>Teléfono cliente:</b> {s['telefono_cliente']}</p>
                <p><b>Servicio:</b> {s['servicio']}</p>
                <p><b>Estado:</b> {estado_html(s['estado'])}</p>
                <p><b>Recoger / comprar:</b> {s['lugar_compra']}</p>
                <p><b>Entregar / destino:</b> {s['lugar_entrega']}</p>
                <p><b>Detalle:</b> {s['detalle']}</p>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button(f"Aceptar #{s['id']}", key=f"aceptar_{s['id']}", use_container_width=True):
                    s["estado"] = "Aceptado"
                    cambiar_estado_trabajador(trabajador["id"], "Ocupado")
                    st.rerun()

            with c2:
                if st.button(f"Pendiente #{s['id']}", key=f"pendiente_{s['id']}", use_container_width=True):
                    s["estado"] = "Pendiente"
                    st.rerun()

            with c3:
                if st.button(f"Finalizar #{s['id']}", key=f"finalizar_{s['id']}", use_container_width=True):
                    s["estado"] = "Finalizado"
                    cambiar_estado_trabajador(trabajador["id"], "Disponible")
                    st.session_state.trabajador_actual["estado"] = "Disponible"
                    st.rerun()

            st.write("Chat con el cliente")

            for msg in st.session_state.chats.get(s["id"], []):
                clase = "chat-worker" if msg["de"] == "Colaborador" else "chat-user"
                st.markdown(f"""
                <div class="{clase}">
                    <b>{msg['de']}:</b> {msg['texto']}<br>
                    <small>{msg['hora']}</small>
                </div>
                """, unsafe_allow_html=True)

            texto = st.text_input("Responder mensaje", key=f"msg_colaborador_{s['id']}")

            if st.button("Enviar respuesta", key=f"send_colaborador_{s['id']}"):
                if texto:
                    st.session_state.chats[s["id"]].append({
                        "de": "Colaborador",
                        "texto": texto,
                        "hora": datetime.now().strftime("%H:%M")
                    })
                    st.toast("Mensaje enviado.")
                    st.rerun()

            st.divider()

    soporte_whatsapp()
