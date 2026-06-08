# =========================================================
# PARTE 1 / 5
# CONFIGURACIÓN GENERAL, IMPORTACIONES Y CONSTANTES
# App Express Local + Google Sheets + Firebase Push
# =========================================================

import streamlit as st
import pandas as pd
import gspread
import re
import uuid
import json
import base64

from datetime import datetime
from urllib.parse import quote
from google.oauth2.service_account import Credentials

# Firebase Admin para enviar notificaciones push reales
import firebase_admin
from firebase_admin import credentials as firebase_credentials
from firebase_admin import messaging


# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================

st.set_page_config(
    page_title="Express Local",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# URL DE GOOGLE SHEETS
# =========================================================

SPREADSHEET_URL = "AQUI_PEGA_LA_URL_DE_TU_GOOGLE_SHEETS"


# =========================================================
# CREDENCIALES ADMINISTRADOR
# =========================================================

ADMIN_USUARIO = "administrador123"
ADMIN_CLAVE = "123456"


# =========================================================
# HOJAS DE GOOGLE SHEETS
# =========================================================

HOJA_USUARIOS = "Usuarios"
HOJA_DATOS_GENERALES = "Datos generales"
HOJA_COLABORADORES = "Colaboradores"
HOJA_SOLICITUDES = "Solicitudes"


# =========================================================
# ENCABEZADOS DE HOJAS
# IMPORTANTE:
# Push Token se agrega automáticamente si no existe.
# =========================================================

ENCABEZADOS_USUARIOS = [
    "ID",
    "Nombre",
    "Primer apellido",
    "Segundo apellido",
    "Teléfono",
    "Usuario",
    "Clave",
    "Tipo",
    "Fecha",
    "Push Token"
]

ENCABEZADOS_COLABORADORES = [
    "ID",
    "Nombre",
    "Primer apellido",
    "Segundo apellido",
    "Teléfono",
    "Usuario",
    "Clave",
    "Tipo",
    "Servicio",
    "Estado",
    "Fecha",
    "Push Token"
]

ENCABEZADOS_SOLICITUDES = [
    "ID",
    "Fecha",
    "Servicio",
    "Cliente ID",
    "Cliente",
    "Teléfono cliente",
    "Detalle",
    "Estado",
    "Colaborador ID",
    "Colaborador",
    "Teléfono colaborador"
]

ENCABEZADOS_DATOS_GENERALES = [
    "Clave",
    "Valor"
]


# =========================================================
# SERVICIOS DISPONIBLES
# =========================================================

SERVICIOS = {
    "Taxi": {
        "icono": "🚕",
        "descripcion": "Servicio de transporte local rápido y seguro.",
        "color1": "#ff9800",
        "color2": "#ff3d00"
    },
    "Express": {
        "icono": "🛵",
        "descripcion": "Mandados, entregas y servicios express.",
        "color1": "#ff5f6d",
        "color2": "#ffc371"
    },
    "Carga": {
        "icono": "📦",
        "descripcion": "Traslado de paquetes, cajas y artículos.",
        "color1": "#2193b0",
        "color2": "#6dd5ed"
    },
    "Camión": {
        "icono": "🚚",
        "descripcion": "Servicio para cargas grandes o traslados pesados.",
        "color1": "#11998e",
        "color2": "#38ef7d"
    }
}


# =========================================================
# LÍMITES DEMO
# =========================================================

MAX_USUARIOS_DEMO = 6

MAX_COLABORADORES_POR_SERVICIO = {
    "Taxi": 6,
    "Express": 6,
    "Carga": 6,
    "Camión": 6
}


# =========================================================
# CONFIGURACIÓN FIREBASE PUSH
# IMPORTANTE:
# En Streamlit Cloud debes guardar firebase_service_account
# dentro de st.secrets, NO en GitHub.
# =========================================================

@st.cache_resource(show_spinner=False)
def inicializar_firebase_admin():
    """
    Inicializa Firebase Admin para enviar notificaciones push.
    Usa st.secrets["firebase_service_account"].
    """

    if firebase_admin._apps:
        return firebase_admin.get_app()

    if "firebase_service_account" not in st.secrets:
        return None

    service_account_info = dict(st.secrets["firebase_service_account"])

    cred = firebase_credentials.Certificate(service_account_info)

    app = firebase_admin.initialize_app(cred)

    return app


def firebase_disponible():
    """
    Verifica si Firebase Admin está configurado.
    """
    try:
        app = inicializar_firebase_admin()
        return app is not None
    except Exception:
        return False


# =========================================================
# ESTILOS BASE
# =========================================================

def cargar_estilos():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #fff7ed 0%, #eff6ff 100%);
        color: #0f172a;
    }

    h1, h2, h3 {
        color: #0f172a !important;
        font-weight: 900 !important;
    }

    p, label, span, div {
        font-size: 16px;
    }

    .card {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid #e2e8f0;
        border-radius: 28px;
        padding: 28px;
        margin-bottom: 22px;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
    }

    .service-card {
        color: white;
        border-radius: 28px;
        padding: 28px;
        min-height: 190px;
        text-align: center;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
    }

    .service-card h2 {
        color: white !important;
        font-size: 30px !important;
    }

    .service-card p {
        color: white !important;
        font-weight: 600;
    }

    .badge {
        padding: 8px 16px;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
    }

    .disponible {
        background: #dcfce7;
        color: #166534;
    }

    .ocupado {
        background: #fee2e2;
        color: #991b1b;
    }

    .fuera {
        background: #e5e7eb;
        color: #374151;
    }

    .pendiente {
        background: #fef3c7;
        color: #92400e;
    }

    .aceptado {
        background: #dbeafe;
        color: #1d4ed8;
    }

    .finalizado {
        background: #dcfce7;
        color: #166534;
    }

    div.stButton > button {
        border-radius: 22px !important;
        border: none !important;
        padding: 12px 22px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ff7a18, #ff3d2e) !important;
        color: white !important;
        box-shadow: 0 15px 35px rgba(255, 61, 46, 0.25);
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 18px 40px rgba(255, 61, 46, 0.35);
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div {
        border-radius: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =========================================================
# CARGA INICIAL
# =========================================================

cargar_estilos()
# =========================================================
# PARTE 2 / 5
# GOOGLE SHEETS, SESIÓN, REGISTROS Y PUSH TOKEN
# =========================================================

@st.cache_resource(show_spinner=False)
def conectar_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    if "gcp_service_account" in st.secrets:
        info = dict(st.secrets["gcp_service_account"])
    else:
        info = dict(st.secrets)

    creds = Credentials.from_service_account_info(info, scopes=scopes)
    cliente = gspread.authorize(creds)

    return cliente.open_by_url(SPREADSHEET_URL)


@st.cache_resource(show_spinner=False)
def obtener_hoja_cache(nombre):
    libro = conectar_google_sheets()
    return libro.worksheet(nombre)


def obtener_hoja(nombre, encabezados):
    libro = conectar_google_sheets()

    try:
        hoja = obtener_hoja_cache(nombre)
    except gspread.WorksheetNotFound:
        hoja = libro.add_worksheet(
            title=nombre,
            rows=500,
            cols=len(encabezados) + 5
        )
        hoja.append_row(encabezados)
        st.cache_resource.clear()
        st.cache_data.clear()
        return hoja

    valores = hoja.get_all_values()

    if not valores:
        hoja.append_row(encabezados)
        st.cache_data.clear()
        return hoja

    encabezados_actuales = valores[0]

    for encabezado in encabezados:
        if encabezado not in encabezados_actuales:
            nueva_columna = len(encabezados_actuales) + 1
            hoja.update_cell(1, nueva_columna, encabezado)
            encabezados_actuales.append(encabezado)

    return hoja


@st.cache_data(ttl=20, show_spinner=False)
def leer_registros_cache(nombre, encabezados_tuple):
    encabezados = list(encabezados_tuple)
    hoja = obtener_hoja(nombre, encabezados)
    filas = hoja.get_all_values()

    if len(filas) <= 1:
        return []

    encabezados_reales = filas[0]
    registros = []

    for i, fila in enumerate(filas[1:], start=2):
        fila_completa = fila + [""] * (len(encabezados_reales) - len(fila))
        registro = dict(zip(encabezados_reales, fila_completa[:len(encabezados_reales)]))
        registro["_fila"] = i
        registros.append(registro)

    return registros


def leer_registros(nombre, encabezados):
    return leer_registros_cache(nombre, tuple(encabezados))


def agregar_registro(nombre, encabezados, datos):
    hoja = obtener_hoja(nombre, encabezados)
    encabezados_reales = hoja.row_values(1)

    fila = [datos.get(campo, "") for campo in encabezados_reales]

    hoja.append_row(
        fila,
        value_input_option="USER_ENTERED"
    )

    st.cache_data.clear()


def actualizar_celda(nombre, encabezados, fila, columna, valor):
    hoja = obtener_hoja(nombre, encabezados)
    encabezados_reales = hoja.row_values(1)

    if columna not in encabezados_reales:
        nueva_columna = len(encabezados_reales) + 1
        hoja.update_cell(1, nueva_columna, columna)
        encabezados_reales.append(columna)

    indice_columna = encabezados_reales.index(columna) + 1

    hoja.update_cell(
        int(fila),
        indice_columna,
        valor
    )

    st.cache_data.clear()


def actualizar_varias_celdas(nombre, encabezados, fila, cambios):
    hoja = obtener_hoja(nombre, encabezados)
    encabezados_reales = hoja.row_values(1)

    for columna in cambios.keys():
        if columna not in encabezados_reales:
            nueva_columna = len(encabezados_reales) + 1
            hoja.update_cell(1, nueva_columna, columna)
            encabezados_reales.append(columna)

    for columna, valor in cambios.items():
        indice_columna = encabezados_reales.index(columna) + 1
        hoja.update_cell(
            int(fila),
            indice_columna,
            valor
        )

    st.cache_data.clear()


def eliminar_fila(nombre, encabezados, fila):
    hoja = obtener_hoja(nombre, encabezados)
    hoja.delete_rows(int(fila))
    st.cache_data.clear()


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def normalizar_usuario(texto):
    return str(texto).strip().lower()


def limpiar_texto(texto):
    return str(texto).strip()


def limpiar_telefono(texto):
    return re.sub(r"[^0-9]", "", str(texto))


def telefono_whatsapp_cr(texto):
    numero = limpiar_telefono(texto)

    if numero.startswith("506"):
        return numero

    return "506" + numero


def link_whatsapp(numero, mensaje):
    return f"https://wa.me/{telefono_whatsapp_cr(numero)}?text={quote(mensaje)}"


def badge_estado(estado):
    estado_l = str(estado).strip().lower()

    if estado_l == "disponible":
        return '<span class="badge disponible">🟢 Disponible</span>'

    if estado_l == "ocupado":
        return '<span class="badge ocupado">🔴 Ocupado</span>'

    if estado_l == "fuera de servicio":
        return '<span class="badge fuera">⚫ Fuera de servicio</span>'

    if estado_l == "pendiente":
        return '<span class="badge pendiente">⏳ Pendiente</span>'

    if estado_l == "aceptado":
        return '<span class="badge aceptado">✅ Aceptado</span>'

    if estado_l == "finalizado":
        return '<span class="badge finalizado">🏁 Finalizado</span>'

    return f'<span class="badge fuera">{estado}</span>'


# =========================================================
# SESIÓN
# =========================================================

def inicializar_estado():
    valores = {
        "pagina": "login",
        "tipo": None,
        "usuario_actual": None,
        "colaborador_actual": None,
        "servicio_seleccionado": None,
        "admin_autenticado": False,
        "push_token_actual": "",
        "alertas_activadas": True,
        "sonido_habilitado": False,
        "ultimo_total_pendientes_colaborador": 0,
        "ultimo_total_aceptadas_usuario": 0,
        "ultima_alerta_usuario_ids": "",
        "ultima_alerta_colaborador_ids": "",
        "alerta_usuario_inicializada": False,
        "alerta_colaborador_inicializada": False
    }

    for clave, valor in valores.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def cerrar_sesion():
    st.session_state.pagina = "login"
    st.session_state.tipo = None
    st.session_state.usuario_actual = None
    st.session_state.colaborador_actual = None
    st.session_state.servicio_seleccionado = None
    st.session_state.admin_autenticado = False
    st.session_state.push_token_actual = ""
    st.session_state.ultimo_total_pendientes_colaborador = 0
    st.session_state.ultimo_total_aceptadas_usuario = 0
    st.session_state.ultima_alerta_usuario_ids = ""
    st.session_state.ultima_alerta_colaborador_ids = ""
    st.session_state.alerta_usuario_inicializada = False
    st.session_state.alerta_colaborador_inicializada = False


# =========================================================
# PUSH TOKEN
# =========================================================

def guardar_push_token_usuario(usuario_id, token):
    usuarios = leer_registros(
        HOJA_USUARIOS,
        ENCABEZADOS_USUARIOS
    )

    for u in usuarios:
        if u.get("ID") == usuario_id:
            actualizar_celda(
                HOJA_USUARIOS,
                ENCABEZADOS_USUARIOS,
                u["_fila"],
                "Push Token",
                token
            )
            return True

    return False


def guardar_push_token_colaborador(colaborador_id, token):
    colaboradores = leer_registros(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES
    )

    for c in colaboradores:
        if c.get("ID") == colaborador_id:
            actualizar_celda(
                HOJA_COLABORADORES,
                ENCABEZADOS_COLABORADORES,
                c["_fila"],
                "Push Token",
                token
            )
            return True

    return False


def enviar_push_token(token, titulo, cuerpo):
    if not token:
        return False

    try:
        if not firebase_disponible():
            return False

        mensaje = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title=titulo,
                body=cuerpo
            ),
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=titulo,
                    body=cuerpo,
                    require_interaction=True
                )
            )
        )

        messaging.send(mensaje)
        return True

    except Exception:
        return False
