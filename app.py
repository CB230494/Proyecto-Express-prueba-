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
# REGISTRO, LOGIN, SOLICITUDES Y NOTIFICACIONES PUSH
# =========================================================

PWA_NOTIFICACIONES_URL = "https://express-local-push-test.web.app"


# =========================================================
# VALIDACIONES Y CONTADORES
# =========================================================

def usuario_existe(nombre_usuario):
    usuario_n = normalizar_usuario(nombre_usuario)

    usuarios = leer_registros(HOJA_USUARIOS, ENCABEZADOS_USUARIOS)
    colaboradores = leer_registros(HOJA_COLABORADORES, ENCABEZADOS_COLABORADORES)

    for u in usuarios:
        if normalizar_usuario(u.get("Usuario", "")) == usuario_n:
            return True

    for c in colaboradores:
        if normalizar_usuario(c.get("Usuario", "")) == usuario_n:
            return True

    return False


def total_usuarios_registrados():
    return len(leer_registros(HOJA_USUARIOS, ENCABEZADOS_USUARIOS))


def total_colaboradores_servicio(servicio):
    colaboradores = leer_registros(HOJA_COLABORADORES, ENCABEZADOS_COLABORADORES)

    return sum(
        1 for c in colaboradores
        if c.get("Servicio") == servicio
    )


# =========================================================
# LOGIN
# =========================================================

def buscar_usuario_login(nombre_usuario, clave):
    usuario_n = normalizar_usuario(nombre_usuario)
    clave_limpia = limpiar_texto(clave)

    usuarios = leer_registros(HOJA_USUARIOS, ENCABEZADOS_USUARIOS)

    for u in usuarios:
        if (
            normalizar_usuario(u.get("Usuario", "")) == usuario_n
            and limpiar_texto(u.get("Clave", "")) == clave_limpia
        ):
            return u

    return None


def buscar_colaborador_login(nombre_usuario, clave):
    usuario_n = normalizar_usuario(nombre_usuario)
    clave_limpia = limpiar_texto(clave)

    colaboradores = leer_registros(HOJA_COLABORADORES, ENCABEZADOS_COLABORADORES)

    for c in colaboradores:
        if (
            normalizar_usuario(c.get("Usuario", "")) == usuario_n
            and limpiar_texto(c.get("Clave", "")) == clave_limpia
        ):
            return c

    return None


# =========================================================
# REGISTRO
# =========================================================

def registrar_usuario(nombre, apellido1, apellido2, telefono, usuario, clave):
    datos = {
        "ID": str(uuid.uuid4())[:8],
        "Nombre": limpiar_texto(nombre),
        "Primer apellido": limpiar_texto(apellido1),
        "Segundo apellido": limpiar_texto(apellido2),
        "Teléfono": telefono_whatsapp_cr(telefono),
        "Usuario": normalizar_usuario(usuario),
        "Clave": limpiar_texto(clave),
        "Tipo": "Usuario",
        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Push Token": ""
    }

    agregar_registro(
        HOJA_USUARIOS,
        ENCABEZADOS_USUARIOS,
        datos
    )

    return datos


def registrar_colaborador(nombre, apellido1, apellido2, telefono, usuario, clave, servicio):
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
        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Push Token": ""
    }

    agregar_registro(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES,
        datos
    )

    return datos


# =========================================================
# SOLICITUDES
# =========================================================

def crear_solicitud(servicio, usuario, detalle):
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

    notificar_colaboradores_disponibles(
        servicio,
        "🔔 Nueva solicitud",
        f"Hay una nueva solicitud de {servicio}: {detalle}"
    )

    return datos


def solicitudes_usuario(usuario_id):
    solicitudes = leer_registros(HOJA_SOLICITUDES, ENCABEZADOS_SOLICITUDES)

    return [
        s for s in solicitudes
        if s.get("Cliente ID") == usuario_id
    ]


