import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from urllib.parse import quote
import uuid
import time
import random

# =========================================================
# APP EXPRESS - DEMO CON GOOGLE SHEETS
# Base: https://docs.google.com/spreadsheets/d/1LSnqaX5qDsw1Tq-qdknohQPr6XX09JnqAM0-4CiqC0E/edit
# Hojas usadas/creadas:
# - Usuarios
# - Colaboradores
# - Solicitudes
# =========================================================

st.set_page_config(
    page_title="Express Local",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)

SPREADSHEET_ID = "1LSnqaX5qDsw1Tq-qdknohQPr6XX09JnqAM0-4CiqC0E"
ADMIN_WHATSAPP = "50663009645"

CLAVES_COLABORADOR = {
    "Taxi": ["TAXI-101", "TAXI-202", "TAXI-303", "TAXI-404", "TAXI-505", "TAXI-606"],
    "Express": ["EXP-101", "EXP-202", "EXP-303", "EXP-404", "EXP-505", "EXP-606"],
    "Carga": ["CAR-101", "CAR-202", "CAR-303", "CAR-404", "CAR-505", "CAR-606"],
    "Camión": ["CAM-101", "CAM-202", "CAM-303", "CAM-404", "CAM-505", "CAM-606"],
}

SERVICIOS = {
    "Taxi": {
        "icono": "🚕",
        "clase": "taxi",
        "titulo": "Taxi local",
        "descripcion": "Viajes dentro y fuera de la comunidad, traslados rápidos y servicios programados.",
        "color": "#f59e0b",
        "frase": "Solicite un taxi disponible y coordine el viaje por WhatsApp.",
    },
    "Express": {
        "icono": "🛵",
        "clase": "express",
        "titulo": "Express",
        "descripcion": "Mandados, compras, documentos, comida, entregas pequeñas y servicios rápidos.",
        "color": "#ef4444",
        "frase": "Pida su express y conecte con el colaborador disponible.",
    },
    "Carga": {
        "icono": "📦",
        "clase": "carga",
        "titulo": "Carga liviana",
        "descripcion": "Traslado de paquetes medianos, compras grandes, artículos y entregas especiales.",
        "color": "#2563eb",
        "frase": "Coordine carga liviana con personas disponibles en su zona.",
    },
    "Camión": {
        "icono": "🚚",
        "clase": "camion",
        "titulo": "Camión",
        "descripcion": "Mudanzas, materiales, carga pesada y transporte especial según disponibilidad.",
        "color": "#16a34a",
        "frase": "Busque camión disponible y coordine detalles directamente.",
    },
}

PROMOCIONES = [
    {"titulo": "Promo restaurante", "texto": "Espacio listo para imagen de promoción 1", "emoji": "🍔", "color": "#ef4444"},
    {"titulo": "Servicio destacado", "texto": "Espacio listo para imagen de promoción 2", "emoji": "🛵", "color": "#f97316"},
    {"titulo": "Oferta local", "texto": "Espacio listo para imagen de promoción 3", "emoji": "🥤", "color": "#22c55e"},
    {"titulo": "Comercio aliado", "texto": "Espacio listo para imagen de promoción 4", "emoji": "🛒", "color": "#2563eb"},
]

USUARIOS_DEMO = [
    ["U001", "Ana", "Mora", "Solís", "87001111", "anamora", "1234", "Usuario", fecha_actual := datetime.now().strftime("%d/%m/%Y %H:%M")],
    ["U002", "Luis", "Castro", "Vega", "87002222", "luiscastro", "1234", "Usuario", fecha_actual],
    ["U003", "María", "Rojas", "López", "87003333", "mariarojas", "1234", "Usuario", fecha_actual],
    ["U004", "José", "Vargas", "Arias", "87004444", "josevargas", "1234", "Usuario", fecha_actual],
    ["U005", "Daniela", "Campos", "Ruiz", "87005555", "danicampos", "1234", "Usuario", fecha_actual],
    ["U006", "Carlos", "Ramírez", "Soto", "87006666", "carlosramirez", "1234", "Usuario", fecha_actual],
]