# =========================================================
# PARTE 3 / 5
# SOLICITUDES, COMPONENTES VISUALES, ALERTAS Y FORMULARIOS
# =========================================================

# =========================================================
# FUNCIONES DE SOLICITUDES
# =========================================================

def crear_solicitud(servicio, usuario, detalle):
    """
    Crea una nueva solicitud de servicio hecha por un usuario.
    """
    datos = {
        "ID": str(uuid.uuid4())[:8],
        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Servicio": servicio,
        "Cliente ID": usuario["ID"],
        "Cliente": f'{usuario["Nombre"]} {usuario["Primer apellido"]} {usuario["Segundo apellido"]}'.strip(),
        "Teléfono cliente": usuario["Teléfono"],
        "Detalle": limpiar_texto(detalle),
        "Estado": "Pendiente",
        "Colaborador ID": "",
        "Colaborador": "",
        "Teléfono colaborador": ""
    }

    agregar_registro(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES,
        datos
    )

    return datos


def solicitudes_usuario(usuario_id):
    """
    Devuelve todas las solicitudes realizadas por un usuario.
    """
    solicitudes = leer_registros(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES
    )

    return [
        s for s in solicitudes
        if s["Cliente ID"] == usuario_id
    ]


def solicitudes_pendientes_servicio(servicio):
    """
    Devuelve solamente las solicitudes pendientes de un servicio.
    Si otro colaborador ya aceptó la solicitud, desaparece para los demás.
    """
    solicitudes = leer_registros(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES
    )

    return [
        s for s in solicitudes
        if s["Servicio"] == servicio and s["Estado"] == "Pendiente"
    ]