def solicitudes_pendientes_servicio(servicio):
    solicitudes = leer_registros(HOJA_SOLICITUDES, ENCABEZADOS_SOLICITUDES)

    return [
        s for s in solicitudes
        if s.get("Servicio") == servicio and s.get("Estado") == "Pendiente"
    ]


def solicitudes_colaborador(colaborador_id):
    solicitudes = leer_registros(HOJA_SOLICITUDES, ENCABEZADOS_SOLICITUDES)

    return [
        s for s in solicitudes
        if s.get("Colaborador ID") == colaborador_id
    ]


def actualizar_estado_colaborador(colaborador, nuevo_estado):
    fila_colaborador = colaborador.get("_fila")

    if not fila_colaborador:
        colaboradores = leer_registros(
            HOJA_COLABORADORES,
            ENCABEZADOS_COLABORADORES
        )

        encontrado = next(
            (c for c in colaboradores if c.get("ID") == colaborador.get("ID")),
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
    solicitudes_actuales = leer_registros(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES
    )

    solicitud_actual = next(
        (s for s in solicitudes_actuales if s.get("ID") == solicitud.get("ID")),
        None
    )

    if not solicitud_actual:
        st.error("La solicitud ya no existe.")
        return False

    if solicitud_actual.get("Estado") != "Pendiente":
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

    notificar_usuario_por_id(
        solicitud_actual["Cliente ID"],
        "✅ Solicitud aceptada",
        f"{nombre_colaborador} aceptó su solicitud de {solicitud_actual['Servicio']}."
    )

    return True


def finalizar_solicitud(solicitud, colaborador):
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

    notificar_usuario_por_id(
        solicitud["Cliente ID"],
        "🏁 Servicio finalizado",
        f"Su servicio de {solicitud['Servicio']} fue finalizado."
    )

    return True


# =========================================================
# NOTIFICACIONES PUSH
# =========================================================

def notificar_usuario_por_id(usuario_id, titulo, mensaje):
    usuarios = leer_registros(
        HOJA_USUARIOS,
        ENCABEZADOS_USUARIOS
    )

    usuario = next(
        (u for u in usuarios if u.get("ID") == usuario_id),
        None
    )

    if not usuario:
        return False

    token = usuario.get("Push Token", "")

    if not token:
        return False

    return enviar_push_token(token, titulo, mensaje)


def notificar_colaboradores_disponibles(servicio, titulo, mensaje):
    colaboradores = leer_registros(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES
    )

    enviados = 0

    for c in colaboradores:
        if (
            c.get("Servicio") == servicio
            and c.get("Estado") == "Disponible"
            and c.get("Push Token")
        ):
            ok = enviar_push_token(
                c.get("Push Token"),
                titulo,
                mensaje
            )

            if ok:
                enviados += 1

    return enviados


# =========================================================
# ACTIVACIÓN DE PUSH TOKEN
# =========================================================

def bloque_activar_notificaciones():
    st.markdown("""
    <div class="card">
        <h3>🔔 Notificaciones push</h3>
        <p>
            Para recibir avisos aunque la app esté en segundo plano,
            active las notificaciones desde la página segura de Express Local.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.link_button(
        "🔔 Abrir página para activar notificaciones",
        PWA_NOTIFICACIONES_URL,
        use_container_width=True
    )

    token = st.text_area(
        "Pegue aquí el TOKEN DEL DISPOSITIVO generado en la página de notificaciones",
        height=120,
        placeholder="Pegue aquí el token completo..."
    )

    if st.button("💾 Guardar token de este dispositivo", use_container_width=True):
        if not token.strip():
            st.error("Debe pegar el token generado.")
            return

        token_limpio = token.strip()

        if st.session_state.tipo == "Usuario" and st.session_state.usuario_actual:
            ok = guardar_push_token_usuario(
                st.session_state.usuario_actual["ID"],
                token_limpio
            )

            if ok:
                st.session_state.usuario_actual["Push Token"] = token_limpio
                st.success("Token guardado correctamente para este usuario.")
            else:
                st.error("No se pudo guardar el token del usuario.")

        elif st.session_state.tipo == "Colaborador" and st.session_state.colaborador_actual:
            ok = guardar_push_token_colaborador(
                st.session_state.colaborador_actual["ID"],
                token_limpio
            )

            if ok:
                st.session_state.colaborador_actual["Push Token"] = token_limpio
                st.success("Token guardado correctamente para este colaborador.")
            else:
                st.error("No se pudo guardar el token del colaborador.")

        else:
            st.warning("Debe iniciar sesión como usuario o colaborador.")


# =========================================================
# FORMULARIOS DE USUARIO
# =========================================================

def formulario_login_usuario():
    st.markdown("<h3>🚪 Ingreso de usuario</h3>", unsafe_allow_html=True)

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
            st.rerun()
        else:
            st.error("Usuario o clave incorrecta.")


def formulario_registro_usuario():
    st.markdown("<h3>👤 Registro nuevo de usuario</h3>", unsafe_allow_html=True)

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
        clave = st.text_input("Clave", type="password")

        guardar = st.form_submit_button("Registrarme como usuario")

    if guardar:
        if total_usuarios_registrados() >= MAX_USUARIOS_DEMO:
            st.error(f"El demo permite registrar máximo {MAX_USUARIOS_DEMO} usuarios.")
            return

        if not all([nombre, apellido1, apellido2, telefono, usuario, clave]):
            st.error("Debe completar todos los espacios.")
            return

        if usuario_existe(usuario):
            st.error("Ese nombre de usuario ya existe.")
            return

        nuevo = registrar_usuario(
            nombre,
            apellido1,
            apellido2,
            telefono,
            usuario,
            clave
        )

        st.session_state.usuario_actual = nuevo
        st.session_state.tipo = "Usuario"
        st.session_state.pagina = "panel_usuario"

        st.success("Usuario registrado correctamente.")
        st.rerun()


# =========================================================
# FORMULARIOS DE COLABORADOR
# =========================================================

def formulario_login_colaborador():
    st.markdown("<h3>🛠️ Ingreso de colaborador</h3>", unsafe_allow_html=True)

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
            st.rerun()
        else:
            st.error("Usuario o clave incorrecta.")


def formulario_registro_colaborador():
    st.markdown("<h3>🧰 Registro nuevo de colaborador</h3>", unsafe_allow_html=True)

    with st.form("form_registro_colaborador"):
        c1, c2, c3 = st.columns(3)

        with c1:
            nombre = st.text_input("Nombre", key="col_nombre")

        with c2:
            apellido1 = st.text_input("Primer apellido", key="col_ap1")

        with c3:
            apellido2 = st.text_input("Segundo apellido", key="col_ap2")

        telefono = st.text_input("Número de teléfono Costa Rica", key="col_tel")

        servicio = st.selectbox(
            "Servicio que brindará",
            list(SERVICIOS.keys())
        )

        usuario = st.text_input("Nombre de usuario", key="col_user")
        clave = st.text_input("Clave personal", type="password", key="col_pass")

        guardar = st.form_submit_button("Registrarme como colaborador")

    if guardar:
        if not all([nombre, apellido1, apellido2, telefono, servicio, usuario, clave]):
            st.error("Debe completar todos los espacios.")
            return

        limite = MAX_COLABORADORES_POR_SERVICIO.get(servicio, 6)

        if total_colaboradores_servicio(servicio) >= limite:
            st.error(f"Ya existen {limite} colaboradores registrados para {servicio}.")
            return

        if usuario_existe(usuario):
            st.error("Ese nombre de usuario ya existe.")
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

        st.session_state.colaborador_actual = nuevo
        st.session_state.tipo = "Colaborador"
        st.session_state.pagina = "panel_colaborador"

        st.success("Colaborador registrado correctamente.")
        st.rerun()
# =========================================================
# PARTE 4 / 5
# PÁGINAS PRINCIPALES: LOGIN, USUARIO, SERVICIO Y COLABORADOR
# =========================================================

def hero():
    st.markdown("""
    <div class="card" style="text-align:center;">
        <h1>🛵 Express Local</h1>
        <p>Solicita taxi, express, carga y camión de forma rápida y segura.</p>
    </div>
    """, unsafe_allow_html=True)


def promo_carousel():
    st.markdown("""
    <div class="card" style="text-align:center;">
        <h2>🔥 Servicios disponibles</h2>
        <p>Seleccione el servicio que necesita y un colaborador disponible podrá aceptar su solicitud.</p>
    </div>
    """, unsafe_allow_html=True)


def sidebar_menu():
    with st.sidebar:
        st.title("🛵 Express Local")

        if st.session_state.tipo == "Usuario" and st.session_state.usuario_actual:
            st.success(f"Usuario: {st.session_state.usuario_actual.get('Usuario', '')}")

        if st.session_state.tipo == "Colaborador" and st.session_state.colaborador_actual:
            st.success(f"Colaborador: {st.session_state.colaborador_actual.get('Usuario', '')}")

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

        st.link_button(
            "🔔 Activar notificaciones",
            PWA_NOTIFICACIONES_URL,
            use_container_width=True
        )

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()


def pagina_login():
    hero()

    st.markdown("""
    <div class="card" style="text-align:center;">
        <h2>Acceso principal</h2>
        <p>Seleccione si desea ingresar como usuario o colaborador.</p>
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

    col1, col2 = st.columns([7, 2])

    with col2:
        if st.button("Administrador", key="btn_admin_oculto", use_container_width=True):
            st.session_state.pagina = "admin_login"
            st.rerun()


def pagina_panel_usuario():
    sidebar_menu()

    usuario = st.session_state.usuario_actual

    promo_carousel()

    st.markdown(f"""
    <div class="card">
        <h2>Hola, {usuario.get('Nombre', '')} 👋</h2>
        <p>Seleccione el servicio que necesita.</p>
    </div>
    """, unsafe_allow_html=True)

    bloque_activar_notificaciones()

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

    solicitudes = solicitudes_usuario(usuario["ID"])

    if not solicitudes:
        st.info("Todavía no tiene solicitudes registradas.")
    else:
        for s in reversed(solicitudes):
            st.markdown(f"""
            <div class="card">
                <h3>{s.get('Servicio', '')} · Solicitud #{s.get('ID', '')}</h3>
                <p><b>Fecha:</b> {s.get('Fecha', '')}</p>
                <p><b>Estado:</b> {badge_estado(s.get('Estado', ''))}</p>
                <p><b>Detalle:</b> {s.get('Detalle', '')}</p>
                <p><b>Colaborador:</b> {s.get('Colaborador', '') if s.get('Colaborador', '') else 'Pendiente de aceptación'}</p>
            </div>
            """, unsafe_allow_html=True)

            if s.get("Estado") == "Aceptado" and s.get("Teléfono colaborador"):
                mensaje = (
                    f"Hola {s.get('Colaborador', '')}, soy {s.get('Cliente', '')}. "
                    f"Tengo la solicitud #{s.get('ID', '')} de {s.get('Servicio', '')}. "
                    "Quisiera coordinar los detalles por este medio."
                )

                st.link_button(
                    "💬 Chatear con colaborador por WhatsApp",
                    link_whatsapp(
                        s.get("Teléfono colaborador"),
                        mensaje
                    ),
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
    <div class="service-card" style="background: linear-gradient(135deg, {info['color1']}, {info['color2']});">
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
        if c.get("Servicio") == servicio
    ]

    disponibles = [
        c for c in colaboradores_servicio
        if c.get("Estado") == "Disponible"
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
                f'{c.get("Nombre", "")} '
                f'{c.get("Primer apellido", "")} '
                f'{c.get("Segundo apellido", "")}'
            ).strip()

            st.markdown(f"""
            <div class="card">
                <h3>{nombre}</h3>
                <p><b>Servicio:</b> {c.get('Servicio', '')}</p>
                <p><b>Estado:</b> {badge_estado(c.get('Estado', ''))}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📲 Crear solicitud")

    with st.form("crear_solicitud_servicio"):
        detalle = st.text_area(
            "Detalle de la solicitud",
            placeholder="Ejemplo: necesito un taxi hacia el centro / retirar comida / trasladar una caja..."
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
            f"Solicitud enviada correctamente. Código: {nueva['ID']}"
        )

        st.session_state.pagina = "panel_usuario"
        st.rerun()

    if st.button("⬅️ Volver a servicios", use_container_width=True):
        st.session_state.pagina = "panel_usuario"
        st.rerun()


def pagina_panel_colaborador():
    sidebar_menu()

    colaborador = st.session_state.colaborador_actual
    servicio = colaborador["Servicio"]
    info = SERVICIOS[servicio]

    st.markdown(f"""
    <div class="service-card" style="background: linear-gradient(135deg, {info['color1']}, {info['color2']});">
        <h2>{info['icono']} Panel de {servicio}</h2>
        <p>Administre su estado y acepte solicitudes pendientes.</p>
    </div>
    """, unsafe_allow_html=True)

    bloque_activar_notificaciones()

    nombre = (
        f'{colaborador.get("Nombre", "")} '
        f'{colaborador.get("Primer apellido", "")} '
        f'{colaborador.get("Segundo apellido", "")}'
    ).strip()

    st.markdown(f"""
    <div class="card">
        <h2>{nombre}</h2>
        <p><b>Teléfono:</b> {colaborador.get('Teléfono', '')}</p>
        <p><b>Servicio:</b> {servicio}</p>
        <p><b>Estado actual:</b> {badge_estado(colaborador.get('Estado', ''))}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🚦 Cambiar estado")

    c1, c2 = st.columns([2, 1])

    estados = ["Disponible", "Ocupado", "Fuera de servicio"]

    with c1:
        nuevo_estado = st.selectbox(
            "Estado",
            estados,
            index=estados.index(colaborador.get("Estado"))
            if colaborador.get("Estado") in estados else 0
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
    st.subheader("🔔 Solicitudes pendientes")

    if colaborador.get("Estado") != "Disponible":
        st.warning("Para aceptar solicitudes debe estar en estado Disponible.")
        pendientes = []
    else:
        pendientes = solicitudes_pendientes_servicio(servicio)

    if not pendientes:
        st.info("No hay solicitudes pendientes para este servicio.")
    else:
        for s in reversed(pendientes):
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s.get('ID', '')} · {s.get('Servicio', '')}</h3>
                <p><b>Fecha:</b> {s.get('Fecha', '')}</p>
                <p><b>Cliente:</b> {s.get('Cliente', '')}</p>
                <p><b>Detalle:</b> {s.get('Detalle', '')}</p>
                <p><b>Estado:</b> {badge_estado(s.get('Estado', ''))}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"✅ Aceptar solicitud #{s.get('ID', '')}",
                key=f"aceptar_{s.get('ID', '')}",
                use_container_width=True
            ):
                aceptada = aceptar_solicitud(
                    s,
                    colaborador
                )

                if aceptada:
                    st.success("Solicitud aceptada correctamente.")
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
                <h3>Solicitud #{s.get('ID', '')} · {s.get('Servicio', '')}</h3>
                <p><b>Cliente:</b> {s.get('Cliente', '')}</p>
                <p><b>Teléfono cliente:</b> {s.get('Teléfono cliente', '')}</p>
                <p><b>Detalle:</b> {s.get('Detalle', '')}</p>
                <p><b>Estado:</b> {badge_estado(s.get('Estado', ''))}</p>
            </div>
            """, unsafe_allow_html=True)

            if s.get("Teléfono cliente"):
                mensaje = (
                    f"Hola {s.get('Cliente', '')}, soy {s.get('Colaborador', '')}, "
                    f"acepté su solicitud #{s.get('ID', '')} de {s.get('Servicio', '')}. "
                    "Coordinemos los detalles por este medio."
                )

                st.link_button(
                    "💬 Chatear con usuario por WhatsApp",
                    link_whatsapp(
                        s.get("Teléfono cliente"),
                        mensaje
                    ),
                    use_container_width=True
                )

            if s.get("Estado") != "Finalizado":
                if st.button(
                    f"🏁 Finalizar solicitud #{s.get('ID', '')}",
                    key=f"fin_{s.get('ID', '')}",
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
# ADMINISTRADOR, DASHBOARD Y EJECUCIÓN PRINCIPAL
# =========================================================

def pagina_admin_login():
    hero()

    st.markdown("""
    <div class="card" style="max-width:500px; margin:auto;">
        <h2>🔐 Acceso administrador</h2>
        <p>Ingrese las credenciales administrativas.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_admin_login"):
        usuario = st.text_input("Usuario administrador")
        clave = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")

    if ingresar:
        if usuario == ADMIN_USUARIO and clave == ADMIN_CLAVE:
            st.session_state.tipo = "Administrador"
            st.session_state.admin_autenticado = True
            st.session_state.pagina = "panel_admin"
            st.rerun()
        else:
            st.error("Credenciales incorrectas.")


def pagina_panel_admin():
    sidebar_menu()

    st.markdown("""
    <div class="card">
        <h1>📊 Panel Administrador</h1>
        <p>Control general de usuarios, colaboradores, solicitudes y notificaciones.</p>
    </div>
    """, unsafe_allow_html=True)

    usuarios = leer_registros(
        HOJA_USUARIOS,
        ENCABEZADOS_USUARIOS
    )

    colaboradores = leer_registros(
        HOJA_COLABORADORES,
        ENCABEZADOS_COLABORADORES
    )

    solicitudes = leer_registros(
        HOJA_SOLICITUDES,
        ENCABEZADOS_SOLICITUDES
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Usuarios", len(usuarios))
    c2.metric("Colaboradores", len(colaboradores))
    c3.metric("Solicitudes", len(solicitudes))
    c4.metric(
        "Finalizadas",
        sum(1 for s in solicitudes if s.get("Estado") == "Finalizado")
    )

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Dashboard",
        "👤 Usuarios",
        "🛠️ Colaboradores",
        "📋 Solicitudes"
    ])

    with tab1:
        st.subheader("📈 Resumen por servicio")

        resumen = []

        for servicio in SERVICIOS.keys():
            total_servicio = sum(
                1 for s in solicitudes
                if s.get("Servicio") == servicio
            )

            finalizadas = sum(
                1 for s in solicitudes
                if s.get("Servicio") == servicio and s.get("Estado") == "Finalizado"
            )

            pendientes = sum(
                1 for s in solicitudes
                if s.get("Servicio") == servicio and s.get("Estado") == "Pendiente"
            )

            aceptadas = sum(
                1 for s in solicitudes
                if s.get("Servicio") == servicio and s.get("Estado") == "Aceptado"
            )

            resumen.append({
                "Servicio": servicio,
                "Total": total_servicio,
                "Pendientes": pendientes,
                "Aceptadas": aceptadas,
                "Finalizadas": finalizadas
            })

        df_resumen = pd.DataFrame(resumen)
        st.dataframe(df_resumen, use_container_width=True)

        st.subheader("🏆 Clientes más activos")

        clientes = {}

        for s in solicitudes:
            cliente = s.get("Cliente", "")
            if cliente:
                clientes[cliente] = clientes.get(cliente, 0) + 1

        df_clientes = pd.DataFrame(
            [{"Cliente": k, "Solicitudes": v} for k, v in clientes.items()]
        ).sort_values("Solicitudes", ascending=False) if clientes else pd.DataFrame()

        if not df_clientes.empty:
            st.dataframe(df_clientes, use_container_width=True)
        else:
            st.info("No hay datos de clientes todavía.")

        st.subheader("🛠️ Colaboradores con más servicios")

        conteo_colaboradores = {}

        for s in solicitudes:
            colaborador = s.get("Colaborador", "")
            if colaborador:
                conteo_colaboradores[colaborador] = conteo_colaboradores.get(colaborador, 0) + 1

        df_colaboradores_resumen = pd.DataFrame(
            [{"Colaborador": k, "Servicios tomados": v} for k, v in conteo_colaboradores.items()]
        ).sort_values("Servicios tomados", ascending=False) if conteo_colaboradores else pd.DataFrame()

        if not df_colaboradores_resumen.empty:
            st.dataframe(df_colaboradores_resumen, use_container_width=True)
        else:
            st.info("No hay servicios aceptados todavía.")

    with tab2:
        st.subheader("👤 Usuarios registrados")

        if usuarios:
            st.dataframe(pd.DataFrame(usuarios), use_container_width=True)

            for u in usuarios:
                with st.expander(f"Eliminar usuario: {u.get('Nombre', '')} {u.get('Primer apellido', '')}"):
                    st.warning("Esta acción eliminará el usuario de Google Sheets.")

                    if st.button(
                        f"🗑️ Eliminar usuario {u.get('ID')}",
                        key=f"eliminar_usuario_{u.get('ID')}",
                        use_container_width=True
                    ):
                        eliminar_fila(
                            HOJA_USUARIOS,
                            ENCABEZADOS_USUARIOS,
                            u["_fila"]
                        )

                        st.success("Usuario eliminado correctamente.")
                        st.rerun()
        else:
            st.info("No hay usuarios registrados.")

    with tab3:
        st.subheader("🛠️ Colaboradores registrados")

        if colaboradores:
            st.dataframe(pd.DataFrame(colaboradores), use_container_width=True)

            for c in colaboradores:
                nombre = (
                    f'{c.get("Nombre", "")} '
                    f'{c.get("Primer apellido", "")} '
                    f'{c.get("Segundo apellido", "")}'
                ).strip()

                with st.expander(f"Eliminar colaborador: {nombre}"):
                    st.warning("Esta acción eliminará el colaborador de Google Sheets.")

                    if st.button(
                        f"🗑️ Eliminar colaborador {c.get('ID')}",
                        key=f"eliminar_colaborador_{c.get('ID')}",
                        use_container_width=True
                    ):
                        eliminar_fila(
                            HOJA_COLABORADORES,
                            ENCABEZADOS_COLABORADORES,
                            c["_fila"]
                        )

                        st.success("Colaborador eliminado correctamente.")
                        st.rerun()
        else:
            st.info("No hay colaboradores registrados.")

    with tab4:
        st.subheader("📋 Solicitudes registradas")

        if solicitudes:
            st.dataframe(pd.DataFrame(solicitudes), use_container_width=True)
        else:
            st.info("No hay solicitudes registradas.")


# =========================================================
# EJECUCIÓN PRINCIPAL
# =========================================================

inicializar_estado()

if st.session_state.pagina == "login":
    pagina_login()

elif st.session_state.pagina == "admin_login":
    pagina_admin_login()

elif st.session_state.pagina == "panel_admin":
    if st.session_state.admin_autenticado:
        pagina_panel_admin()
    else:
        st.session_state.pagina = "admin_login"
        st.rerun()

elif st.session_state.pagina == "panel_usuario":
    if st.session_state.usuario_actual:
        pagina_panel_usuario()
    else:
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "servicio_usuario":
    if st.session_state.usuario_actual:
        pagina_servicio_usuario()
    else:
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "panel_colaborador":
    if st.session_state.colaborador_actual:
        pagina_panel_colaborador()
    else:
        st.session_state.pagina = "login"
        st.rerun()

else:
    st.session_state.pagina = "login"
    st.rerun()
