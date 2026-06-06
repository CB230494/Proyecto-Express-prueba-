# =========================================================
# PARTE 1 / 5
# IMPORTACIONES, CONFIGURACIÓN GENERAL Y ESTILO VISUAL
# =========================================================

import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid
import re
from urllib.parse import quote
from streamlit_autorefresh import st_autorefresh

# =========================================================
# CONFIGURACIÓN GENERAL DE STREAMLIT
# =========================================================

st.set_page_config(
    page_title="Express Local",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CONFIGURACIÓN DE GOOGLE SHEETS
# =========================================================

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1LSnqaX5qDsw1Tq-qdknohQPr6XX09JnqAM0-4CiqC0E/edit?gid=0#gid=0"

HOJA_USUARIOS = "Usuarios"
HOJA_COLABORADORES = "Datos generales"
HOJA_SOLICITUDES = "Solicitudes"

# =========================================================
# DATOS GENERALES DEL SISTEMA
# =========================================================

ADMIN_WHATSAPP = "50663009645"

ADMIN_USUARIO = "administrador123"
ADMIN_CLAVE = "123456"

LIMITE_USUARIOS_DEMO = 6
LIMITE_COLABORADORES_POR_SERVICIO = 5

# =========================================================
# CATÁLOGO DE SERVICIOS
# =========================================================

SERVICIOS = {
    "Taxi": {
        "icono": "🚕",
        "color1": "#facc15",
        "color2": "#f97316",
        "descripcion": "Viajes locales, traslados rápidos y servicio puerta a puerta.",
        "mensaje": "Hola, necesito ayuda para solicitar un taxi."
    },
    "Express": {
        "icono": "🛵",
        "color1": "#ef4444",
        "color2": "#fb7185",
        "descripcion": "Mandados, compras, documentos y entregas rápidas.",
        "mensaje": "Hola, necesito ayuda para solicitar un express."
    },
    "Carga": {
        "icono": "📦",
        "color1": "#2563eb",
        "color2": "#06b6d4",
        "descripcion": "Traslado de paquetes, compras grandes o artículos medianos.",
        "mensaje": "Hola, necesito ayuda para solicitar servicio de carga."
    },
    "Camión": {
        "icono": "🚚",
        "color1": "#16a34a",
        "color2": "#22c55e",
        "descripcion": "Mudanzas, materiales, carga pesada o transporte especial.",
        "mensaje": "Hola, necesito ayuda para solicitar un camión."
    }
}

# =========================================================
# CLAVES DEMO PARA COLABORADORES
# =========================================================

CLAVES_COLABORADOR = {
    "Taxi": ["TAXI01", "TAXI02", "TAXI03", "TAXI04", "TAXI05", "TAXI06"],
    "Express": ["EXP01", "EXP02", "EXP03", "EXP04", "EXP05", "EXP06"],
    "Carga": ["CARGA01", "CARGA02", "CARGA03", "CARGA04", "CARGA05", "CARGA06"],
    "Camión": ["CAMION01", "CAMION02", "CAMION03", "CAMION04", "CAMION05", "CAMION06"],
}

# =========================================================
# ENCABEZADOS DE LAS HOJAS
# =========================================================

ENCABEZADOS_USUARIOS = [
    "ID", "Nombre", "Primer apellido", "Segundo apellido",
    "Teléfono", "Usuario", "Clave", "Tipo", "Fecha"
]

ENCABEZADOS_COLABORADORES = [
    "ID", "Nombre", "Primer apellido", "Segundo apellido",
    "Teléfono", "Usuario", "Clave", "Tipo", "Servicio", "Estado", "Fecha"
]

ENCABEZADOS_SOLICITUDES = [
    "ID", "Fecha", "Servicio", "Cliente ID", "Cliente",
    "Teléfono cliente", "Detalle", "Estado", "Colaborador ID",
    "Colaborador", "Teléfono colaborador"
]

# =========================================================
# ESTILO VISUAL MODERNO
# =========================================================

st.markdown("""
<style>

/* =========================================================
   FONDO GENERAL
   ========================================================= */

:root, html, body, .stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 121, 46, 0.18), transparent 34%),
        radial-gradient(circle at top right, rgba(59, 130, 246, 0.13), transparent 30%),
        linear-gradient(135deg, #fff7ed 0%, #ffffff 45%, #eff6ff 100%) !important;
    color: #111827 !important;
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* =========================================================
   SIDEBAR OSCURO MODERNO
   ========================================================= */

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(249, 115, 22, 0.22), transparent 30%),
        linear-gradient(180deg, #07111f 0%, #0f172a 55%, #111827 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 950 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    border-radius: 16px !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #fb923c, #ef4444) !important;
    border: 1px solid transparent !important;
}

/* =========================================================
   TEXTOS GENERALES
   ========================================================= */

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #111827;
}

h1 {
    font-weight: 950 !important;
}

p {
    line-height: 1.45;
}

/* =========================================================
   INPUTS Y FORMULARIOS
   ========================================================= */

input, textarea, select {
    border-radius: 14px !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    min-height: 48px !important;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border: 1px solid #fb923c !important;
    box-shadow: 0 0 0 3px rgba(251, 146, 60, 0.18) !important;
}

/* =========================================================
   BOTONES GENERALES
   ========================================================= */

.stButton > button,
.stFormSubmitButton > button {
    border-radius: 15px !important;
    border: none !important;
    font-weight: 900 !important;
    min-height: 48px !important;
    background: linear-gradient(135deg, #ff7a1a, #ff3d1f) !important;
    color: #ffffff !important;
    box-shadow: 0 14px 26px rgba(239, 68, 68, 0.24) !important;
    transition: all .18s ease-in-out;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.03);
    box-shadow: 0 18px 32px rgba(239, 68, 68, 0.30) !important;
}

.stLinkButton > a {
    border-radius: 15px !important;
    border: none !important;
    font-weight: 900 !important;
    min-height: 48px !important;
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: #ffffff !important;
    text-align: center !important;
    box-shadow: 0 14px 26px rgba(34, 197, 94, 0.22) !important;
}

/* =========================================================
   HERO PRINCIPAL
   ========================================================= */

.hero {
    padding: 34px 30px 28px 30px;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
    margin-bottom: 18px;
    text-align: center;
    position: relative;
}

.hero h1 {
    font-size: 58px;
    margin: 0;
    font-weight: 950;
    letter-spacing: -1.8px;
    color: #111827 !important;
}

.hero h1 span {
    color: #fb4b18 !important;
}

.hero p {
    font-size: 20px;
    margin-top: 10px;
    color: #64748b !important;
    font-weight: 500;
}

/* =========================================================
   TARJETAS PRINCIPALES
   ========================================================= */

.card {
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(226, 232, 240, 0.95);
    box-shadow: 0 22px 55px rgba(15, 23, 42, 0.09);
    border-radius: 26px;
    padding: 24px;
    margin-bottom: 18px;
    backdrop-filter: blur(14px);
}

.login-card {
    min-height: 210px;
    border-radius: 24px;
    padding: 26px;
    background: rgba(255,255,255,0.76);
    border: 1px solid rgba(226, 232, 240, 0.95);
    box-shadow: 0 20px 42px rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(12px);
}

/* =========================================================
   TARJETAS DE SERVICIO
   ========================================================= */

.service-card {
    border-radius: 26px;
    padding: 28px 22px;
    min-height: 205px;
    box-shadow: 0 22px 42px rgba(15, 23, 42, 0.17);
    transition: all .2s ease;
    border: 1px solid rgba(255,255,255,0.28);
}

.service-card:hover {
    transform: translateY(-4px);
}

.service-card h2 {
    color: #ffffff !important;
    font-size: 32px;
    margin: 0 0 10px 0;
    font-weight: 950;
}

.service-card p {
    color: #fff7ed !important;
    font-size: 15px;
    line-height: 1.35;
}

/* =========================================================
   PROMOCIONES
   ========================================================= */

.promo-carousel {
    height: 168px;
    border-radius: 28px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.13);
    margin-bottom: 24px;
    background: linear-gradient(135deg, #fb7185, #f97316, #22c55e, #06b6d4);
    background-size: 400% 400%;
    animation: gradientMove 4s ease infinite;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.promo-carousel h2 {
    color: #ffffff !important;
    font-size: 34px;
    font-weight: 950;
    margin: 0;
}

.promo-carousel p {
    color: #fff7ed !important;
    font-size: 17px;
    margin-top: 8px;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* =========================================================
   BADGES DE ESTADO
   ========================================================= */

.badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 14px;
}

.disponible {
    background: #dcfce7;
    color: #166534 !important;
}

.ocupado {
    background: #fee2e2;
    color: #991b1b !important;
}

.fuera {
    background: #e5e7eb;
    color: #374151 !important;
}

.pendiente {
    background: #fef3c7;
    color: #92400e !important;
}

.aceptado {
    background: #dbeafe;
    color: #1d4ed8 !important;
}

.finalizado {
    background: #dcfce7;
    color: #166534 !important;
}

/* =========================================================
   BOTÓN ADMINISTRADOR
   ========================================================= */

.admin-button-wrapper button {
    width: 100% !important;
    min-width: 190px !important;
    height: 44px !important;
    padding: 8px 18px !important;
    border-radius: 999px !important;
    white-space: nowrap !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    font-size: 14px !important;
    line-height: 1 !important;
}

/* =========================================================
   ALERTAS VISUALES
   ========================================================= */

.alerta-sonido-box {
    background: linear-gradient(135deg, #f97316, #ef4444);
    color: white !important;
    border-radius: 22px;
    padding: 18px 22px;
    margin-bottom: 18px;
    box-shadow: 0 18px 36px rgba(239, 68, 68, 0.24);
    font-weight: 900;
}

.alerta-sonido-box h3,
.alerta-sonido-box p {
    color: white !important;
    margin: 0;
}

/* =========================================================
   MÉTRICAS Y TABLAS
   ========================================================= */

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 14px 28px rgba(15,23,42,0.06);
}

[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
}

/* =========================================================
   PEQUEÑAS NOTAS
   ========================================================= */

.small-note {
    color: #6b7280 !important;
    font-size: 14px;
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media(max-width: 768px) {
    .hero h1 {
        font-size: 36px;
    }

    .hero p {
        font-size: 16px;
    }

    .promo-carousel h2 {
        font-size: 25px;
    }

    .admin-button-wrapper button {
        min-width: 150px !important;
        font-size: 13px !important;
    }
}

</style>
""", unsafe_allow_html=True)
# =========================================================
# PARTE 2 / 5
# CONEXIÓN CON GOOGLE SHEETS Y FUNCIONES AUXILIARES
# =========================================================

# =========================================================
# CONEXIÓN GOOGLE SHEETS
# =========================================================

@st.cache_resource(show_spinner=False)
def conectar_google_sheets():
    """
    Conecta la aplicación Streamlit con Google Sheets usando
    las credenciales guardadas en st.secrets.
    """
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


def obtener_hoja(nombre, encabezados):
    """
    Obtiene una hoja específica del archivo de Google Sheets.
    Si la hoja no existe, la crea automáticamente.
    Si la hoja existe pero no tiene encabezados correctos, los corrige.
    """
    libro = conectar_google_sheets()

    try:
        hoja = libro.worksheet(nombre)
    except gspread.WorksheetNotFound:
        hoja = libro.add_worksheet(
            title=nombre,
            rows=200,
            cols=len(encabezados) + 3
        )

    valores = hoja.get_all_values()

    if not valores:
        hoja.append_row(encabezados)
    else:
        primera = valores[0]

        if primera[:len(encabezados)] != encabezados:
            hoja.clear()
            hoja.append_row(encabezados)

    return hoja


def leer_registros(nombre, encabezados):
    """
    Lee todos los registros de una hoja y los devuelve como
    una lista de diccionarios.

    También agrega el campo interno _fila para poder editar
    o eliminar registros específicos.
    """
    hoja = obtener_hoja(nombre, encabezados)
    filas = hoja.get_all_values()

    if len(filas) <= 1:
        return []

    registros = []

    for i, fila in enumerate(filas[1:], start=2):
        fila_completa = fila + [""] * (len(encabezados) - len(fila))
        registro = dict(zip(encabezados, fila_completa[:len(encabezados)]))
        registro["_fila"] = i
        registros.append(registro)

    return registros


def agregar_registro(nombre, encabezados, datos):
    """
    Agrega un nuevo registro al final de la hoja indicada.
    """
    hoja = obtener_hoja(nombre, encabezados)
    fila = [datos.get(campo, "") for campo in encabezados]

    hoja.append_row(
        fila,
        value_input_option="USER_ENTERED"
    )


def actualizar_celda(nombre, encabezados, fila, columna, valor):
    """
    Actualiza una sola celda según la fila y el nombre de columna.
    """
    hoja = obtener_hoja(nombre, encabezados)
    indice_columna = encabezados.index(columna) + 1

    hoja.update_cell(
        fila,
        indice_columna,
        valor
    )


def actualizar_varias_celdas(nombre, encabezados, fila, cambios):
    """
    Actualiza varias columnas de una misma fila.
    El parámetro cambios debe venir como diccionario:
    {
        "Nombre columna": "nuevo valor"
    }
    """
    hoja = obtener_hoja(nombre, encabezados)

    for columna, valor in cambios.items():
        indice_columna = encabezados.index(columna) + 1
        hoja.update_cell(
            fila,
            indice_columna,
            valor
        )


def eliminar_fila(nombre, encabezados, fila):
    """
    Elimina una fila completa de una hoja.
    Se usa en el panel administrador para eliminar usuarios
    y colaboradores.
    """
    hoja = obtener_hoja(nombre, encabezados)
    hoja.delete_rows(int(fila))


# =========================================================
# FUNCIONES AUXILIARES GENERALES
# =========================================================

def normalizar_usuario(texto):
    """
    Convierte el usuario a minúsculas y elimina espacios.
    Esto evita duplicados por mayúsculas/minúsculas.
    """
    return str(texto).strip().lower()


def limpiar_texto(texto):
    """
    Limpia espacios al inicio y final del texto.
    """
    return str(texto).strip()


def limpiar_telefono(texto):
    """
    Deja solamente números en el teléfono.
    """
    return re.sub(r"[^0-9]", "", str(texto))


def telefono_whatsapp_cr(texto):
    """
    Convierte cualquier número nacional en formato WhatsApp Costa Rica.
    Si ya trae 506, lo conserva.
    """
    numero = limpiar_telefono(texto)

    if numero.startswith("506"):
        return numero

    return "506" + numero


def link_whatsapp(numero, mensaje):
    """
    Genera un enlace directo a WhatsApp con mensaje precargado.
    """
    return f"https://wa.me/{telefono_whatsapp_cr(numero)}?text={quote(mensaje)}"


def usuario_existe(nombre_usuario):
    """
    Verifica si un nombre de usuario ya existe como cliente
    o como colaborador.
    """
    usuario_n = normalizar_usuario(nombre_usuario)

    usuarios = leer_registros(
        HOJA_USUARIOS,
        ENCABEZADOS_USUARIOS
    )

    colaboradores = leer_registros(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES
    )

    for u in usuarios:
        if normalizar_usuario(u["Usuario"]) == usuario_n:
            return True

    for c in colaboradores:
        if normalizar_usuario(c["Usuario"]) == usuario_n:
            return True

    return False


def badge_estado(estado):
    """
    Devuelve una etiqueta visual HTML según el estado.
    """
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
# CONTROL DE SESIÓN
# =========================================================

def inicializar_estado():
    """
    Inicializa las variables principales de sesión.
    Estas variables controlan qué pantalla ve cada persona.
    También inicializa variables de alertas internas.
    """
    valores = {
        "pagina": "login",
        "tipo": None,
        "usuario_actual": None,
        "colaborador_actual": None,
        "servicio_seleccionado": None,
        "admin_autenticado": False,

        # Variables para alertas sonoras y visuales
        "alertas_activadas": True,
        "ultimo_total_pendientes_colaborador": 0,
        "ultimo_total_aceptadas_usuario": 0,
        "ultima_alerta_usuario_ids": "",
        "ultima_alerta_colaborador_ids": ""
    }

    for clave, valor in valores.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def cerrar_sesion():
    """
    Cierra cualquier sesión activa y devuelve la app al login.
    También reinicia los controles de alertas.
    """
    st.session_state.pagina = "login"
    st.session_state.tipo = None
    st.session_state.usuario_actual = None
    st.session_state.colaborador_actual = None
    st.session_state.servicio_seleccionado = None
    st.session_state.admin_autenticado = False

    st.session_state.ultimo_total_pendientes_colaborador = 0
    st.session_state.ultimo_total_aceptadas_usuario = 0
    st.session_state.ultima_alerta_usuario_ids = ""
    st.session_state.ultima_alerta_colaborador_ids = ""


# =========================================================
# CONTADORES Y VALIDACIONES
# =========================================================

def total_usuarios_registrados():
    """
    Cuenta cuántos usuarios existen en la hoja Usuarios.
    """
    return len(
        leer_registros(
            HOJA_USUARIOS,
            ENCABEZADOS_USUARIOS
        )
    )


def total_colaboradores_servicio(servicio):
    """
    Cuenta cuántos colaboradores existen para un servicio específico.
    """
    colaboradores = leer_registros(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES
    )

    return sum(
        1 for c in colaboradores
        if c["Servicio"] == servicio
    )


# =========================================================
# LOGIN DE USUARIOS Y COLABORADORES
# =========================================================

def buscar_usuario_login(nombre_usuario, clave):
    """
    Busca un usuario cliente por usuario y clave.
    El usuario no distingue mayúsculas/minúsculas.
    La clave sí se compara exactamente.
    """
    usuario_n = normalizar_usuario(nombre_usuario)
    clave_limpia = limpiar_texto(clave)

    usuarios = leer_registros(
        HOJA_USUARIOS,
        ENCABEZADOS_USUARIOS
    )

    for u in usuarios:
        if (
            normalizar_usuario(u["Usuario"]) == usuario_n
            and limpiar_texto(u["Clave"]) == clave_limpia
        ):
            return u

    return None


def buscar_colaborador_login(nombre_usuario, clave):
    """
    Busca un colaborador por usuario y clave.
    """
    usuario_n = normalizar_usuario(nombre_usuario)
    clave_limpia = limpiar_texto(clave)

    colaboradores = leer_registros(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES
    )

    for c in colaboradores:
        if (
            normalizar_usuario(c["Usuario"]) == usuario_n
            and limpiar_texto(c["Clave"]) == clave_limpia
        ):
            return c

    return None


# =========================================================
# REGISTRO DE USUARIOS Y COLABORADORES
# =========================================================

def registrar_usuario(nombre, apellido1, apellido2, telefono, usuario, clave):
    """
    Registra un nuevo usuario cliente en Google Sheets.
    """
    datos = {
        "ID": str(uuid.uuid4())[:8],
        "Nombre": limpiar_texto(nombre),
        "Primer apellido": limpiar_texto(apellido1),
        "Segundo apellido": limpiar_texto(apellido2),
        "Teléfono": telefono_whatsapp_cr(telefono),
        "Usuario": normalizar_usuario(usuario),
        "Clave": limpiar_texto(clave),
        "Tipo": "Usuario",
        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    agregar_registro(
        HOJA_USUARIOS,
        ENCABEZADOS_USUARIOS,
        datos
    )

    return datos


def registrar_colaborador(nombre, apellido1, apellido2, telefono, usuario, clave, servicio):
    """
    Registra un nuevo colaborador/trabajador en Google Sheets.
    """
    datos = {
        "ID": str(uuid.uuid4())[:8],
        "Nombre": limpiar_texto(nombre),
        "Primer apellido": limpiar_texto(apellido1),
        "Segundo apellido": limpiar_texto(apellido2),
        "Teléfono": telefono_whatsapp_cr(telefono),
        "Usuario": normalizar_usuario(usuario),
        "Clave": limpiar_texto(clave),
        "Tipo": "Colaborador",
        "Servicio": servicio,
        "Estado": "Disponible",
        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    agregar_registro(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES,
        datos
    )

    return datos
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
    Devuelve las solicitudes pendientes de un servicio específico.
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
    Devuelve todas las solicitudes aceptadas o finalizadas
    por un colaborador específico.
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
    Cambia el estado de un colaborador:
    Disponible, Ocupado o Fuera de servicio.
    """
    actualizar_celda(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES,
        int(colaborador["_fila"]),
        "Estado",
        nuevo_estado
    )

    colaborador["Estado"] = nuevo_estado
    st.session_state.colaborador_actual = colaborador


def aceptar_solicitud(solicitud, colaborador):
    """
    Permite que un colaborador acepte una solicitud pendiente.
    También cambia el estado del colaborador a Ocupado.
    """
    nombre_colaborador = (
        f'{colaborador["Nombre"]} '
        f'{colaborador["Primer apellido"]} '
        f'{colaborador["Segundo apellido"]}'
    ).strip()

    actualizar_varias_celdas(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES,
        int(solicitud["_fila"]),
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


def finalizar_solicitud(solicitud, colaborador):
    """
    Finaliza una solicitud aceptada y devuelve al colaborador
    al estado Disponible.
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
# FUNCIONES DE ALERTA SONORA Y VISUAL
# =========================================================

def reproducir_alerta(titulo="🔔 Nueva notificación", mensaje="Hay una actualización nueva en la app."):
    """
    Reproduce una alerta sonora dentro de la app y muestra
    una tarjeta visual de notificación.

    Importante:
    Algunos navegadores pueden bloquear el sonido automático
    si el usuario no ha interactuado antes con la página.
    """
    if not st.session_state.get("alertas_activadas", True):
        return

    st.markdown(f"""
    <div class="alerta-sonido-box">
        <h3>{titulo}</h3>
        <p>{mensaje}</p>
    </div>

    <audio autoplay>
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>
    """, unsafe_allow_html=True)

    st.toast(mensaje)


def activar_refresco_automatico():
    """
    Refresca automáticamente la app cada cierto tiempo
    para revisar cambios en solicitudes.

    15000 milisegundos = 15 segundos.
    """
    st_autorefresh(
        interval=15000,
        key="refresco_automatico_notificaciones"
    )


# =========================================================
# COMPONENTES VISUALES
# =========================================================

def hero():
    """
    Encabezado visual principal de la app.
    """
    st.markdown("""
    <div class="hero">
        <h1>🛵 Express <span>Local</span></h1>
        <p>Solicita taxi, express, carga y camión de forma rápida y segura.</p>
    </div>
    """, unsafe_allow_html=True)


def promo_carousel():
    """
    Banner visual de promociones o información destacada.
    """
    st.markdown("""
    <div class="promo-carousel">
        <div>
            <h2>🔥 Promociones y servicios destacados</h2>
            <p>Este espacio puede mostrar restaurantes, comercios, ofertas y servicios activos.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_menu():
    """
    Menú lateral visible cuando una sesión está activa.
    Las claves demo solo se muestran al administrador.
    """
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
    """
    Formulario para que un usuario registrado pueda ingresar.
    """
    st.markdown("""
    <h3>🚪 Ingreso de usuario</h3>
    <p class="small-note">Ingresa con tu usuario y contraseña para solicitar servicios.</p>
    """, unsafe_allow_html=True)

    with st.form("form_login_usuario"):
        usuario = st.text_input(
            "Nombre de usuario",
            key="login_user_user"
        )

        clave = st.text_input(
            "Clave",
            type="password",
            key="login_user_pass"
        )

        ingresar = st.form_submit_button(
            "Ingresar como usuario"
        )

    if ingresar:
        encontrado = buscar_usuario_login(
            usuario,
            clave
        )

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
    """
    Formulario para registrar un nuevo usuario cliente.
    """
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

        guardar = st.form_submit_button(
            "Registrarme como usuario"
        )

    if guardar:
        if total_usuarios_registrados() >= LIMITE_USUARIOS_DEMO:
            st.error(
                f"El demo permite registrar máximo {LIMITE_USUARIOS_DEMO} usuarios."
            )
            return

        if not all([nombre, apellido1, apellido2, telefono, usuario, clave]):
            st.error("Debe completar todos los espacios.")
            return

        if usuario_existe(usuario):
            st.error("Ese nombre de usuario ya existe. Use otro.")
            return

        nuevo = registrar_usuario(
            nombre,
            apellido1,
            apellido2,
            telefono,
            usuario,
            clave
        )

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
    """
    Formulario para que un colaborador registrado pueda ingresar.
    """
    st.markdown("""
    <h3>🛠️ Ingreso de colaborador</h3>
    <p class="small-note">Ingresa con tus credenciales para aceptar solicitudes.</p>
    """, unsafe_allow_html=True)

    with st.form("form_login_colaborador"):
        usuario = st.text_input(
            "Nombre de usuario",
            key="login_col_user"
        )

        clave = st.text_input(
            "Clave",
            type="password",
            key="login_col_pass"
        )

        ingresar = st.form_submit_button(
            "Ingresar como colaborador"
        )

    if ingresar:
        encontrado = buscar_colaborador_login(
            usuario,
            clave
        )

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
    """
    Formulario para registrar un nuevo colaborador o trabajador.
    """
    st.markdown("""
    <h3>🧰 Registro nuevo de colaborador</h3>
    <p class="small-note">Regístrate como colaborador para brindar servicios.</p>
    """, unsafe_allow_html=True)

    st.caption(
        f"Demo: máximo {LIMITE_COLABORADORES_POR_SERVICIO} colaboradores por servicio."
    )

    with st.form("form_registro_colaborador"):
        c1, c2, c3 = st.columns(3)

        with c1:
            nombre = st.text_input("Nombre", key="col_nombre")

        with c2:
            apellido1 = st.text_input("Primer apellido", key="col_ap1")

        with c3:
            apellido2 = st.text_input("Segundo apellido", key="col_ap2")

        telefono = st.text_input(
            "Número de teléfono Costa Rica",
            key="col_tel"
        )

        servicio = st.selectbox(
            "Servicio que brindará",
            list(SERVICIOS.keys())
        )

        codigo = st.text_input(
            "Clave autorizada por el coordinador",
            type="password"
        )

        usuario = st.text_input(
            "Nombre de usuario",
            key="col_user"
        )

        clave = st.text_input(
            "Clave personal",
            type="password",
            help="Puede usar números, mayúsculas y minúsculas.",
            key="col_pass"
        )

        guardar = st.form_submit_button(
            "Registrarme como colaborador"
        )

    if guardar:
        if not all([nombre, apellido1, apellido2, telefono, servicio, codigo, usuario, clave]):
            st.error("Debe completar todos los espacios.")
            return

        if codigo.strip() not in CLAVES_COLABORADOR[servicio]:
            st.error(
                "La clave del coordinador no corresponde al servicio seleccionado."
            )
            return

        if total_colaboradores_servicio(servicio) >= LIMITE_COLABORADORES_POR_SERVICIO:
            st.error(
                f"Ya existen {LIMITE_COLABORADORES_POR_SERVICIO} colaboradores registrados para {servicio}."
            )
            return

        if usuario_existe(usuario):
            st.error("Ese nombre de usuario ya existe. Use otro.")
            return

        nuevo = registrar_colaborador(
            nombre,
            apellido1,
            apellido2,
            telefono,
            usuario,
            clave,
            servicio
        )

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
    """
    Pantalla principal de ingreso.
    Mantiene las pestañas de Usuarios y Colaboradores.
    Botón administrador corregido.
    """
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
    """
    Panel principal para usuarios.
    Permite seleccionar servicios, ver solicitudes propias
    y recibir alerta cuando una solicitud pasa a Aceptado.
    """
    activar_refresco_automatico()
    sidebar_menu()

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

    aceptadas_usuario = [
        s for s in solicitudes
        if s["Estado"] == "Aceptado"
    ]

    ids_aceptadas_actuales = ",".join(
        sorted([s["ID"] for s in aceptadas_usuario])
    )

    if (
        ids_aceptadas_actuales
        and st.session_state.ultima_alerta_usuario_ids
        and ids_aceptadas_actuales != st.session_state.ultima_alerta_usuario_ids
    ):
        reproducir_alerta(
            "🔔 Solicitud aceptada",
            "Un colaborador aceptó una de sus solicitudes."
        )

    st.session_state.ultima_alerta_usuario_ids = ids_aceptadas_actuales
    st.session_state.ultimo_total_aceptadas_usuario = len(aceptadas_usuario)

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
    """
    Muestra información del servicio seleccionado,
    colaboradores disponibles y formulario de solicitud.
    """
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
    """
    Panel principal de colaborador.
    Permite cambiar estado, aceptar solicitudes, finalizar servicios
    y recibir alerta cuando hay nuevas solicitudes pendientes.
    """
    activar_refresco_automatico()
    sidebar_menu()

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
            actualizar_estado_colaborador(
                colaborador,
                nuevo_estado
            )
            st.success("Estado actualizado.")
            st.rerun()

    st.divider()
    st.subheader("🔔 Solicitudes pendientes para mi servicio")

    pendientes = solicitudes_pendientes_servicio(servicio)

    ids_pendientes_actuales = ",".join(
        sorted([s["ID"] for s in pendientes])
    )

    if (
        ids_pendientes_actuales
        and st.session_state.ultima_alerta_colaborador_ids
        and ids_pendientes_actuales != st.session_state.ultima_alerta_colaborador_ids
    ):
        reproducir_alerta(
            "🔔 Nueva solicitud",
            f"Hay una nueva solicitud pendiente para {servicio}."
        )

    st.session_state.ultima_alerta_colaborador_ids = ids_pendientes_actuales
    st.session_state.ultimo_total_pendientes_colaborador = len(pendientes)

    if colaborador["Estado"] != "Disponible":
        st.warning("Para aceptar nuevas solicitudes debe estar en estado Disponible.")

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

            if colaborador["Estado"] == "Disponible":
                if st.button(
                    f"✅ Aceptar solicitud #{s['ID']}",
                    key=f"aceptar_{s['ID']}",
                    use_container_width=True
                ):
                    aceptar_solicitud(
                        s,
                        colaborador
                    )
                    st.success("Solicitud aceptada. Ahora el usuario podrá contactarlo por WhatsApp.")
                    st.rerun()

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