def solicitudes_colaborador(colaborador_id):
    """
    Devuelve todas las solicitudes tomadas por un colaborador.
    """
    solicitudes = leer_registros(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES
    )

    return [
        s for s in solicitudes
        if s["Colaborador ID"] == colaborador_id
    ]


def actualizar_estado_colaborador(colaborador, nuevo_estado):
    """
    Cambia el estado de un colaborador.

    Si el colaborador guardado en sesión no trae _fila,
    se busca nuevamente en Google Sheets usando el ID.
    """
    fila_colaborador = colaborador.get("_fila")

    if not fila_colaborador:
        colaboradores = leer_registros(
            HOJA_COLABORADORES,
            ENCABEZADOS_COLABORADORES
        )

        encontrado = next(
            (c for c in colaboradores if c["ID"] == colaborador["ID"]),
            None
        )

        if not encontrado:
            st.error("No se pudo encontrar el colaborador en la base de datos.")
            return False

        fila_colaborador = encontrado["_fila"]
        colaborador.update(encontrado)

    actualizar_celda(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES,
        int(fila_colaborador),
        "Estado",
        nuevo_estado
    )

    colaborador["Estado"] = nuevo_estado
    colaborador["_fila"] = fila_colaborador
    st.session_state.colaborador_actual = colaborador

    return True


def aceptar_solicitud(solicitud, colaborador):
    """
    Acepta una solicitud pendiente.

    Protección:
    Antes de aceptar, vuelve a leer Google Sheets.
    Si la solicitud ya fue aceptada por otro colaborador,
    bloquea la acción.
    """
    solicitudes_actuales = leer_registros(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES
    )

    solicitud_actual = next(
        (s for s in solicitudes_actuales if s["ID"] == solicitud["ID"]),
        None
    )

    if not solicitud_actual:
        st.error("La solicitud ya no existe.")
        return False

    if solicitud_actual["Estado"] != "Pendiente":
        st.warning("Esta solicitud ya fue aceptada por otro colaborador.")
        return False

    nombre_colaborador = (
        f'{colaborador["Nombre"]} '
        f'{colaborador["Primer apellido"]} '
        f'{colaborador["Segundo apellido"]}'
    ).strip()

    actualizar_varias_celdas(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES,
        int(solicitud_actual["_fila"]),
        {
            "Estado": "Aceptado",
            "Colaborador ID": colaborador["ID"],
            "Colaborador": nombre_colaborador,
            "Teléfono colaborador": colaborador["Teléfono"]
        }
    )

    actualizar_estado_colaborador(
        colaborador,
        "Ocupado"
    )

    return True


def finalizar_solicitud(solicitud, colaborador):
    """
    Finaliza una solicitud y devuelve al colaborador a Disponible.
    """
    actualizar_celda(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES,
        int(solicitud["_fila"]),
        "Estado",
        "Finalizado"
    )

    actualizar_estado_colaborador(
        colaborador,
        "Disponible"
    )


# =========================================================
# ALERTAS SONORAS Y VISUALES
# =========================================================

def boton_activar_sonido():
    """
    Botón para solicitar permiso del navegador y activar sonido.
    Debe presionarse una vez en cada dispositivo.
    """
    components.html("""
    <div style="
        background:#fff7ed;
        border:1px solid #fed7aa;
        border-radius:18px;
        padding:14px 16px;
        margin-bottom:14px;
        font-family:Arial, sans-serif;
    ">
        <div style="font-weight:800; color:#9a3412; margin-bottom:8px;">
            🔊 Alertas del dispositivo
        </div>

        <button onclick="activarAlertasExpress()" style="
            background:linear-gradient(135deg,#f97316,#ef4444);
            color:white;
            border:none;
            border-radius:999px;
            padding:10px 18px;
            font-weight:800;
            cursor:pointer;
            width:100%;
        ">
            🔊 Activar sonido y notificaciones
        </button>

        <div id="estado_alerta_express" style="
            margin-top:8px;
            color:#7c2d12;
            font-size:13px;
        ">
            Presione el botón una vez en este dispositivo.
        </div>
    </div>

    <script>
    function beepExpress() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            const audioCtx = new AudioContext();

            const osc1 = audioCtx.createOscillator();
            const gain1 = audioCtx.createGain();

            osc1.type = "square";
            osc1.frequency.setValueAtTime(900, audioCtx.currentTime);
            gain1.gain.setValueAtTime(0.35, audioCtx.currentTime);

            osc1.connect(gain1);
            gain1.connect(audioCtx.destination);

            osc1.start();
            osc1.stop(audioCtx.currentTime + 0.40);

            setTimeout(() => {
                try {
                    const osc2 = audioCtx.createOscillator();
                    const gain2 = audioCtx.createGain();

                    osc2.type = "square";
                    osc2.frequency.setValueAtTime(1150, audioCtx.currentTime);
                    gain2.gain.setValueAtTime(0.35, audioCtx.currentTime);

                    osc2.connect(gain2);
                    gain2.connect(audioCtx.destination);

                    osc2.start();
                    osc2.stop(audioCtx.currentTime + 0.45);
                } catch (e) {}
            }, 480);

        } catch (e) {
            console.log("Error de sonido:", e);
        }
    }

    async function activarAlertasExpress() {
        localStorage.setItem("express_alertas_activas", "1");

        beepExpress();

        if ("Notification" in window) {
            try {
                const permiso = await Notification.requestPermission();

                if (permiso === "granted") {
                    new Notification("🔊 Alertas activadas", {
                        body: "Express Local ya puede mostrar notificaciones mientras la app esté abierta."
                    });
                }
            } catch (e) {}
        }

        if (navigator.vibrate) {
            navigator.vibrate([250, 120, 250]);
        }

        document.getElementById("estado_alerta_express").innerHTML =
            "✅ Alertas activadas. Mantenga esta pantalla abierta.";
    }
    </script>
    """, height=150)