COLABORADORES_DEMO = []
for servicio, prefijo in [("Taxi", "TAX"), ("Express", "EXP"), ("Carga", "CAR"), ("Camión", "CAM")]:
    for i in range(1, 6):
        COLABORADORES_DEMO.append([
            f"{prefijo}{i:03d}",
            f"Colaborador {servicio} {i}",
            "Demo",
            "Local",
            f"8800{len(COLABORADORES_DEMO)+1:04d}",
            f"{servicio.lower()}{i}",
            "1234",
            servicio,
            "Disponible" if i <= 3 else "Fuera de servicio",
            fecha_actual,
        ])

CSS = """
<style>
:root, html, body, .stApp { color-scheme: light !important; background: #fff7ed !important; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #111827 0%, #1f2937 50%, #7c2d12 100%) !important; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stHeader"] { background: rgba(255, 247, 237, 0.78) !important; }
h1, h2, h3, h4, p, label, span, div { color: #111827; }
.stTextInput input, .stPassword input, .stSelectbox div[data-baseweb="select"] > div, textarea {
    border-radius: 16px !important; border: 1px solid #fed7aa !important; background: white !important;
}
.stButton > button, .stFormSubmitButton > button {
    width: 100%; min-height: 46px; border-radius: 16px; border: 0; font-weight: 900;
    background: linear-gradient(135deg, #f97316, #ef4444); color: white !important;
    box-shadow: 0 10px 22px rgba(239, 68, 68, .18);
}
.stButton > button:hover, .stFormSubmitButton > button:hover { filter: brightness(.95); color: white !important; }
.stLinkButton > a {
    width: 100%; min-height: 46px; border-radius: 16px; border: 0; font-weight: 900;
    background: linear-gradient(135deg, #22c55e, #16a34a) !important; color: white !important;
    display: flex; align-items: center; justify-content: center;
}
.hero {
    border-radius: 32px; padding: 34px; margin-bottom: 18px;
    background: radial-gradient(circle at top left, #fde68a, transparent 30%), linear-gradient(135deg, #f97316, #ef4444 55%, #7c3aed);
    color: white !important; box-shadow: 0 20px 40px rgba(124,45,18,.25);
}
.hero * { color: white !important; }
.hero h1 { font-size: 48px; line-height: 1; margin: 0 0 12px 0; font-weight: 1000; }
.hero p { font-size: 19px; margin: 0; opacity: .96; }
.card {
    background: rgba(255,255,255,.95); border: 1px solid #ffedd5; border-radius: 26px;
    padding: 24px; box-shadow: 0 14px 28px rgba(124,45,18,.08); margin-bottom: 16px;
}
.login-card { min-height: 245px; }
.badge { display: inline-block; padding: 8px 13px; border-radius: 999px; font-weight: 900; font-size: 13px; }
.ok { background: #dcfce7; color: #166534 !important; }
.warn { background: #fef3c7; color: #92400e !important; }
.danger { background: #fee2e2; color: #991b1b !important; }
.gray { background: #e5e7eb; color: #374151 !important; }
.blue { background: #dbeafe; color: #1d4ed8 !important; }
.service-card {
    border-radius: 28px; padding: 25px; min-height: 210px; color: white !important;
    box-shadow: 0 18px 34px rgba(17,24,39,.16); transition: all .18s ease; margin-bottom: 8px;
}
.service-card:hover { transform: translateY(-3px); }
.service-card * { color: white !important; }
.service-card h2 { font-size: 34px; margin: 0 0 8px 0; font-weight: 1000; }
.taxi { background: linear-gradient(135deg, #f59e0b, #facc15); }
.express { background: linear-gradient(135deg, #ef4444, #f97316); }
.carga { background: linear-gradient(135deg, #2563eb, #06b6d4); }
.camion { background: linear-gradient(135deg, #16a34a, #84cc16); }
.promo {
    border-radius: 30px; padding: 28px; min-height: 185px; display: flex; align-items: center;
    justify-content: space-between; color: white !important; box-shadow: 0 20px 38px rgba(17,24,39,.14);
}
.promo * { color: white !important; }
.promo-emoji { font-size: 82px; line-height: 1; }
.worker-row { border-left: 8px solid #f97316; }
.whatsapp-box { background: #052e16; border-radius: 22px; padding: 20px; margin-top: 12px; }
.whatsapp-box * { color: white !important; }
.small-muted { color: #6b7280 !important; font-size: 14px; }
@media(max-width: 768px) { .hero h1 { font-size: 34px; } .service-card { min-height: 165px; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# =========================================================
# CONEXIÓN GOOGLE SHEETS
# =========================================================

def normalizar_usuario(valor: str) -> str:
    return str(valor or "").strip().lower().replace(" ", "")


def limpiar_telefono(valor: str) -> str:
    tel = "".join([c for c in str(valor or "") if c.isdigit()])
    if tel.startswith("506"):
        return tel
    return f"506{tel}" if tel else ""


def whatsapp_link(numero: str, mensaje: str) -> str:
    numero_limpio = limpiar_telefono(numero)
    return f"https://wa.me/{numero_limpio}?text={quote(mensaje)}"


def obtener_credenciales():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    if "gcp_service_account" not in st.secrets:
        st.error("Falta configurar st.secrets['gcp_service_account'] con las credenciales de Google Sheets.")
        st.stop()
    return Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)


@st.cache_resource(show_spinner=False)
def conectar_google_sheets():
    creds = obtener_credenciales()
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


def obtener_hoja(nombre: str, encabezados: list[str]):
    libro = conectar_google_sheets()
    try:
        hoja = libro.worksheet(nombre)
    except gspread.WorksheetNotFound:
        hoja = libro.add_worksheet(title=nombre, rows=1000, cols=max(20, len(encabezados)))
    valores = hoja.get_all_values()
    if not valores:
        hoja.append_row(encabezados)
    elif valores[0] != encabezados:
        # Si la hoja existe pero no tiene encabezados correctos, no borra datos: solo muestra advertencia.
        pass
    return hoja


HEADERS_USUARIOS = ["id", "nombre", "primer_apellido", "segundo_apellido", "telefono", "usuario", "clave", "tipo", "fecha_registro"]
HEADERS_COLABORADORES = ["id", "nombre", "primer_apellido", "segundo_apellido", "telefono", "usuario", "clave", "servicio", "estado", "fecha_registro"]
HEADERS_SOLICITUDES = [
    "id", "fecha", "servicio", "usuario_cliente", "cliente_nombre", "telefono_cliente", "colaborador_id",
    "colaborador_nombre", "telefono_colaborador", "estado", "detalle", "origen", "destino", "aceptado_fecha"
]


def cargar_df(nombre: str, encabezados: list[str]) -> pd.DataFrame:
    hoja = obtener_hoja(nombre, encabezados)
    data = hoja.get_all_records()
    df = pd.DataFrame(data)
    for col in encabezados:
        if col not in df.columns:
            df[col] = ""
    return df[encabezados]


def append_row(nombre: str, encabezados: list[str], row: list):
    hoja = obtener_hoja(nombre, encabezados)
    hoja.append_row(row, value_input_option="USER_ENTERED")


def actualizar_celda_por_id(nombre: str, encabezados: list[str], id_registro: str, columna: str, valor: str):
    hoja = obtener_hoja(nombre, encabezados)
    valores = hoja.get_all_values()
    if not valores:
        return False
    header = valores[0]
    if columna not in header:
        return False
    col_idx = header.index(columna) + 1
    for i, fila in enumerate(valores[1:], start=2):
        if fila and fila[0] == id_registro:
            hoja.update_cell(i, col_idx, valor)
            return True
    return False


def actualizar_varias_celdas_por_id(nombre: str, encabezados: list[str], id_registro: str, cambios: dict):
    hoja = obtener_hoja(nombre, encabezados)
    valores = hoja.get_all_values()
    if not valores:
        return False
    header = valores[0]
    fila_idx = None
    for i, fila in enumerate(valores[1:], start=2):
        if fila and fila[0] == id_registro:
            fila_idx = i
            break
    if fila_idx is None:
        return False
    for columna, valor in cambios.items():
        if columna in header:
            hoja.update_cell(fila_idx, header.index(columna) + 1, valor)
    return True


def sembrar_datos_demo():
    df_u = cargar_df("Usuarios", HEADERS_USUARIOS)
    df_c = cargar_df("Colaboradores", HEADERS_COLABORADORES)
    if df_u.empty:
        hoja_u = obtener_hoja("Usuarios", HEADERS_USUARIOS)
        hoja_u.append_rows(USUARIOS_DEMO, value_input_option="USER_ENTERED")
    if df_c.empty:
        hoja_c = obtener_hoja("Colaboradores", HEADERS_COLABORADORES)
        hoja_c.append_rows(COLABORADORES_DEMO, value_input_option="USER_ENTERED")


try:
    sembrar_datos_demo()
except Exception as e:
    st.error(f"No se pudo conectar o preparar la base de datos: {e}")
    st.stop()

# =========================================================
# ESTADO DE SESIÓN
# =========================================================

for key, default in {
    "autenticado": False,
    "rol": None,
    "perfil": {},
    "pagina": "login",
    "servicio_seleccionado": None,
    "promo_index": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def cerrar_sesion():
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.session_state.perfil = {}
    st.session_state.pagina = "login"
    st.session_state.servicio_seleccionado = None


def nombre_completo(row) -> str:
    return f"{row.get('nombre','')} {row.get('primer_apellido','')} {row.get('segundo_apellido','')}".strip()


def estado_badge(estado: str) -> str:
    estado = str(estado or "").strip()
    if estado == "Disponible":
        return '<span class="badge ok">🟢 Disponible</span>'
    if estado == "Ocupado":
        return '<span class="badge danger">🔴 Ocupado</span>'
    if estado == "Fuera de servicio":
        return '<span class="badge gray">⚫ Fuera de servicio</span>'
    if estado == "Pendiente":
        return '<span class="badge warn">⏳ Pendiente</span>'
    if estado == "Aceptado":
        return '<span class="badge blue">✅ Aceptado</span>'
    if estado == "Finalizado":
        return '<span class="badge ok">🏁 Finalizado</span>'
    if estado == "Cancelado":
        return '<span class="badge danger">❌ Cancelado</span>'
    return f'<span class="badge gray">{estado}</span>'


def hero(titulo, texto, icono="🛵"):
    st.markdown(f"""
    <div class="hero">
        <h1>{icono} {titulo}</h1>
        <p>{texto}</p>
    </div>
    """, unsafe_allow_html=True)


def mostrar_promo_carousel():
    idx = int(time.time() / 4) % len(PROMOCIONES)
    promo = PROMOCIONES[idx]
    st.markdown(f"""
    <div class="promo" style="background: linear-gradient(135deg, {promo['color']}, #7c3aed);">
        <div>
            <h2>{promo['titulo']}</h2>
            <p>{promo['texto']}</p>
            <p class="small-muted" style="color:white!important; opacity:.90;">Este espacio se puede sustituir luego por imágenes reales de restaurantes o comercios.</p>
        </div>
        <div class="promo-emoji">{promo['emoji']}</div>
    </div>
    """, unsafe_allow_html=True)


def menu_lateral():
    with st.sidebar:
        st.markdown("# 🛵 Express Local")
        st.markdown("---")
        if st.session_state.autenticado:
            st.success(f"Sesión: {st.session_state.rol}")
            st.write(nombre_completo(st.session_state.perfil))
            if st.button("🏠 Inicio", use_container_width=True):
                st.session_state.pagina = "panel"
                st.rerun()
            if st.button("✏️ Cambiar mis datos", use_container_width=True):
                st.session_state.pagina = "perfil"
                st.rerun()
            mensaje = "Hola, necesito ayuda con la app de Express Local."
            st.link_button("💬 Ayuda por WhatsApp", whatsapp_link(ADMIN_WHATSAPP, mensaje), use_container_width=True)
            if st.button("🚪 Cerrar sesión", use_container_width=True):
                cerrar_sesion()
                st.rerun()
        else:
            st.info("Ingrese o regístrese para usar la app.")
        st.markdown("---")
        st.caption("Claves demo colaborador")
        st.code("Taxi: TAXI-101 a TAXI-606\nExpress: EXP-101 a EXP-606\nCarga: CAR-101 a CAR-606\nCamión: CAM-101 a CAM-606")


menu_lateral()

# =========================================================
# LOGIN Y REGISTRO
# =========================================================

def validar_telefono(tel: str) -> bool:
    digitos = "".join([c for c in str(tel) if c.isdigit()])
    if digitos.startswith("506"):
        digitos = digitos[3:]
    return len(digitos) == 8


def usuario_existe(usuario: str) -> bool:
    u = normalizar_usuario(usuario)
    df_u = cargar_df("Usuarios", HEADERS_USUARIOS)
    df_c = cargar_df("Colaboradores", HEADERS_COLABORADORES)
    usuarios = set(df_u["usuario"].astype(str).map(normalizar_usuario).tolist()) | set(df_c["usuario"].astype(str).map(normalizar_usuario).tolist())
    return u in usuarios


def registrar_usuario(nombre, p1, p2, telefono, usuario, clave):
    if usuario_existe(usuario):
        st.error("Ese nombre de usuario ya existe. Use otro.")
        return False
    if not validar_telefono(telefono):
        st.error("El teléfono debe tener 8 dígitos de Costa Rica. Puede escribirlo con o sin 506.")
        return False
    row = [str(uuid.uuid4())[:8], nombre.strip(), p1.strip(), p2.strip(), limpiar_telefono(telefono), normalizar_usuario(usuario), clave, "Usuario", datetime.now().strftime("%d/%m/%Y %H:%M")]
    append_row("Usuarios", HEADERS_USUARIOS, row)
    st.success("Usuario registrado correctamente. Ahora puede ingresar.")
    return True


def registrar_colaborador(nombre, p1, p2, telefono, usuario, clave, servicio, clave_autorizacion):
    if clave_autorizacion not in CLAVES_COLABORADOR.get(servicio, []):
        st.error("La clave de autorización no corresponde al servicio seleccionado.")
        return False
    if usuario_existe(usuario):
        st.error("Ese nombre de usuario ya existe. Use otro.")
        return False
    if not validar_telefono(telefono):
        st.error("El teléfono debe tener 8 dígitos de Costa Rica. Puede escribirlo con o sin 506.")
        return False
    row = [str(uuid.uuid4())[:8], nombre.strip(), p1.strip(), p2.strip(), limpiar_telefono(telefono), normalizar_usuario(usuario), clave, servicio, "Disponible", datetime.now().strftime("%d/%m/%Y %H:%M")]
    append_row("Colaboradores", HEADERS_COLABORADORES, row)
    st.success("Colaborador registrado correctamente. Ahora puede ingresar.")
    return True


def login(usuario, clave, rol):
    usuario_n = normalizar_usuario(usuario)
    if rol == "Usuario":
        df = cargar_df("Usuarios", HEADERS_USUARIOS)
    else:
        df = cargar_df("Colaboradores", HEADERS_COLABORADORES)
    if df.empty:
        st.error("No hay registros disponibles.")
        return
    df["usuario_norm"] = df["usuario"].astype(str).map(normalizar_usuario)
    match = df[(df["usuario_norm"] == usuario_n) & (df["clave"].astype(str) == str(clave))]
    if match.empty:
        st.error("Usuario o clave incorrecta.")
        return
    st.session_state.autenticado = True
    st.session_state.rol = rol
    st.session_state.perfil = match.iloc[0].to_dict()
    st.session_state.pagina = "panel"
    st.rerun()


if not st.session_state.autenticado:
    hero("Express Local", "Demo colorido para usuarios y colaboradores: taxi, express, carga y camión.", "🚀")
    tab1, tab2, tab3, tab4 = st.tabs(["Ingresar usuario", "Registrar usuario", "Ingresar colaborador", "Registrar colaborador"])

    with tab1:
        st.markdown('<div class="card login-card"><h2>👤 Ingreso de usuario</h2><p>Ingrese con su usuario registrado para solicitar servicios.</p></div>', unsafe_allow_html=True)
        with st.form("login_usuario"):
            u = st.text_input("Nombre de usuario", key="lu")
            c = st.text_input("Clave", type="password", key="lc")
            if st.form_submit_button("Ingresar como usuario"):
                login(u, c, "Usuario")

    with tab2:
        st.markdown('<div class="card login-card"><h2>📝 Registro de usuario</h2><p>Complete sus datos. El nombre de usuario no se puede repetir.</p></div>', unsafe_allow_html=True)
        with st.form("registro_usuario"):
            c1, c2, c3 = st.columns(3)
            nombre = c1.text_input("Nombre")
            p1 = c2.text_input("Primer apellido")
            p2 = c3.text_input("Segundo apellido")
            telefono = st.text_input("Número de teléfono")
            usuario = st.text_input("Nombre de usuario")
            clave = st.text_input("Clave", type="password")
            if st.form_submit_button("Registrar usuario"):
                if not all([nombre, p1, p2, telefono, usuario, clave]):
                    st.error("Complete todos los campos.")
                else:
                    registrar_usuario(nombre, p1, p2, telefono, usuario, clave)

    with tab3:
        st.markdown('<div class="card login-card"><h2>🧰 Ingreso de colaborador</h2><p>Los colaboradores registrados ingresan con su usuario y clave.</p></div>', unsafe_allow_html=True)
        with st.form("login_colaborador"):
            u = st.text_input("Nombre de usuario", key="lcu")
            c = st.text_input("Clave", type="password", key="lcc")
            if st.form_submit_button("Ingresar como colaborador"):
                login(u, c, "Colaborador")

    with tab4:
        st.markdown('<div class="card login-card"><h2>🔐 Registro de colaborador</h2><p>Debe tener una clave autorizada por el coordinador para registrarse.</p></div>', unsafe_allow_html=True)
        with st.form("registro_colaborador"):
            c1, c2, c3 = st.columns(3)
            nombre = c1.text_input("Nombre", key="cn")
            p1 = c2.text_input("Primer apellido", key="cp1")
            p2 = c3.text_input("Segundo apellido", key="cp2")
            telefono = st.text_input("Número de teléfono", key="ct")
            usuario = st.text_input("Nombre de usuario", key="cu")
            clave = st.text_input("Clave de ingreso", type="password", key="cc")
            servicio = st.selectbox("Servicio que brindará", list(SERVICIOS.keys()), key="cs")
            clave_aut = st.text_input("Clave dada por el coordinador", type="password", key="ca")
            if st.form_submit_button("Registrar colaborador"):
                if not all([nombre, p1, p2, telefono, usuario, clave, servicio, clave_aut]):
                    st.error("Complete todos los campos.")
                else:
                    registrar_colaborador(nombre, p1, p2, telefono, usuario, clave, servicio, clave_aut)

    st.stop()

# =========================================================
# PERFIL
# =========================================================

if st.session_state.pagina == "perfil":
    hero("Mis datos", "Actualice su información básica de contacto.", "✏️")
    perfil = st.session_state.perfil
    with st.form("actualizar_perfil"):
        c1, c2, c3 = st.columns(3)
        nombre = c1.text_input("Nombre", value=str(perfil.get("nombre", "")))
        p1 = c2.text_input("Primer apellido", value=str(perfil.get("primer_apellido", "")))
        p2 = c3.text_input("Segundo apellido", value=str(perfil.get("segundo_apellido", "")))
        telefono = st.text_input("Teléfono", value=str(perfil.get("telefono", "")))
        if st.form_submit_button("Guardar cambios"):
            if not validar_telefono(telefono):
                st.error("Teléfono inválido.")
            else:
                hoja = "Usuarios" if st.session_state.rol == "Usuario" else "Colaboradores"
                headers = HEADERS_USUARIOS if st.session_state.rol == "Usuario" else HEADERS_COLABORADORES
                actualizar_varias_celdas_por_id(hoja, headers, perfil["id"], {
                    "nombre": nombre,
                    "primer_apellido": p1,
                    "segundo_apellido": p2,
                    "telefono": limpiar_telefono(telefono),
                })
                st.session_state.perfil.update({"nombre": nombre, "primer_apellido": p1, "segundo_apellido": p2, "telefono": limpiar_telefono(telefono)})
                st.success("Datos actualizados.")
    st.stop()

# =========================================================
# PANEL USUARIO
# =========================================================

if st.session_state.rol == "Usuario":
    perfil = st.session_state.perfil
    hero(f"Hola, {perfil.get('nombre')}", "Seleccione un servicio, revise colaboradores disponibles y coordine por WhatsApp.", "👤")
    mostrar_promo_carousel()
    st.write("")

    st.subheader("Servicios disponibles")
    cols = st.columns(4)
    for i, (servicio, data) in enumerate(SERVICIOS.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="service-card {data['clase']}">
                <h2>{data['icono']}<br>{data['titulo']}</h2>
                <p>{data['descripcion']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Entrar a {servicio}", key=f"entrar_{servicio}"):
                st.session_state.servicio_seleccionado = servicio
                st.rerun()

    servicio = st.session_state.servicio_seleccionado
    if servicio:
        data = SERVICIOS[servicio]
        st.markdown("---")
        st.markdown(f"""
        <div class="card">
            <h2>{data['icono']} {data['titulo']}</h2>
            <p>{data['frase']}</p>
        </div>
        """, unsafe_allow_html=True)

        df_col = cargar_df("Colaboradores", HEADERS_COLABORADORES)
        df_col = df_col[df_col["servicio"].astype(str) == servicio]

        st.subheader("Colaboradores del servicio")
        if df_col.empty:
            st.info("Todavía no hay colaboradores registrados para este servicio.")
        else:
            for _, row in df_col.iterrows():
                st.markdown(f"""
                <div class="card worker-row">
                    <h3>{nombre_completo(row)}</h3>
                    <p><b>Servicio:</b> {row['servicio']} &nbsp; <b>Estado:</b> {estado_badge(row['estado'])}</p>
                    <p><b>Teléfono:</b> {row['telefono']}</p>
                </div>
                """, unsafe_allow_html=True)

        st.subheader("Hacer llamado a colaboradores disponibles")
        disponibles = df_col[df_col["estado"].astype(str) == "Disponible"]
        if disponibles.empty:
            st.warning("No hay colaboradores disponibles en este momento.")
        else:
            with st.form("crear_solicitud_broadcast"):
                origen = st.text_input("Lugar de salida / recogida / compra")
                destino = st.text_input("Lugar de destino / entrega")
                detalle = st.text_area("Detalle del servicio solicitado")
                enviar = st.form_submit_button("📣 Enviar solicitud a disponibles")
                if enviar:
                    solicitud_id = str(uuid.uuid4())[:8]
                    append_row("Solicitudes", HEADERS_SOLICITUDES, [
                        solicitud_id,
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        servicio,
                        perfil["usuario"],
                        nombre_completo(perfil),
                        perfil["telefono"],
                        "",
                        "",
                        "",
                        "Pendiente",
                        detalle,
                        origen,
                        destino,
                        "",
                    ])
                    st.success("Solicitud enviada. Los colaboradores disponibles de ese servicio podrán aceptarla.")
                    st.rerun()

    st.markdown("---")
    st.subheader("Mis solicitudes")
    df_sol = cargar_df("Solicitudes", HEADERS_SOLICITUDES)
    df_mis = df_sol[df_sol["usuario_cliente"].astype(str) == str(perfil.get("usuario"))]
    if df_mis.empty:
        st.info("No tiene solicitudes registradas.")
    else:
        for _, s in df_mis.sort_values("fecha", ascending=False).iterrows():
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['id']} - {s['servicio']}</h3>
                <p><b>Estado:</b> {estado_badge(s['estado'])}</p>
                <p><b>Detalle:</b> {s['detalle']}</p>
                <p><b>Origen:</b> {s['origen']}</p>
                <p><b>Destino:</b> {s['destino']}</p>
                <p><b>Colaborador asignado:</b> {s['colaborador_nombre'] if s['colaborador_nombre'] else 'Pendiente de aceptación'}</p>
            </div>
            """, unsafe_allow_html=True)
            if str(s["estado"]) == "Aceptado" and str(s["telefono_colaborador"]):
                msg = f"Hola {s['colaborador_nombre']}, soy {s['cliente_nombre']}. Mi solicitud es #{s['id']} para {s['servicio']}. Origen: {s['origen']}. Destino: {s['destino']}."
                st.link_button("💬 Chatear con colaborador por WhatsApp", whatsapp_link(s["telefono_colaborador"], msg), use_container_width=True)