def reproducir_alerta(titulo="🔔 Nueva notificación", mensaje="Hay una actualización nueva en la app."):
    """
    Lanza alerta visual, sonido, vibración y notificación del navegador.
    Funciona mientras la app esté abierta.
    """
    if not st.session_state.get("alertas_activadas", True):
        return

    st.markdown(f"""
    <div class="alerta-sonido-box">
        <h3>{titulo}</h3>
        <p>{mensaje}</p>
    </div>
    """, unsafe_allow_html=True)

    components.html(f"""
    <script>
    function beepExpressNow() {{
        try {{
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            const audioCtx = new AudioContext();

            const osc1 = audioCtx.createOscillator();
            const gain1 = audioCtx.createGain();

            osc1.type = "square";
            osc1.frequency.setValueAtTime(950, audioCtx.currentTime);
            gain1.gain.setValueAtTime(0.45, audioCtx.currentTime);

            osc1.connect(gain1);
            gain1.connect(audioCtx.destination);

            osc1.start();
            osc1.stop(audioCtx.currentTime + 0.55);

            setTimeout(() => {{
                try {{
                    const osc2 = audioCtx.createOscillator();
                    const gain2 = audioCtx.createGain();

                    osc2.type = "square";
                    osc2.frequency.setValueAtTime(1200, audioCtx.currentTime);
                    gain2.gain.setValueAtTime(0.45, audioCtx.currentTime);

                    osc2.connect(gain2);
                    gain2.connect(audioCtx.destination);

                    osc2.start();
                    osc2.stop(audioCtx.currentTime + 0.55);
                }} catch(e) {{}}
            }}, 650);

            setTimeout(() => {{
                try {{
                    const osc3 = audioCtx.createOscillator();
                    const gain3 = audioCtx.createGain();

                    osc3.type = "square";
                    osc3.frequency.setValueAtTime(800, audioCtx.currentTime);
                    gain3.gain.setValueAtTime(0.45, audioCtx.currentTime);

                    osc3.connect(gain3);
                    gain3.connect(audioCtx.destination);

                    osc3.start();
                    osc3.stop(audioCtx.currentTime + 0.55);
                }} catch(e) {{}}
            }}, 1300);

        }} catch(e) {{
            console.log("No se pudo reproducir sonido:", e);
        }}
    }}

    beepExpressNow();

    if (navigator.vibrate) {{
        navigator.vibrate([400, 180, 400, 180, 400]);
    }}

    if ("Notification" in window && Notification.permission === "granted") {{
        new Notification("{titulo}", {{
            body: "{mensaje}"
        }});
    }}
    </script>
    """, height=0)

    st.toast(mensaje)


def activar_refresco_automatico():
    """
    Refresca la app para revisar cambios.
    Se deja en 60 segundos para no saturar Google Sheets.
    """
    st_autorefresh(
        interval=60000,
        key="refresco_automatico_notificaciones"
    )


# =========================================================
# COMPONENTES VISUALES
# =========================================================

def hero():
    st.markdown("""
    <div class="hero">
        <h1>🛵 Express <span>Local</span></h1>
        <p>Solicita taxi, express, carga y camión de forma rápida y segura.</p>
    </div>
    """, unsafe_allow_html=True)


def promo_carousel():
    st.markdown("""
    <div class="promo-carousel">
        <div>
            <h2>🔥 Promociones y servicios destacados</h2>
            <p>Este espacio puede mostrar restaurantes, comercios, ofertas y servicios activos.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_menu():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 20px 0;">
            <h1 style="font-size: 28px; line-height: 1.1;">
                🛵 Express<br>
                <span style="color:#fb923c;">Local</span>
            </h1>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.tipo == "Usuario" and st.session_state.usuario_actual:
            u = st.session_state.usuario_actual
            st.success(f"Usuario: {u['Usuario']}")

        if st.session_state.tipo == "Colaborador" and st.session_state.colaborador_actual:
            c = st.session_state.colaborador_actual
            st.success(f"{c['Servicio']}: {c['Usuario']}")

        if st.session_state.tipo == "Administrador":
            st.success("Administrador activo")

        st.divider()

        if st.button("🏠 Inicio", use_container_width=True):
            if st.session_state.tipo == "Usuario":
                st.session_state.pagina = "panel_usuario"
            elif st.session_state.tipo == "Colaborador":
                st.session_state.pagina = "panel_colaborador"
            elif st.session_state.tipo == "Administrador":
                st.session_state.pagina = "panel_admin"
            else:
                st.session_state.pagina = "login"

            st.rerun()

        if st.session_state.tipo == "Usuario":
            if st.button("👤 Cambiar mis datos", use_container_width=True):
                st.session_state.pagina = "editar_usuario"
                st.rerun()

        st.link_button(
            "💬 Ayuda WhatsApp",
            link_whatsapp(
                ADMIN_WHATSAPP,
                "Hola, necesito ayuda con la plataforma Express Local."
            ),
            use_container_width=True
        )

        if st.session_state.tipo == "Administrador":
            st.divider()
            st.caption("CLAVES DEMO")
            st.write("Para colaboradores")

            for servicio, claves in CLAVES_COLABORADOR.items():
                icono = SERVICIOS[servicio]["icono"]
                st.write(f"**{icono} {servicio}**")
                st.caption(f"{claves[0]} - {claves[-1]}")

        st.divider()

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()


# =========================================================
# FORMULARIOS DE USUARIO
# =========================================================

def formulario_login_usuario():
    st.markdown("""
    <h3>🚪 Ingreso de usuario</h3>
    <p class="small-note">Ingresa con tu usuario y contraseña para solicitar servicios.</p>
    """, unsafe_allow_html=True)

    with st.form("form_login_usuario"):
        usuario = st.text_input("Nombre de usuario", key="login_user_user")
        clave = st.text_input("Clave", type="password", key="login_user_pass")
        ingresar = st.form_submit_button("Ingresar como usuario")

    if ingresar:
        encontrado = buscar_usuario_login(usuario, clave)

        if encontrado:
            st.session_state.usuario_actual = encontrado
            st.session_state.tipo = "Usuario"
            st.session_state.pagina = "panel_usuario"
            st.session_state.ultimo_total_aceptadas_usuario = 0
            st.session_state.ultima_alerta_usuario_ids = ""
            st.rerun()
        else:
            st.error("Usuario o clave incorrecta.")


def formulario_registro_usuario():
    st.markdown("""
    <h3>👤 Registro nuevo de usuario</h3>
    <p class="small-note">Crea tu cuenta como usuario para comenzar.</p>
    """, unsafe_allow_html=True)

    st.caption(f"Demo: máximo {LIMITE_USUARIOS_DEMO} usuarios registrados.")

    with st.form("form_registro_usuario"):
        c1, c2, c3 = st.columns(3)

        with c1:
            nombre = st.text_input("Nombre")

        with c2:
            apellido1 = st.text_input("Primer apellido")

        with c3:
            apellido2 = st.text_input("Segundo apellido")

        telefono = st.text_input("Número de teléfono Costa Rica")
        usuario = st.text_input("Nombre de usuario")
        clave = st.text_input(
            "Clave",
            type="password",
            help="Puede usar números, mayúsculas y minúsculas."
        )

        guardar = st.form_submit_button("Registrarme como usuario")

    if guardar:
        if total_usuarios_registrados() >= LIMITE_USUARIOS_DEMO:
            st.error(f"El demo permite registrar máximo {LIMITE_USUARIOS_DEMO} usuarios.")
            return

        if not all([nombre, apellido1, apellido2, telefono, usuario, clave]):
            st.error("Debe completar todos los espacios.")
            return

        if usuario_existe(usuario):
            st.error("Ese nombre de usuario ya existe. Use otro.")
            return

        nuevo = registrar_usuario(nombre, apellido1, apellido2, telefono, usuario, clave)

        st.success("Usuario creado correctamente. Ya puede ingresar.")
        st.session_state.usuario_actual = nuevo
        st.session_state.tipo = "Usuario"
        st.session_state.pagina = "panel_usuario"
        st.session_state.ultimo_total_aceptadas_usuario = 0
        st.session_state.ultima_alerta_usuario_ids = ""
        st.rerun()


# =========================================================
# FORMULARIOS DE COLABORADOR
# =========================================================

def formulario_login_colaborador():
    st.markdown("""
    <h3>🛠️ Ingreso de colaborador</h3>
    <p class="small-note">Ingresa con tus credenciales para aceptar solicitudes.</p>
    """, unsafe_allow_html=True)

    with st.form("form_login_colaborador"):
        usuario = st.text_input("Nombre de usuario", key="login_col_user")
        clave = st.text_input("Clave", type="password", key="login_col_pass")
        ingresar = st.form_submit_button("Ingresar como colaborador")

    if ingresar:
        encontrado = buscar_colaborador_login(usuario, clave)

        if encontrado:
            st.session_state.colaborador_actual = encontrado
            st.session_state.tipo = "Colaborador"
            st.session_state.pagina = "panel_colaborador"
            st.session_state.ultimo_total_pendientes_colaborador = 0
            st.session_state.ultima_alerta_colaborador_ids = ""
            st.rerun()
        else:
            st.error("Usuario o clave incorrecta.")


def formulario_registro_colaborador():
    st.markdown("""
    <h3>🧰 Registro nuevo de colaborador</h3>
    <p class="small-note">Regístrate como colaborador para brindar servicios.</p>
    """, unsafe_allow_html=True)

    st.caption(f"Demo: máximo {LIMITE_COLABORADORES_POR_SERVICIO} colaboradores por servicio.")

    with st.form("form_registro_colaborador"):
        c1, c2, c3 = st.columns(3)

        with c1:
            nombre = st.text_input("Nombre", key="col_nombre")

        with c2:
            apellido1 = st.text_input("Primer apellido", key="col_ap1")

        with c3:
            apellido2 = st.text_input("Segundo apellido", key="col_ap2")

        telefono = st.text_input("Número de teléfono Costa Rica", key="col_tel")
        servicio = st.selectbox("Servicio que brindará", list(SERVICIOS.keys()))
        codigo = st.text_input("Clave autorizada por el coordinador", type="password")
        usuario = st.text_input("Nombre de usuario", key="col_user")
        clave = st.text_input(
            "Clave personal",
            type="password",
            help="Puede usar números, mayúsculas y minúsculas.",
            key="col_pass"
        )

        guardar = st.form_submit_button("Registrarme como colaborador")

    if guardar:
        if not all([nombre, apellido1, apellido2, telefono, servicio, codigo, usuario, clave]):
            st.error("Debe completar todos los espacios.")
            return

        if codigo.strip() not in CLAVES_COLABORADOR[servicio]:
            st.error("La clave del coordinador no corresponde al servicio seleccionado.")
            return

        if total_colaboradores_servicio(servicio) >= LIMITE_COLABORADORES_POR_SERVICIO:
            st.error(f"Ya existen {LIMITE_COLABORADORES_POR_SERVICIO} colaboradores registrados para {servicio}.")
            return

        if usuario_existe(usuario):
            st.error("Ese nombre de usuario ya existe. Use otro.")
            return

        nuevo = registrar_colaborador(nombre, apellido1, apellido2, telefono, usuario, clave, servicio)

        st.success("Colaborador creado correctamente.")
        st.session_state.colaborador_actual = nuevo
        st.session_state.tipo = "Colaborador"
        st.session_state.pagina = "panel_colaborador"
        st.session_state.ultimo_total_pendientes_colaborador = 0
        st.session_state.ultima_alerta_colaborador_ids = ""
        st.rerun()
# =========================================================
# PARTE 4 / 5
# PÁGINAS PRINCIPALES: LOGIN, USUARIO, SERVICIO Y COLABORADOR
# =========================================================

def pagina_login():
    hero()

    st.markdown("""
    <style>
    .admin-admin-box {
        margin-top: 10px;
        margin-bottom: 6px;
    }

    .admin-admin-box button {
        white-space: nowrap !important;
        word-break: normal !important;
        overflow-wrap: normal !important;
        min-width: 190px !important;
        height: 44px !important;
        padding: 8px 18px !important;
        border-radius: 999px !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        line-height: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="text-align:center; max-width: 980px; margin: 0 auto 24px auto;">
        <h2 style="font-size:34px; margin-bottom:8px;">Acceso principal</h2>
        <p style="color:#64748b !important; font-size:17px;">
            Seleccione si desea ingresar como usuario o colaborador. También puede registrarse por primera vez.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👤 Usuarios", "🛠️ Colaboradores"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            formulario_login_usuario()

        with col2:
            formulario_registro_usuario()

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            formulario_login_colaborador()

        with col2:
            formulario_registro_colaborador()

    st.markdown("<br>", unsafe_allow_html=True)

    col_espacio, col_admin = st.columns([7, 2])

    with col_admin:
        st.markdown('<div class="admin-admin-box">', unsafe_allow_html=True)

        if st.button("Administrador", key="btn_admin_oculto", use_container_width=True):
            st.session_state.pagina = "admin_login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


def pagina_panel_usuario():
    activar_refresco_automatico()
    sidebar_menu()
    boton_activar_sonido()

    usuario = st.session_state.usuario_actual

    promo_carousel()

    st.markdown(f"""
    <div class="card">
        <h2 style="font-size:32px;">Hola, {usuario['Nombre']} 👋</h2>
        <p style="color:#64748b !important;">
            Seleccione el servicio que necesita. La solicitud será visible para los colaboradores disponibles de ese servicio.
        </p>
    </div>
    """, unsafe_allow_html=True)

    solicitudes = solicitudes_usuario(usuario["ID"])

    # =====================================================
    # ALERTA PARA USUARIO
    # Suena SOLO cuando aparece una solicitud NUEVA en estado Aceptado.
    # No suena cuando finalizan.
    # =====================================================

    ids_aceptadas_actuales = set(
        s["ID"] for s in solicitudes
        if s["Estado"] == "Aceptado"
    )

    ids_aceptadas_anteriores_txt = st.session_state.get(
        "ultima_alerta_usuario_ids",
        ""
    )

    ids_aceptadas_anteriores = set(
        ids_aceptadas_anteriores_txt.split(",")
    ) if ids_aceptadas_anteriores_txt else set()

    ids_nuevas_aceptadas = ids_aceptadas_actuales - ids_aceptadas_anteriores

    if not st.session_state.get("alerta_usuario_inicializada", False):
        st.session_state.alerta_usuario_inicializada = True
    else:
        if ids_nuevas_aceptadas:
            reproducir_alerta(
                "🔔 Solicitud aceptada",
                "Un colaborador aceptó una de sus solicitudes."
            )

    st.session_state.ultima_alerta_usuario_ids = ",".join(
        sorted(ids_aceptadas_actuales)
    )

    st.session_state.ultimo_total_aceptadas_usuario = len(
        ids_aceptadas_actuales
    )

    cols = st.columns(4)

    for i, (servicio, info) in enumerate(SERVICIOS.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="service-card" style="background: linear-gradient(135deg, {info['color1']}, {info['color2']});">
                <h2>{info['icono']}<br>{servicio}</h2>
                <p>{info['descripcion']}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"Solicitar {servicio}",
                key=f"sol_{servicio}",
                use_container_width=True
            ):
                st.session_state.servicio_seleccionado = servicio
                st.session_state.pagina = "servicio_usuario"
                st.rerun()

    st.divider()
    st.subheader("📋 Mis solicitudes")

    if not solicitudes:
        st.info("Todavía no tiene solicitudes registradas.")
    else:
        for s in reversed(solicitudes):
            st.markdown(f"""
            <div class="card">
                <h3>{s['Servicio']} · Solicitud #{s['ID']}</h3>
                <p><b>Fecha:</b> {s['Fecha']}</p>
                <p><b>Estado:</b> {badge_estado(s['Estado'])}</p>
                <p><b>Detalle:</b> {s['Detalle']}</p>
                <p><b>Colaborador:</b> {s['Colaborador'] if s['Colaborador'] else 'Pendiente de aceptación'}</p>
            </div>
            """, unsafe_allow_html=True)

            if s["Estado"] == "Aceptado" and s["Teléfono colaborador"]:
                mensaje = (
                    f"Hola {s['Colaborador']}, soy {s['Cliente']}. "
                    f"Tengo la solicitud #{s['ID']} de {s['Servicio']}. "
                    "Quisiera coordinar los detalles por este medio."
                )

                st.link_button(
                    "💬 Chatear con colaborador por WhatsApp",
                    link_whatsapp(s["Teléfono colaborador"], mensaje),
                    use_container_width=True
                )


def pagina_servicio_usuario():
    sidebar_menu()

    usuario = st.session_state.usuario_actual
    servicio = st.session_state.servicio_seleccionado

    if not servicio:
        st.session_state.pagina = "panel_usuario"
        st.rerun()

    info = SERVICIOS[servicio]

    st.markdown(f"""
    <div class="service-card" style="background: linear-gradient(135deg, {info['color1']}, {info['color2']}); min-height:150px;">
        <h2>{info['icono']} {servicio}</h2>
        <p>{info['descripcion']}</p>
    </div>
    """, unsafe_allow_html=True)

    colaboradores = leer_registros(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES
    )

    colaboradores_servicio = [
        c for c in colaboradores
        if c["Servicio"] == servicio
    ]

    disponibles = [
        c for c in colaboradores_servicio
        if c["Estado"] == "Disponible"
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric("Colaboradores registrados", len(colaboradores_servicio))
    c2.metric("Disponibles", len(disponibles))
    c3.metric("Ocupados / fuera", len(colaboradores_servicio) - len(disponibles))

    st.subheader("🚦 Estado de colaboradores")

    if not colaboradores_servicio:
        st.warning("Aún no hay colaboradores registrados para este servicio.")
    else:
        for c in colaboradores_servicio:
            nombre = (
                f'{c["Nombre"]} '
                f'{c["Primer apellido"]} '
                f'{c["Segundo apellido"]}'
            ).strip()

            st.markdown(f"""
            <div class="card">
                <h3>{nombre}</h3>
                <p><b>Servicio:</b> {c['Servicio']}</p>
                <p><b>Estado:</b> {badge_estado(c['Estado'])}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📲 Hacer llamado a colaboradores disponibles")

    with st.form("crear_solicitud_servicio"):
        detalle = st.text_area(
            "Detalle de la solicitud",
            placeholder="Ejemplo: necesito un taxi hacia el centro / retirar comida en restaurante / trasladar una caja..."
        )

        enviar = st.form_submit_button(
            f"Hacer llamado de {servicio}"
        )

    if enviar:
        if not disponibles:
            st.error("No hay colaboradores disponibles en este momento.")
            return

        if not detalle.strip():
            st.error("Debe indicar el detalle de la solicitud.")
            return

        nueva = crear_solicitud(
            servicio,
            usuario,
            detalle
        )

        st.success(
            f"Solicitud enviada. Código: {nueva['ID']}. Espere a que un colaborador la acepte."
        )

        st.session_state.pagina = "panel_usuario"
        st.rerun()

    if st.button("⬅️ Volver a servicios", use_container_width=True):
        st.session_state.pagina = "panel_usuario"
        st.rerun()


def pagina_panel_colaborador():
    activar_refresco_automatico()
    sidebar_menu()
    boton_activar_sonido()

    colaborador = st.session_state.colaborador_actual
    servicio = colaborador["Servicio"]
    info = SERVICIOS[servicio]

    st.markdown(f"""
    <div class="service-card" style="background: linear-gradient(135deg, {info['color1']}, {info['color2']}); min-height:150px;">
        <h2>{info['icono']} Panel de {servicio}</h2>
        <p>Administre su estado y acepte solicitudes pendientes.</p>
    </div>
    """, unsafe_allow_html=True)

    nombre = (
        f'{colaborador["Nombre"]} '
        f'{colaborador["Primer apellido"]} '
        f'{colaborador["Segundo apellido"]}'
    ).strip()

    st.markdown(f"""
    <div class="card">
        <h2>{nombre}</h2>
        <p><b>Teléfono:</b> {colaborador['Teléfono']}</p>
        <p><b>Servicio:</b> {servicio}</p>
        <p><b>Estado actual:</b> {badge_estado(colaborador['Estado'])}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🚦 Cambiar estado")

    c1, c2 = st.columns([2, 1])

    with c1:
        nuevo_estado = st.selectbox(
            "Estado",
            ["Disponible", "Ocupado", "Fuera de servicio"],
            index=["Disponible", "Ocupado", "Fuera de servicio"].index(colaborador["Estado"])
            if colaborador["Estado"] in ["Disponible", "Ocupado", "Fuera de servicio"] else 0
        )

    with c2:
        st.write("")
        st.write("")

        if st.button("Actualizar estado", use_container_width=True):
            actualizado = actualizar_estado_colaborador(
                colaborador,
                nuevo_estado
            )

            if actualizado:
                st.success("Estado actualizado.")
                st.rerun()

    st.divider()
    st.subheader("🔔 Solicitudes pendientes para mi servicio")

    if colaborador["Estado"] != "Disponible":
        st.warning("Para aceptar nuevas solicitudes debe estar en estado Disponible.")
        pendientes = []
    else:
        pendientes = solicitudes_pendientes_servicio(servicio)

    # =====================================================
    # ALERTA PARA COLABORADOR
    # Suena SOLO cuando aparece una solicitud NUEVA pendiente.
    # No suena cuando desaparece porque otro colaborador aceptó.
    # =====================================================

    ids_pendientes_actuales = set(
        s["ID"] for s in pendientes
    )

    ids_pendientes_anteriores_txt = st.session_state.get(
        "ultima_alerta_colaborador_ids",
        ""
    )

    ids_pendientes_anteriores = set(
        ids_pendientes_anteriores_txt.split(",")
    ) if ids_pendientes_anteriores_txt else set()

    ids_nuevas_pendientes = ids_pendientes_actuales - ids_pendientes_anteriores

    if not st.session_state.get("alerta_colaborador_inicializada", False):
        st.session_state.alerta_colaborador_inicializada = True
    else:
        if ids_nuevas_pendientes:
            reproducir_alerta(
                "🔔 Nueva solicitud",
                f"Hay una nueva solicitud pendiente para {servicio}."
            )

    st.session_state.ultima_alerta_colaborador_ids = ",".join(
        sorted(ids_pendientes_actuales)
    )

    st.session_state.ultimo_total_pendientes_colaborador = len(
        ids_pendientes_actuales
    )

    if not pendientes:
        st.info("No hay solicitudes pendientes para este servicio.")
    else:
        for s in reversed(pendientes):
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['ID']} · {s['Servicio']}</h3>
                <p><b>Fecha:</b> {s['Fecha']}</p>
                <p><b>Cliente:</b> {s['Cliente']}</p>
                <p><b>Detalle:</b> {s['Detalle']}</p>
                <p><b>Estado:</b> {badge_estado(s['Estado'])}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"✅ Aceptar solicitud #{s['ID']}",
                key=f"aceptar_{s['ID']}",
                use_container_width=True
            ):
                aceptada = aceptar_solicitud(
                    s,
                    colaborador
                )

                if aceptada:
                    st.success("Solicitud aceptada. Ahora el usuario podrá contactarlo por WhatsApp.")
                    st.rerun()
                else:
                    st.warning("La solicitud ya no está disponible.")

    st.divider()
    st.subheader("📌 Mis servicios aceptados")

    aceptadas = solicitudes_colaborador(
        colaborador["ID"]
    )

    if not aceptadas:
        st.info("Aún no tiene solicitudes aceptadas.")
    else:
        for s in reversed(aceptadas):
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['ID']} · {s['Servicio']}</h3>
                <p><b>Cliente:</b> {s['Cliente']}</p>
                <p><b>Teléfono cliente:</b> {s['Teléfono cliente']}</p>
                <p><b>Detalle:</b> {s['Detalle']}</p>
                <p><b>Estado:</b> {badge_estado(s['Estado'])}</p>
            </div>
            """, unsafe_allow_html=True)

            mensaje = (
                f"Hola {s['Cliente']}, soy {s['Colaborador']}, "
                f"acepté su solicitud #{s['ID']} de {s['Servicio']}. "
                "Coordinemos los detalles por este medio."
            )

            st.link_button(
                "💬 Chatear con usuario por WhatsApp",
                link_whatsapp(
                    s["Teléfono cliente"],
                    mensaje
                ),
                use_container_width=True
            )

            if s["Estado"] != "Finalizado":
                if st.button(
                    f"🏁 Finalizar solicitud #{s['ID']}",
                    key=f"fin_{s['ID']}",
                    use_container_width=True
                ):
                    finalizar_solicitud(
                        s,
                        colaborador
                    )

                    st.success("Solicitud finalizada.")
                    st.rerun()
                    # =========================================================
# PARTE 5 / 5
# EDITAR USUARIO, ADMINISTRADOR Y EJECUCIÓN PRINCIPAL
# =========================================================

def pagina_editar_usuario():
    """
    Permite al usuario actualizar sus datos básicos.
    """
    sidebar_menu()

    usuario = st.session_state.usuario_actual

    st.subheader("👤 Cambiar datos de usuario")
    st.info("Por seguridad del demo, aquí se actualizan nombre, apellidos y teléfono. El usuario y clave quedan igual.")

    with st.form("editar_usuario"):
        nombre = st.text_input("Nombre", value=usuario["Nombre"])
        apellido1 = st.text_input("Primer apellido", value=usuario["Primer apellido"])
        apellido2 = st.text_input("Segundo apellido", value=usuario["Segundo apellido"])
        telefono = st.text_input("Teléfono", value=usuario["Teléfono"])

        guardar = st.form_submit_button("Guardar cambios")

    if guardar:
        cambios = {
            "Nombre": limpiar_texto(nombre),
            "Primer apellido": limpiar_texto(apellido1),
            "Segundo apellido": limpiar_texto(apellido2),
            "Teléfono": telefono_whatsapp_cr(telefono)
        }

        actualizar_varias_celdas(
            HOJA_USUARIOS,
            ENCABEZADOS_USUARIOS,
            int(usuario["_fila"]),
            cambios
        )

        usuario.update(cambios)

        st.session_state.usuario_actual = usuario
        st.success("Datos actualizados.")
        st.session_state.pagina = "panel_usuario"
        st.rerun()


def pagina_admin_login():
    """
    Pantalla privada de acceso administrador.
    """
    hero()

    st.markdown("""
    <div class="card" style="max-width:620px; margin: 0 auto;">
        <h2 style="font-size:32px;">🔐 Acceso administrador</h2>
        <p style="color:#64748b !important;">
            Ingrese las credenciales administrativas para gestionar usuarios,
            colaboradores y revisar el dashboard.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("form_admin_login"):
        usuario = st.text_input("Usuario administrador")
        clave = st.text_input("Contraseña", type="password")

        ingresar = st.form_submit_button("Ingresar")

    if ingresar:
        if usuario == ADMIN_USUARIO and clave == ADMIN_CLAVE:
            st.session_state.admin_autenticado = True
            st.session_state.tipo = "Administrador"
            st.session_state.pagina = "panel_admin"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    if st.button("⬅️ Volver", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()


def pagina_panel_admin():
    """
    Panel administrador.
    Incluye dashboard, estadísticas, solicitudes,
    eliminación de usuarios y eliminación de colaboradores.
    """
    if not st.session_state.get("admin_autenticado"):
        st.session_state.pagina = "admin_login"
        st.rerun()

    sidebar_menu()

    st.markdown("""
    <div class="card">
        <h1 style="margin-bottom:4px;">🛡️ Panel Administrador</h1>
        <p style="color:#64748b !important;">
            Área privada para control general de usuarios, colaboradores y actividad del sistema.
        </p>
    </div>
    """, unsafe_allow_html=True)

    usuarios = leer_registros(HOJA_USUARIOS, ENCABEZADOS_USUARIOS)
    colaboradores = leer_registros(HOJA_COLABORADORES, ENCABEZADOS_COLABORADORES)
    solicitudes = leer_registros(HOJA_SOLICITUDES, ENCABEZADOS_SOLICITUDES)

    st.subheader("📊 Dashboard general")

    total_solicitudes = len(solicitudes)
    finalizadas = [s for s in solicitudes if s["Estado"] == "Finalizado"]
    pendientes = [s for s in solicitudes if s["Estado"] == "Pendiente"]
    aceptadas = [s for s in solicitudes if s["Estado"] == "Aceptado"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Usuarios registrados", len(usuarios))
    c2.metric("Colaboradores", len(colaboradores))
    c3.metric("Solicitudes totales", total_solicitudes)
    c4.metric("Finalizadas", len(finalizadas))

    c5, c6, c7 = st.columns(3)

    c5.metric("Pendientes", len(pendientes))
    c6.metric("Aceptadas", len(aceptadas))
    c7.metric("Servicios disponibles", len(SERVICIOS))

    st.divider()
    st.subheader("🚕 Servicios más solicitados")

    if solicitudes:
        df_solicitudes = pd.DataFrame(solicitudes)

        conteo_servicios = (
            df_solicitudes["Servicio"]
            .value_counts()
            .reset_index()
        )

        conteo_servicios.columns = ["Servicio", "Cantidad"]

        st.dataframe(conteo_servicios, use_container_width=True)
        st.bar_chart(conteo_servicios.set_index("Servicio"))
    else:
        st.info("Aún no hay solicitudes registradas.")

    st.divider()
    st.subheader("🛠️ Actividad por colaborador / trabajador")

    if solicitudes:
        actividad_colaboradores = {}

        for s in solicitudes:
            col_id = s.get("Colaborador ID", "")
            col_nombre = s.get("Colaborador", "")
            servicio = s.get("Servicio", "")
            estado = s.get("Estado", "")

            if col_id and col_nombre:
                if col_id not in actividad_colaboradores:
                    actividad_colaboradores[col_id] = {
                        "Colaborador": col_nombre,
                        "Servicio principal": servicio,
                        "Total servicios aceptados": 0,
                        "Servicios finalizados": 0,
                        "Servicios activos": 0
                    }

                actividad_colaboradores[col_id]["Total servicios aceptados"] += 1

                if estado == "Finalizado":
                    actividad_colaboradores[col_id]["Servicios finalizados"] += 1

                if estado == "Aceptado":
                    actividad_colaboradores[col_id]["Servicios activos"] += 1

        if actividad_colaboradores:
            df_colaboradores = pd.DataFrame(list(actividad_colaboradores.values()))

            st.dataframe(df_colaboradores, use_container_width=True)
            st.bar_chart(df_colaboradores.set_index("Colaborador")["Servicios finalizados"])
        else:
            st.info("Todavía no hay colaboradores con servicios aceptados.")
    else:
        st.info("No hay información de colaboradores todavía.")

    st.divider()
    st.subheader("👤 Clientes más activos")

    if solicitudes:
        actividad_clientes = {}

        for s in solicitudes:
            cliente_id = s.get("Cliente ID", "")
            cliente = s.get("Cliente", "")
            servicio = s.get("Servicio", "")

            if cliente_id:
                if cliente_id not in actividad_clientes:
                    actividad_clientes[cliente_id] = {
                        "Cliente": cliente,
                        "Total solicitudes": 0,
                        "Servicios solicitados": {}
                    }

                actividad_clientes[cliente_id]["Total solicitudes"] += 1

                actividad_clientes[cliente_id]["Servicios solicitados"][servicio] = (
                    actividad_clientes[cliente_id]["Servicios solicitados"].get(servicio, 0) + 1
                )

        tabla_clientes = []

        for datos in actividad_clientes.values():
            servicios_txt = ", ".join(
                [f"{serv}: {cant}" for serv, cant in datos["Servicios solicitados"].items()]
            )

            tabla_clientes.append({
                "Cliente": datos["Cliente"],
                "Total solicitudes": datos["Total solicitudes"],
                "Servicios solicitados": servicios_txt
            })

        df_clientes = pd.DataFrame(tabla_clientes).sort_values(
            by="Total solicitudes",
            ascending=False
        )

        st.dataframe(df_clientes, use_container_width=True)
        st.bar_chart(df_clientes.set_index("Cliente")["Total solicitudes"])
    else:
        st.info("Todavía no hay clientes con solicitudes.")

    st.divider()
    st.subheader("📋 Solicitudes registradas")

    if solicitudes:
        df_todas = pd.DataFrame(solicitudes)

        columnas_mostrar = [
            "ID", "Fecha", "Servicio", "Cliente",
            "Teléfono cliente", "Detalle", "Estado",
            "Colaborador", "Teléfono colaborador"
        ]

        columnas_existentes = [
            c for c in columnas_mostrar
            if c in df_todas.columns
        ]

        st.dataframe(
            df_todas[columnas_existentes],
            use_container_width=True
        )
    else:
        st.info("No hay solicitudes registradas.")

    st.divider()
    st.subheader("🗑️ Eliminar usuarios")

    st.warning(
        "Al eliminar un usuario se elimina de la hoja Usuarios. "
        "Sus solicitudes anteriores quedan como historial."
    )

    if usuarios:
        for u in usuarios:
            nombre = (
                f'{u["Nombre"]} '
                f'{u["Primer apellido"]} '
                f'{u["Segundo apellido"]}'
            ).strip()

            with st.expander(f"👤 {nombre} | Usuario: {u['Usuario']}"):
                st.write(f"**ID:** {u['ID']}")
                st.write(f"**Teléfono:** {u['Teléfono']}")
                st.write(f"**Fecha de registro:** {u['Fecha']}")

                confirmar = st.checkbox(
                    f"Confirmo eliminar usuario {u['Usuario']}",
                    key=f"check_user_{u['ID']}"
                )

                if st.button(
                    f"Eliminar usuario {u['ID']}",
                    key=f"del_user_{u['ID']}"
                ):
                    if confirmar:
                        eliminar_fila(
                            HOJA_USUARIOS,
                            ENCABEZADOS_USUARIOS,
                            u["_fila"]
                        )

                        st.success("Usuario eliminado correctamente.")
                        st.rerun()
                    else:
                        st.error("Debe marcar la confirmación antes de eliminar.")
    else:
        st.info("No hay usuarios registrados.")

    st.divider()
    st.subheader("🗑️ Eliminar colaboradores / trabajadores")

    st.warning(
        "Al eliminar un colaborador se elimina de la hoja Datos generales. "
        "Sus servicios anteriores quedan como historial."
    )

    if colaboradores:
        for c in colaboradores:
            nombre = (
                f'{c["Nombre"]} '
                f'{c["Primer apellido"]} '
                f'{c["Segundo apellido"]}'
            ).strip()

            with st.expander(
                f"🛠️ {nombre} | {c['Servicio']} | Usuario: {c['Usuario']}"
            ):
                st.write(f"**ID:** {c['ID']}")
                st.write(f"**Teléfono:** {c['Teléfono']}")
                st.write(f"**Servicio:** {c['Servicio']}")
                st.write(f"**Estado actual:** {c['Estado']}")
                st.write(f"**Fecha de registro:** {c['Fecha']}")

                confirmar = st.checkbox(
                    f"Confirmo eliminar colaborador {c['Usuario']}",
                    key=f"check_col_{c['ID']}"
                )

                if st.button(
                    f"Eliminar colaborador {c['ID']}",
                    key=f"del_col_{c['ID']}"
                ):
                    if confirmar:
                        eliminar_fila(
                            HOJA_COLABORADORES,
                            ENCABEZADOS_COLABORADORES,
                            c["_fila"]
                        )

                        st.success("Colaborador eliminado correctamente.")
                        st.rerun()
                    else:
                        st.error("Debe marcar la confirmación antes de eliminar.")
    else:
        st.info("No hay colaboradores registrados.")


# =========================================================
# EJECUCIÓN PRINCIPAL DE LA APP
# =========================================================

inicializar_estado()

try:
    if st.session_state.pagina == "login":
        pagina_login()

    elif st.session_state.pagina == "panel_usuario":
        pagina_panel_usuario()

    elif st.session_state.pagina == "servicio_usuario":
        pagina_servicio_usuario()

    elif st.session_state.pagina == "panel_colaborador":
        pagina_panel_colaborador()

    elif st.session_state.pagina == "editar_usuario":
        pagina_editar_usuario()

    elif st.session_state.pagina == "admin_login":
        pagina_admin_login()

    elif st.session_state.pagina == "panel_admin":
        pagina_panel_admin()

    else:
        st.session_state.pagina = "login"
        st.rerun()

except Exception as e:
    st.error("Ocurrió un error en la aplicación.")
    st.exception(e)