# =========================================================
# PANEL COLABORADOR
# =========================================================

if st.session_state.rol == "Colaborador":
    perfil = st.session_state.perfil
    servicio = perfil.get("servicio")
    data = SERVICIOS.get(servicio, SERVICIOS["Express"])
    hero(f"Panel {servicio}", "Administre su estado y acepte solicitudes pendientes de su servicio.", data["icono"])
    mostrar_promo_carousel()

    st.markdown(f"""
    <div class="card" style="border-left: 10px solid {data['color']};">
        <h2>{nombre_completo(perfil)}</h2>
        <p><b>Servicio:</b> {servicio}</p>
        <p><b>Teléfono:</b> {perfil.get('telefono')}</p>
        <p><b>Estado actual:</b> {estado_badge(perfil.get('estado'))}</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        nuevo_estado = st.selectbox("Cambiar estado", ["Disponible", "Ocupado", "Fuera de servicio"], index=["Disponible", "Ocupado", "Fuera de servicio"].index(perfil.get("estado", "Disponible")))
    with c2:
        st.write("")
        st.write("")
        if st.button("Actualizar estado"):
            actualizar_celda_por_id("Colaboradores", HEADERS_COLABORADORES, perfil["id"], "estado", nuevo_estado)
            st.session_state.perfil["estado"] = nuevo_estado
            st.success("Estado actualizado.")
            st.rerun()

    st.markdown("---")
    st.subheader("Solicitudes pendientes para mi servicio")
    df_sol = cargar_df("Solicitudes", HEADERS_SOLICITUDES)
    pendientes = df_sol[(df_sol["servicio"].astype(str) == str(servicio)) & (df_sol["estado"].astype(str) == "Pendiente")]
    if perfil.get("estado") != "Disponible":
        st.warning("Para aceptar nuevas solicitudes debe estar en estado Disponible.")
    elif pendientes.empty:
        st.info("No hay solicitudes pendientes para este servicio.")
    else:
        for _, s in pendientes.iterrows():
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['id']}</h3>
                <p><b>Cliente:</b> {s['cliente_nombre']}</p>
                <p><b>Teléfono cliente:</b> {s['telefono_cliente']}</p>
                <p><b>Origen:</b> {s['origen']}</p>
                <p><b>Destino:</b> {s['destino']}</p>
                <p><b>Detalle:</b> {s['detalle']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"✅ Aceptar solicitud #{s['id']}", key=f"aceptar_{s['id']}"):
                ok = actualizar_varias_celdas_por_id("Solicitudes", HEADERS_SOLICITUDES, s["id"], {
                    "colaborador_id": perfil["id"],
                    "colaborador_nombre": nombre_completo(perfil),
                    "telefono_colaborador": perfil["telefono"],
                    "estado": "Aceptado",
                    "aceptado_fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                })
                if ok:
                    actualizar_celda_por_id("Colaboradores", HEADERS_COLABORADORES, perfil["id"], "estado", "Ocupado")
                    st.session_state.perfil["estado"] = "Ocupado"
                    st.success("Solicitud aceptada. El usuario verá su contacto para WhatsApp.")
                    st.rerun()

    st.markdown("---")
    st.subheader("Mis servicios aceptados")
    df_sol = cargar_df("Solicitudes", HEADERS_SOLICITUDES)
    asignadas = df_sol[df_sol["colaborador_id"].astype(str) == str(perfil.get("id"))]
    if asignadas.empty:
        st.info("Aún no tiene solicitudes aceptadas.")
    else:
        for _, s in asignadas.sort_values("fecha", ascending=False).iterrows():
            st.markdown(f"""
            <div class="card">
                <h3>Solicitud #{s['id']} - {s['servicio']}</h3>
                <p><b>Estado:</b> {estado_badge(s['estado'])}</p>
                <p><b>Cliente:</b> {s['cliente_nombre']} | {s['telefono_cliente']}</p>
                <p><b>Origen:</b> {s['origen']}</p>
                <p><b>Destino:</b> {s['destino']}</p>
                <p><b>Detalle:</b> {s['detalle']}</p>
            </div>
            """, unsafe_allow_html=True)
            msg = f"Hola {s['cliente_nombre']}, soy {nombre_completo(perfil)}. Acepté su solicitud #{s['id']} para {s['servicio']}."
            st.link_button("💬 Chatear con usuario por WhatsApp", whatsapp_link(s["telefono_cliente"], msg), use_container_width=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button(f"Finalizar #{s['id']}", key=f"fin_{s['id']}"):
                    actualizar_celda_por_id("Solicitudes", HEADERS_SOLICITUDES, s["id"], "estado", "Finalizado")
                    actualizar_celda_por_id("Colaboradores", HEADERS_COLABORADORES, perfil["id"], "estado", "Disponible")
                    st.session_state.perfil["estado"] = "Disponible"
                    st.rerun()
            with cc2:
                if st.button(f"Cancelar #{s['id']}", key=f"can_{s['id']}"):
                    actualizar_celda_por_id("Solicitudes", HEADERS_SOLICITUDES, s["id"], "estado", "Cancelado")
                    actualizar_celda_por_id("Colaboradores", HEADERS_COLABORADORES, perfil["id"], "estado", "Disponible")
                    st.session_state.perfil["estado"] = "Disponible"
                    st.rerun()
