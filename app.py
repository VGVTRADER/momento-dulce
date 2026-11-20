import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator
from core import check_login, load_users, save_users, hash_pw, cuenta_pendiente
import usuarios as mod_usuarios

st.set_page_config(page_title="Momento Dulce Scanner", page_icon="🎯", layout="wide")

# ── Tema visual TradingView dark ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── Paleta TradingView dark ── */
:root {
    --tv-bg:       #131722;
    --tv-panel:    #1e222d;
    --tv-panel2:   #2a2e39;
    --tv-border:   #2a2e39;
    --tv-border2:  #363a45;
    --tv-text:     #d1d4dc;
    --tv-muted:    #787b86;
    --tv-subtle:   #4c525e;
    --tv-green:    #089981;
    --tv-green-lt: #26a69a;
    --tv-red:      #f23645;
    --tv-blue:     #2962ff;
    --tv-blue-lt:  #1e53e5;
    --tv-orange:   #f7525f;
    --tv-yellow:   #f5c518;
}

/* ── Fondo y texto base ── */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main .block-container {
    background-color: var(--tv-bg) !important;
    color: var(--tv-text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Trebuchet MS", Roboto, sans-serif !important;
}
.main .block-container {
    max-width: 100% !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}
section[data-testid="stSidebar"],
button[data-testid="collapsedControl"] {
    display: none !important;
}

/* ── Texto – forzar blanco/claro en TODOS los contextos ── */
h1, h2, h3, h4, h5, h6,
p, span, div, li, label, a,
.stMarkdown, .stMarkdown *,
[data-testid="stText"],
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * {
    color: var(--tv-text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Trebuchet MS", Roboto, sans-serif !important;
}
h1 { font-size: 22px !important; font-weight: 700 !important; }
h2 { font-size: 17px !important; font-weight: 600 !important; }
h3 { font-size: 14px !important; font-weight: 600 !important; }

/* ── Spinner / "procesando" ── */
[data-testid="stSpinner"],
[data-testid="stSpinner"] *,
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span,
.stSpinner > div > div > p {
    color: var(--tv-text) !important;
    background: transparent !important;
}
/* El círculo animado */
[data-testid="stSpinner"] svg { stroke: var(--tv-blue) !important; }


/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--tv-panel) !important;
    border: 1px solid var(--tv-border) !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: var(--tv-panel) !important;
    color: transparent !important;
    font-size: 0 !important;
    line-height: 0 !important;
    padding: 12px 16px !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    list-style: none !important;
    user-select: none !important;
    border-radius: 8px !important;
    transition: background .15s !important;
}
[data-testid="stExpander"] summary:hover { background: var(--tv-panel2) !important; }
[data-testid="stExpander"] summary::-webkit-details-marker,
[data-testid="stExpander"] summary::marker { display: none !important; }
[data-testid="stExpander"] summary p {
    color: #d1d4dc !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    visibility: visible !important;
}
[data-testid="stExpander"] summary svg { display: none !important; }
[data-testid="stExpander"] summary::after {
    content: "▸" !important;
    margin-left: auto !important;
    font-size: 14px !important;
    color: #2962ff !important;
    flex-shrink: 0 !important;
}
[data-testid="stExpander"] details[open] > summary {
    border-bottom: 1px solid var(--tv-border) !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stExpander"] details > div,
[data-testid="stExpander"] .stExpanderDetails {
    background: var(--tv-bg) !important;
    padding: 16px !important;
}

/* ── Header de Streamlit ── */
[data-testid="stHeader"] { background: var(--tv-bg) !important; }

/* ── Todos los inputs: text, number, select ── */
input,
input[type="text"],
input[type="number"],
input[type="search"],
textarea {
    background-color: var(--tv-panel) !important;
    border: 1px solid var(--tv-border2) !important;
    color: var(--tv-text) !important;
    border-radius: 4px !important;
    caret-color: var(--tv-text) !important;
    font-size: 13px !important;
}
input:focus, textarea:focus {
    border-color: var(--tv-blue) !important;
    box-shadow: 0 0 0 2px rgba(41,98,255,.25) !important;
    outline: none !important;
}

/* Contenedor de number_input — la "caja" con bordes */
[data-testid="stNumberInput"] > div,
[data-testid="stNumberInputContainer"] {
    background: var(--tv-panel) !important;
    border: 1px solid var(--tv-border2) !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}
[data-testid="stNumberInput"] input {
    background: transparent !important;
    border: none !important;
    color: var(--tv-text) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
/* Botones +/- del number_input */
[data-testid="stNumberInput"] button {
    background: var(--tv-panel2) !important;
    color: var(--tv-text) !important;
    border: none !important;
    border-left: 1px solid var(--tv-border2) !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    width: 36px !important;
    cursor: pointer !important;
    transition: background .12s !important;
}
[data-testid="stNumberInput"] button:hover {
    background: var(--tv-blue) !important;
    color: #fff !important;
}
/* Label de number_input */
[data-testid="stNumberInput"] label,
[data-testid="stNumberInput"] > label {
    color: var(--tv-text) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
}

/* Contenedor de text_input */
[data-testid="stTextInput"] > div {
    border: 1px solid var(--tv-border2) !important;
    border-radius: 6px !important;
    background: var(--tv-panel) !important;
    overflow: hidden !important;
}
[data-testid="stTextInput"] input {
    background: var(--tv-panel) !important;
    border: none !important;
    color: var(--tv-text) !important;
    font-size: 14px !important;
    box-shadow: none !important;
    padding: 8px 12px !important;
}
[data-testid="stTextInput"] input:focus {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stTextInput"] > div:focus-within {
    border-color: var(--tv-blue) !important;
    box-shadow: 0 0 0 2px rgba(41,98,255,.25) !important;
}
[data-testid="stTextInput"] label {
    color: var(--tv-muted) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .6px !important;
    margin-bottom: 5px !important;
}

/* Select box */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: var(--tv-panel) !important;
    border: 1px solid var(--tv-border2) !important;
    color: var(--tv-text) !important;
    border-radius: 6px !important;
}

/* Placeholder */
::placeholder { color: var(--tv-subtle) !important; opacity: 1 !important; }

/* ── Radio ── */
[data-testid="stRadio"] label { color: var(--tv-text) !important; font-size: 13px !important; }
[data-testid="stRadio"] div[role="radio"] { border-color: var(--tv-border2) !important; }
[data-testid="stRadio"] div[role="radio"][aria-checked="true"] {
    border-color: var(--tv-blue) !important;
    background: var(--tv-blue) !important;
}

/* ── Botones ── */
.stButton > button {
    background-color: var(--tv-panel2) !important;
    color: var(--tv-text) !important;
    border: 1px solid var(--tv-border2) !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
    transition: all .15s !important;
}
.stButton > button:hover {
    background-color: var(--tv-blue) !important;
    border-color: var(--tv-blue) !important;
    color: #fff !important;
}

/* Botón Escanear — primary */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #064d33, #0a6b47) !important;
    color: #ffffff !important;
    border: 1px solid #0d8a5a44 !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    letter-spacing: .4px !important;
    padding: 14px 24px !important;
    box-shadow: 0 4px 20px #064d3366 !important;
    transition: all .2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0a6b47, #0d8a5a) !important;
    box-shadow: 0 6px 28px #064d3388 !important;
    transform: translateY(-1px) !important;
}

/* Botones de filtro: estilos base (el color dinámico lo inyecta Python) */
[id^="wrap-fbtn-"] button {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: var(--tv-text) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--tv-border) !important;
    gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--tv-muted) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border-radius: 0 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--tv-text) !important;
    border-bottom: 2px solid var(--tv-blue) !important;
    background: transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: var(--tv-panel) !important;
    border: 1px solid var(--tv-border) !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
    padding: 16px !important;
}

/* ── Métricas ── */
[data-testid="stMetric"] {
    background: var(--tv-panel) !important;
    border: 1px solid var(--tv-border) !important;
    border-radius: 6px !important;
    padding: 12px 14px !important;
}
[data-testid="stMetricLabel"] { color: var(--tv-muted) !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: var(--tv-text)  !important; font-size: 20px !important; }

/* ── Dataframes / tabla de resultados ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--tv-border2) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #131722 !important;
}
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] > div > div,
[data-testid="stDataFrame"] canvas,
[data-testid="stDataFrame"] iframe,
[data-testid="stDataFrame"] [class*="stDataFrame"],
[data-testid="stDataFrame"] [class*="dataframe"],
[data-testid="stDataFrame"] [data-testid="StyledDataFrameDataCell"],
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] thead,
[data-testid="stDataFrame"] thead tr,
[data-testid="stDataFrame"] thead th {
    background: #131722 !important;
    background-color: #131722 !important;
    color: #d1d4dc !important;
}
/* Cabecera de la tabla */
[data-testid="stDataFrame"] [class*="header"],
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="columnheader"] * {
    background: #1e222d !important;
    background-color: #1e222d !important;
    color: #d1d4dc !important;
}
/* Filas vacías */
[data-testid="stDataFrame"] [role="row"],
[data-testid="stDataFrame"] [role="gridcell"] {
    background: #131722 !important;
}
/* Toolbar de la tabla (botones descargar, etc.) */
[data-testid="stDataFrameToolbar"] {
    background: var(--tv-panel2) !important;
    border-bottom: 1px solid var(--tv-border) !important;
}
[data-testid="stDataFrameToolbar"] button {
    background: transparent !important;
    color: var(--tv-muted) !important;
    border: none !important;
}
[data-testid="stDataFrameToolbar"] button:hover {
    background: var(--tv-border2) !important;
    color: var(--tv-text) !important;
}

/* ── Alertas / mensajes ── */
[data-testid="stAlert"],
.stAlert {
    border-radius: 6px !important;
    border-left: 3px solid !important;
}
.stSuccess, [data-testid="stAlert"].success {
    background: #0a1f14 !important; border-color: var(--tv-green) !important; color: #26a69a !important;
}
.stInfo, [data-testid="stAlert"].info {
    background: #0a1228 !important; border-color: var(--tv-blue) !important; color: #6b8fff !important;
}
.stWarning, [data-testid="stAlert"].warning {
    background: #1e1400 !important; border-color: var(--tv-yellow) !important; color: var(--tv-yellow) !important;
}
.stError, [data-testid="stAlert"].error {
    background: #1e0808 !important; border-color: var(--tv-red) !important; color: #f87171 !important;
}
/* success/info contienen texto oscuro por defecto — forzar claro */
.stSuccess *, .stInfo *, .stWarning *, .stError * { color: inherit !important; }

/* ── Caption / subtextos ── */
.stCaption, small, [data-testid="stCaptionContainer"] {
    color: var(--tv-muted) !important; font-size: 12px !important;
}

/* ── Dividers / hr ── */
hr { border-color: var(--tv-border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--tv-bg); }
::-webkit-scrollbar-thumb { background: var(--tv-border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--tv-subtle); }

/* ── Sliders ── */
.stSlider [data-baseweb="slider"] [role="slider"] { background: var(--tv-blue) !important; }
[data-testid="stSlider"] [data-baseweb="slider"] { background: var(--tv-border2) !important; }
</style>
""", unsafe_allow_html=True)


# ── LOGIN ─────────────────────────────────────────────────────────────────────
def _pantalla_login():
    st.markdown("""
    <style>
    .login-box {
        max-width: 420px; margin: 60px auto; padding: 36px 32px;
        background: #1e222d; border: 1px solid #2a2e39; border-radius: 12px;
    }
    .login-box h2 { color: #d1d4dc; font-size: 20px; margin-bottom: 4px; }
    .login-box p  { color: #787b86; font-size: 13px; margin-bottom: 20px; }
    /* Ocultar el botón de visibilidad nativo del navegador en inputs de contraseña */
    input[type="password"]::-ms-reveal,
    input[type="password"]::-ms-clear,
    input[type="password"]::-webkit-contacts-auto-fill-button,
    input[type="password"]::-webkit-credentials-auto-fill-button { display: none !important; }
    /* Ocultar el icono de visibilidad que Streamlit añade */
    [data-testid="stTextInput"] [data-testid="textInputRootElement"] + div { display: none !important; }
    button[aria-label="visibility"],
    button[title="visibility"],
    button[aria-label="Show password"],
    button[title="Show password"] { display: none !important; }
    </style>
    <div class='login-box'>
      <h2>🎯 Momento Dulce Scanner</h2>
      <p>Acceso privado — introduce tus credenciales</p>
    </div>
    """, unsafe_allow_html=True)

    modo = st.radio("", ["🔑 Entrar", "📝 Registrarse"], horizontal=True, label_visibility="collapsed")

    if modo == "🔑 Entrar":
        with st.form("login_form"):
            u = st.text_input("Email / usuario")
            p = st.text_input("Contraseña", type="password")
            ok = st.form_submit_button("Entrar →", type="primary", use_container_width=True)
        if ok:
            datos = check_login(u, p)
            if datos:
                st.session_state["usuario_logado"] = datos
                st.rerun()
            elif cuenta_pendiente(u, p):
                st.warning("Tu cuenta está pendiente de activación. Contacta con el administrador.")
            else:
                st.error("Usuario o contraseña incorrectos.")

    else:  # Registrarse
        with st.form("reg_form"):
            ru = st.text_input("Email")
            rn = st.text_input("Nombre")
            rp = st.text_input("Contraseña (mín. 4 caracteres)", type="password")
            rp2 = st.text_input("Repite contraseña", type="password")
            ok = st.form_submit_button("Crear cuenta", type="primary", use_container_width=True)
        if ok:
            u2 = (ru or "").strip().lower()
            if not u2 or not rp:
                st.error("Rellena todos los campos.")
            elif rp != rp2:
                st.error("Las contraseñas no coinciden.")
            elif len(rp) < 4:
                st.error("La contraseña debe tener al menos 4 caracteres.")
            else:
                uu = load_users()
                if u2 in {str(k).strip().lower() for k in uu}:
                    st.error("Ese usuario ya existe.")
                else:
                    from datetime import datetime
                    uu[u2] = {"password": hash_pw(rp), "nombre": rn.strip() or u2,
                              "rol": "usuario", "activo": False,
                              "creado": f"{datetime.now():%d/%m/%Y %H:%M}"}
                    if "@" in u2:
                        uu[u2]["email"] = u2
                    save_users(uu)
                    st.success("✅ Cuenta creada. Espera a que el administrador la active.")

if "usuario_logado" not in st.session_state:
    _pantalla_login()
    st.stop()

_usuario = st.session_state["usuario_logado"]
_es_admin = _usuario.get("rol") == "admin"

# ── Idioma ────────────────────────────────────────────────────────────────────
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"

ES = st.session_state.idioma == "es"

# ── Admin ─────────────────────────────────────────────────────────────────────
_admin = True

@st.cache_data(show_spinner=False)
def traducir(texto: str, destino: str) -> str:
    """Traduce texto usando Google Translate con caché para no repetir llamadas."""
    if not texto or len(texto) < 10:
        return texto
    try:
        # Google Translate tiene límite de ~5000 chars por llamada
        if len(texto) > 4900:
            texto = texto[:4900]
        return GoogleTranslator(source="auto", target=destino).translate(texto)
    except Exception:
        return texto

# Diccionario de textos UI ES / EN
T = {
    "titulo":         "🎯 Momento Dulce Scanner"              if ES else "🎯 Momento Dulce Scanner",
    "subtitulo":      "Detecta acciones que cumplen la estrategia: **Estocástico + Volumen + S/R + Momentum**"
                      if ES else "Detects stocks matching the strategy: **Stochastic + Volume + S/R + Momentum**",
    "perfil_label":   "Selecciona la sensibilidad:"           if ES else "Select sensitivity:",
    "mercados":       "🌍 Selecciona mercados"                if ES else "🌍 Select markets",
    "custom":         "Añadir tickers personalizados"          if ES else "Add custom tickers",
    "custom_input":   "Tickers extra (separados por coma):"   if ES else "Extra tickers (comma separated):",
    "filtro":         "🔎 Filtro de resultados"               if ES else "🔎 Filter results",
    "filtro_ops":     ["Todos", "✅ Solo BUY (Momento Dulce)", "🔴 Solo SELL", "⚠️ Parciales (≥3 condiciones)"]
                      if ES else ["All", "✅ BUY only (Sweet Spot)", "🔴 SELL only", "⚠️ Partial (≥3 conditions)"],
    "escanear":       "🔍 Escanear ahora"                     if ES else "🔍 Scan now",
    "analizando":     "Analizando"                            if ES else "Analysing",
    "resultados":     "📊 Resultados"                         if ES else "📊 Results",
    "buy_titulo":     "acción(es) en MOMENTO DULCE"           if ES else "stock(s) in SWEET SPOT",
    "tec_titulo":     "#### 📝 Análisis técnico"              if ES else "#### 📝 Technical analysis",
    "fund_titulo":    "#### 🏦 Análisis fundamental"          if ES else "#### 🏦 Fundamental analysis",
    "empresa_label":  "¿Qué hace esta empresa?"               if ES else "What does this company do?",
    "pine_btn":       "📋 Ver Pine Script — Listo para TradingView"
                      if ES else "📋 View Pine Script — Ready for TradingView",
    "pine_caption":   "Copia el código → TradingView → Pine Editor → Nuevo script → Pega → Añadir al gráfico"
                      if ES else "Copy the code → TradingView → Pine Editor → New script → Paste → Add to chart",
    "gatillo_titulo": "💥 GATILLO DE ACTIVACIÓN"              if ES else "💥 ACTIVATION TRIGGER",
    "gatillo_sup":    "Entrada cuando precio supere:"         if ES else "Entry when price breaks:",
    "gatillo_max":    "(máximo vela anterior)"                if ES else "(previous candle high)",
    "informe_fecha":  "Informe generado:"                     if ES else "Report generated:",
    "traducir_btn":   "🇬🇧 Traducir a inglés"                 if ES else "🇪🇸 Traducir a español",
}

# ── Tickers por mercado ───────────────────────────────────────────────────────

# ── Inversores Value — carteras 13F más recientes (Q1 2026) ─────────────────

# Warren Buffett — Berkshire Hathaway (top holdings)
BUFFETT = [
    "AAPL","BAC","AXP","KO","CVX","OXY","KHC","MCO","DVA","CB",
    "USB","JPM","SIRI","VZ","GM","ATVI","LPX","PNC","AON","ALLY",
    "V","MA","NUE","BK","CE","UPS","LSXMK","CHTR","BYD",
]

# Ray Dalio — Bridgewater Associates (top holdings)
DALIO = [
    "SPY","GLD","EEM","VWO","IEMG","IVV","IAU","AGG","LQD","TLT",
    "WMT","COST","PG","JNJ","AMZN","GOOGL","MSFT","META","JPM","BAC",
    "XOM","CVX","HD","UNH","V","MA","KO","PEP","MCD","SBUX",
]

# Bill Ackman — Pershing Square (top holdings)
ACKMAN = [
    "HLT","CMG","CP","GOOGL","QSR","HHH","NFLX","NKE","UNH","LOW",
    "STZ","FANNIE","FRMO",
]

# Terry Smith — Fundsmith (equivalentes US cotizados en NYSE/NASDAQ)
SMITH = [
    "MSFT","META","AMZN","GOOGL","AAPL","ISRG","IDEXX","MA","V",
    "MKTX","BKNG","DXCM","PAYC","INTU","CPRT","FAST","MNST","SPGI",
    "FTNT","NOW","VEEV","ZTS","SHW","ECL","ROP","ODFL","CTAS","WST",
]

# David Tepper — Appaloosa Management (top holdings)
TEPPER = [
    "META","AMZN","MSFT","GOOGL","NVDA","AAPL","UBER","ABNB","CRM",
    "BABA","JD","PDD","LI","NIO","INTC","GM","F","VALE","RIO",
    "SPY","QQQ","IWM","HYG",
]

NASDAQ100 = [
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG","TSLA","AVGO","COST",
    "NFLX","TMUS","AMD","ADBE","QCOM","PEP","INTC","INTU","CSCO","AMAT",
    "TXN","BKNG","ISRG","AMGN","MU","HON","VRTX","LRCX","PANW","REGN",
    "KLAC","SNPS","CDNS","ADI","CRWD","MRVL","ASML","KDP","ABNB","GILD",
    "MAR","PYPL","MDLZ","CTAS","ORLY","PCAR","ROST","DXCM","MNST","AEP",
    "PAYX","MCHP","IDXX","ODFL","CPRT","FAST","GEHC","KHC","VRSK","CCEP",
    "EA","BIIB","ON","CTSH","GFS","DDOG","FANG","EXC","XEL","CMCSA",
    "TTWO","DLTR","MRNA","ILMN","ZS","SIRI","SBUX","TEAM","ANSS","NXPI",
]
SP500_SAMPLE = [
    "JPM","BAC","WFC","GS","MS","BLK","C","AXP","USB","PNC",
    "JNJ","UNH","PFE","ABT","MRK","LLY","BMY","AMGN","GILD","CVS",
    "XOM","CVX","COP","EOG","SLB","PSX","VLO","MPC","OXY","HAL",
    "CAT","DE","GE","HON","MMM","RTX","LMT","BA","NOC","GD",
    "WMT","TGT","COST","HD","LOW","MCD","SBUX","NKE","TJX","ROST",
    "DIS","CMCSA","NFLX","T","VZ","TMUS","CHTR","FOX","PARA","WBD",
    "V","MA","PYPL","AXP","COF","DFS","SYF","BK","STT","SCHW",
    "NEE","DUK","SO","D","AEP","EXC","XEL","SRE","PCG","ED",
]
IBEX35 = [
    "SAN.MC","BBVA.MC","ITX.MC","IBE.MC","REP.MC","TEF.MC","ACS.MC",
    "AENA.MC","ANA.MC","ACX.MC","CLNX.MC","COL.MC","ELE.MC","ENG.MC",
    "FER.MC","GRF.MC","IAG.MC","IDR.MC","LOG.MC","MAP.MC","MEL.MC",
    "MRL.MC","MTS.MC","NTGY.MC","PHM.MC","RED.MC","ROVI.MC","SAB.MC",
    "SGRE.MC","SLR.MC","SOL.MC","UNI.MC","VIS.MC","VOD.MC","ZOT.MC",
]
CRYPTO = ["BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD","DOGE-USD","AVAX-USD","DOT-USD","LINK-USD","MATIC-USD","LTC-USD","DASH-USD","XMR-USD","NEO-USD"]

# ── EE.UU. Mid Cap (S&P 400) ─────────────────────────────────────────────────
SP400_MIDCAP = [
    "FN","CASY","EPAM","TMHC","SM","SAIA","RMBS","LNTH","BXMT","OLED",
    "BRKR","CRC","NUVL","GLPI","HRI","CIEN","POWI","BJ","MTZ","MTDR",
    "RLI","MUSA","BCO","ITGR","MMSI","WTS","SPSC","PRGO","ICFI","LCII",
    "GATX","FHI","MGEE","NWBI","TKO","CNO","OGS","AGIO","AEIS","HLNE",
    "KNTK","GMED","WD","MGRC","LMAT","CWT","FRSH","AWR","PBH","GOLF",
]

# ── EE.UU. Small Cap (Russell 2000 muestra) ──────────────────────────────────
RUSSELL2000_SAMPLE = [
    # Small caps NASDAQ/NYSE activos — verificados junio 2025
    "CLOV","ASTS","IONQ","BYRN","ACHR","LUNR","LITB","MNKD","HIMS","OPEN",
    "BIRD","GENI","SEAT","XPOF","NVAX","RLAY","CURV","MVST","BLNK","PRLD",
    "CLBT","JMIA","PAYO","RPAY","LASR","SPCE","PHAT","TPVG","FLNC","ACVA",
    "ARLO","HALO","CPRX","KIDS","CTKB","OCGN","ADMA","ESTA","BTBT","COUR",
    # Reemplazos (BIGC/ATIP/PNTM/LAZY/GOEV/CMAX/RGF/MNTV/CRKN — delisted/OTC)
    "AGIO","TMDX","MGNI","ITRI","PRCT","FORM","NARI","SWAV","ACLS",
]

# ── Europa ────────────────────────────────────────────────────────────────────
DAX40 = [
    "SAP.DE","SIE.DE","ALV.DE","DTE.DE","MUV2.DE","BAS.DE","BAYN.DE","MBG.DE",
    "BMW.DE","VOW3.DE","ADS.DE","DBK.DE","RWE.DE","EON.DE","HEN3.DE","EOAN.DE",
    "DHL.DE","MTX.DE","ZAL.DE","1COV.DE","QGEN.DE","DHER.DE","FRE.DE","IFX.DE",
    "LIN.DE","MRK.DE","PAH3.DE","PUM.DE","SHL.DE","VNA.DE",
    "AIR.DE","BEI.DE","CON.DE","DTG.DE","EVK.DE","FME.DE","HNR1.DE","LEG.DE",
    "MAN.DE","SDF.DE",
]
CAC40 = [
    "MC.PA","OR.PA","TTE.PA","SAN.PA","AIR.PA","RI.PA","BNP.PA","CS.PA",
    "DG.PA","EL.PA","EN.PA","ENGI.PA","ERF.PA","GLE.PA","HO.PA","KER.PA",
    "LR.PA","ML.PA","MT.PA","ORA.PA","PUB.PA","RMS.PA","SAF.PA","SGO.PA",
    "STLA.PA","STM.PA","SU.PA","TEP.PA","URW.PA","VIE.PA",
    "ACA.PA","ATO.PA","BN.PA","CA.PA","CAP.PA","DSY.PA","FP.PA","FR.PA",
    "HDP.PA","SW.PA",
]
FTSE100 = [
    "SHEL.L","AZN.L","HSBA.L","ULVR.L","BP.L","GSK.L","RIO.L","BATS.L",
    "VOD.L","DGE.L","LSEG.L","NG.L","LLOY.L","REL.L","CPG.L","EXPN.L",
    "IMB.L","MNG.L","NWG.L","PSON.L","PRU.L","RKT.L","SGRO.L","SMT.L",
    "TSCO.L","WEIR.L","WTB.L","BHP.L","CCH.L","CNA.L",
    "AAL.L","ABF.L","ADM.L","AHT.L","ANTO.L","AUTO.L","AVV.L","BA.L",
    "BAB.L","BARC.L","BDEV.L","BKG.L","BLND.L","BME.L","BNZL.L","BOO.L",
    "BRBY.L","BT.A.L","CLLN.L","CNXA.L","COB.L","CRH.L","CRH.L","CRDA.L",
    "DCC.L","DLG.L","EVR.L","FCIT.L","FERG.L","FLTR.L","GFS.L","HIK.L",
    "HLMA.L","HMSO.L","HOC.L","HSBA.L","HLN.L","ITRK.L","JD.L","JET.L",
    "KGF.L","LAND.L","LGEN.L","MKS.L","MNDI.L","MRO.L","MXCT.L","NXT.L",
    "OCDO.L","PSH.L","PSN.L","RB.L","RDSA.L","RS1.L","SDR.L","SKG.L",
    "SMDS.L","SMIN.L","SMT.L","SN.L","SPX.L","SSE.L","STAN.L","SVT.L",
    "TATE.L","TUI.L","WEIR.L","WPP.L","WTB.L",
]
EUROSTOXX50 = [
    "ASML.AS","INGA.AS","PHIA.AS","AD.AS","HEIA.AS",
    "AIR.PA","BNP.PA","OR.PA","SAN.PA","TTE.PA","MC.PA","SU.PA",
    "SAP.DE","SIE.DE","ALV.DE","MUV2.DE","BAS.DE","DTE.DE","BMW.DE","MBG.DE",
    "ENEL.MI","ISP.MI","UCG.MI","ENI.MI","G.MI",
    "SAN.MC","BBVA.MC","IBE.MC","ITX.MC","REP.MC",
    "NOVN.SW","ROG.SW","NESN.SW","ABI.BR","CS.PA","ADS.DE",
]
MIB40 = [
    "ENEL.MI","ISP.MI","UCG.MI","ENI.MI","G.MI","STM.MI","TIT.MI","RACE.MI",
    "CPR.MI","AMP.MI","BAMI.MI","BZU.MI","CNHI.MI","DIA.MI","EXO.MI",
    "FCA.MI","HER.MI","INW.MI","LDO.MI","MB.MI","MONC.MI","PIRC.MI",
    "PRY.MI","REC.MI","SRG.MI","TEN.MI","UNI.MI","BRIT.MI","BMED.MI",
    "BGN.MI","A2A.MI","AZMT.MI","ERG.MI","FNM.MI","INWT.MI","MARR.MI",
]
AEX25 = [
    "ASML.AS","INGA.AS","PHIA.AS","AD.AS","HEIA.AS","REN.AS","AKZA.AS",
    "NN.AS","RAND.AS","UNA.AS","WKL.AS","BESI.AS","IMCD.AS","KPN.AS","MT.AS",
    "ABN.AS","ADYEN.AS","AGN.AS","DSFIR.AS","EXOR.AS","LIGHT.AS","SHELL.AS",
]
SMI20 = [
    "NOVN.SW","ROG.SW","NESN.SW","ABBN.SW","CFR.SW","GIVN.SW","LONN.SW",
    "SREN.SW","SCMN.SW","SIKA.SW","UHR.SW","ZURN.SW","ALC.SW","BAER.SW",
    "CSGN.SW","GEBN.SW","HOLN.SW","KREN.SW","PGHN.SW","STMN.SW",
]
OMX30 = [
    "ERIC-B.ST","VOLV-B.ST","SEB-A.ST","SHB-A.ST","SWED-A.ST","ATCO-A.ST",
    "ASSA-B.ST","SAND.ST","SKF-B.ST","ABB.ST","AZN.ST","HEXA-B.ST",
    "INVE-B.ST","LUND-B.ST","NDA-SE.ST","ALFA.ST","ALIV-SDB.ST","BOLS.ST",
    "BOL.ST","CAST.ST","ELUX-B.ST","EVO.ST","GETI-B.ST","HM-B.ST",
    "HUFV-A.ST","INDU-A.ST","LATO-B.ST","MTG-B.ST","NIBE-B.ST","SAAB-B.ST",
]
PSI20 = [
    "EDP.LS","GALP.LS","BCP.LS","NOS.LS","JMT.LS","SON.LS","ALTR.LS",
    "COR.LS","CTT.LS","EGL.LS","EDPR.LS","ESON.LS","GPA.LS","IPMA.LS",
    "MCP.LS","MOTA.LS","NVG.LS","RAM.LS","SLBEN.LS","VIL.LS",
]
BEL20 = [
    "ABI.BR","UCB.BR","KBC.BR","SOLB.BR","ACKB.BR","AGS.BR","APAM.BR",
    "ARGX.BR","BAR.BR","BPOST.BR","COLR.BR","COIL.BR","DPAM.BR","ETL.BR",
    "GBLB.BR","GBL.BR","GLPG.BR","ING.BR","LOTB.BR","MELE.BR",
]
IBEX_MEDIUM = [
    "AMS.MC","APM.MC","BME.MC","CAF.MC","CIE.MC","DOM.MC","DIA.MC",
    "EZE.MC","FAES.MC","FCC.MC","FDRK.MC","FDR.MC","GAM.MC","GLJ.MC",
    "HOP.MC","LAR.MC","LGT.MC","MCM.MC","MDF.MC","ORYC.MC","PRIM.MC",
    "PSG.MC","R4.MC","RBTS.MC","RLIA.MC","SECO.MC","SECU.MC","TLGO.MC",
    "TRG.MC","UFES.MC","VID.MC","ZRPV.MC",
]

# ── Asia-Pacífico ─────────────────────────────────────────────────────────────
NIKKEI_SAMPLE = [
    "7203.T","6758.T","9984.T","8306.T","6861.T","7974.T","4519.T","9432.T",
    "6954.T","8035.T","4063.T","8316.T","4502.T","6367.T","8766.T","9433.T",
    "7267.T","6501.T","6702.T","5108.T","4568.T","2914.T","8411.T","7751.T",
]
HANG_SENG_SAMPLE = [
    "0700.HK","0939.HK","1299.HK","0388.HK","2318.HK","1398.HK","3690.HK",
    "9988.HK","0883.HK","2628.HK","0005.HK","0016.HK","0001.HK","0011.HK",
    "0027.HK","0066.HK","0175.HK","0267.HK","0386.HK","0688.HK",
]
ASX200_SAMPLE = [
    "BHP.AX","CBA.AX","CSL.AX","NAB.AX","ANZ.AX","WBC.AX","WES.AX","MQG.AX",
    "RIO.AX","TLS.AX","WOW.AX","FMG.AX","GMG.AX","REA.AX","ALL.AX","IAG.AX",
    "QBE.AX","STO.AX","TCL.AX","WDS.AX",
]
KOSPI_SAMPLE = [
    "005930.KS","000660.KS","035420.KS","051910.KS","006400.KS","028260.KS",
    "105560.KS","055550.KS","000270.KS","066570.KS","012330.KS","032830.KS",
]
BSE_SAMPLE = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","HINDUNILVR.NS",
    "SBIN.NS","BHARTIARTL.NS","ITC.NS","KOTAKBANK.NS","LT.NS","AXISBANK.NS",
    "ASIANPAINT.NS","MARUTI.NS","WIPRO.NS","SUNPHARMA.NS","ULTRACEMCO.NS",
    "TITAN.NS","BAJFINANCE.NS","NESTLEIND.NS",
]

# ── América ───────────────────────────────────────────────────────────────────
TSX_SAMPLE = [
    "RY.TO","TD.TO","BNS.TO","BMO.TO","CM.TO","ENB.TO","CNQ.TO","SU.TO",
    "TRP.TO","CP.TO","CNR.TO","BCE.TO","T.TO","MFC.TO","SLF.TO","WPM.TO",
    "ABX.TO","AEM.TO","ATD.TO","L.TO",
]
BOVESPA_SAMPLE = [
    "PETR4.SA","VALE3.SA","ITUB4.SA","BBDC4.SA","ABEV3.SA","WEGE3.SA",
    "RENT3.SA","BBAS3.SA","JBSS3.SA","SUZB3.SA","ELET3.SA","RADL3.SA",
    "MGLU3.SA","LREN3.SA","HAPV3.SA","RAIL3.SA","TOT3.SA","VBBR3.SA",
]
IPC_SAMPLE = [
    "WALMEX.MX","FEMSA.MX","AMX.MX","TLEVISA.MX","BIMBOA.MX","CHDRAUI.MX",
    "GFINBURO.MX","GFNORTEO.MX","SORIANA.MX","CEMEX.MX","ALFA.MX","ALPEKA.MX",
]

# ── Materias primas — solo ETFs con precio continuo (sin futuros =F) ─────────
# Los futuros tienen rolls de contrato que rompen Estocástico/S&R/Fibonacci.
# Usamos ETFs de réplica con precio continuo y liquidez alta.
COMMODITIES = [
    # Metales preciosos (spot equivalente)
    "GC=F",  # XAUUSD — Oro
    "SI=F",  # XAGUSD — Plata
    "PL=F",  # XPTUSD — Platino
    "PA=F",  # XPDUSD — Paladio
    # Energía (crudo)
    "CL=F",  # USOIL  — WTI Crude Oil
    "BZ=F",  # UKOIL  — Brent Crude Oil
    # Agrícolas
    "CC=F",  # COCOA  — Cacao
    "KC=F",  # COFFEE — Café
    "ZS=F",  # SOYBEAN — Soja
    "ZW=F",  # WHEAT  — Trigo
]

# ── DARWINEX — cuenta fondeada (largo + corto) ──────────────────────────────
DARWINEX = [
    # Índices (10) — SP500, NDQ, WS30, GDAXI, SPA35, UK100, STOXX50E, NI225, AUS200, FCHI40
    "^GSPC", "^NDX", "^DJI", "^GDAXI", "^IBEX",
    "^FTSE", "^STOXX50E", "^N225", "^AXJO", "^FCHI",
    # Materias primas (4) — XAUUSD, XAGUSD, XTIUSD, XNGUSD
    "GC=F", "SI=F", "CL=F", "NG=F",
    # Forex (38 pares)
    "EURUSD=X", "GBPUSD=X", "AUDUSD=X", "NZDUSD=X", "USDCAD=X",
    "USDCHF=X", "USDJPY=X", "USDSEK=X", "USDNOK=X", "USDSGD=X",
    "USDMXN=X", "EURGBP=X", "EURCHF=X", "EURJPY=X", "EURCAD=X",
    "EURAUD=X", "EURNZD=X", "EURNOK=X", "EURSEK=X", "EURMXN=X",
    "GBPJPY=X", "GBPCHF=X", "GBPCAD=X", "GBPAUD=X", "GBPNZD=X",
    "GBPNOK=X", "GBPSEK=X", "GBPMXN=X", "AUDJPY=X", "AUDCAD=X",
    "AUDNZD=X", "AUDCHF=X", "NZDJPY=X", "NZDCHF=X", "NZDCAD=X",
    "CADCHF=X", "CADJPY=X", "CHFJPY=X",
]

# ── FTMO — cuenta fondeada (largo + corto) ──────────────────────────────────
FTMO = [
    # Divisas (10)
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X",
    "USDCAD=X", "NZDUSD=X", "EURGBP=X", "GBPJPY=X", "AUDJPY=X",
    # Índices CFD (10)
    "^GSPC", "^NDX", "^DJI", "^RUT",
    "^GDAXI", "^STOXX50E", "^FTSE", "^N225", "^HSI", "^AXJO",
    # Criptomonedas (10)
    "BTC-USD", "ETH-USD", "XRP-USD", "ADA-USD", "DOGE-USD",
    "DOT-USD", "LTC-USD", "DASH-USD", "XMR-USD", "NEO-USD",
    # Materias primas (10)
    "GC=F", "SI=F", "PL=F", "PA=F",   # Metales preciosos
    "CL=F", "BZ=F",                    # Crudo WTI / Brent
    "CC=F", "KC=F", "ZS=F", "ZW=F",   # Agrícolas
]

# ── ORION FUNDED — cuenta fondeada (largo + corto) ──────────────────────────
ORION_FUNDED = [
    # Forex (10 principales)
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X",
    "USDCAD=X", "NZDUSD=X", "EURGBP=X", "GBPJPY=X", "AUDJPY=X",
    "EURJPY=X", "GBPCHF=X", "EURCHF=X", "EURCAD=X", "GBPCAD=X",
    "AUDCAD=X", "NZDCHF=X", "CADCHF=X", "CADJPY=X", "CHFJPY=X",
    # Índices CFD
    "^GSPC", "^NDX", "^DJI", "^RUT",
    "^GDAXI", "^STOXX50E", "^FTSE", "^N225", "^HSI", "^AXJO",
    # Metales y Energía
    "GC=F", "SI=F", "PL=F",   # Oro, Plata, Platino
    "CL=F", "BZ=F", "NG=F",   # WTI, Brent, Gas Natural
    # Criptomonedas
    "BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "ADA-USD",
    "SOL-USD", "DOGE-USD", "DOT-USD", "BNB-USD", "AVAX-USD",
]

# ── Futuros principales (índices, bonos, energía, metales) ───────────────────
INDICES_CFD = [
    "^GSPC",     # US500   — S&P 500
    "^NDX",      # US100   — Nasdaq 100
    "^DJI",      # US30    — Dow Jones
    "^RUT",      # US2000  — Russell 2000
    "^GDAXI",    # GER40   — DAX 40
    "^STOXX50E", # EU50    — Euro Stoxx 50
    "^FTSE",     # UK100   — FTSE 100
    "^N225",     # JP225   — Nikkei 225
    "^HSI",      # HK50    — Hang Seng
    "^AXJO",     # AUS200  — ASX 200
]

# ── Mini Futuros (trading directo) ───────────────────────────────────────────
MINI_FUTUROS = [
    "ES=F",   # E-mini S&P 500
    "NQ=F",   # E-mini NASDAQ 100
    "GC=F",   # Oro (Gold Futures)
]

FUTUROS = [
    # Índices EE.UU. — contratos estándar
    "ES=F",   # E-mini S&P 500
    "NQ=F",   # E-mini NASDAQ 100
    "RTY=F",  # E-mini Russell 2000
    "YM=F",   # E-mini Dow Jones
    "EMD=F",  # E-mini S&P MidCap 400
    # Micro contratos EE.UU. (tamaño x10 menor, más accesibles)
    "MES=F",  # Micro E-mini S&P 500
    "MNQ=F",  # Micro E-mini NASDAQ 100
    "M2K=F",  # Micro E-mini Russell 2000
    "MYM=F",  # Micro E-mini Dow Jones
    # Índices Europa / Asia (índices reales, sin futuro en Yahoo)
    "^GDAXI", # DAX 40 (Alemania)
    "^STOXX50E", # Euro Stoxx 50
    "^FTSE",  # FTSE 100 (UK)
    "^N225",  # Nikkei 225 (Japón)
    # Bonos
    "ZN=F",   # T-Note 10 años
    "ZB=F",   # T-Bond 30 años
    # Energía
    "CL=F",   # WTI Crude Oil
    "NG=F",   # Gas Natural
    # Metales
    "GC=F",   # Oro
    "SI=F",   # Plata
]

# ── Divisas principales (Forex) ──────────────────────────────────────────────
FOREX = [
    "EURUSD=X",  # Euro / Dólar
    "GBPUSD=X",  # Libra / Dólar
    "USDJPY=X",  # Dólar / Yen
    "USDCHF=X",  # Dólar / Franco suizo
    "AUDUSD=X",  # Dólar australiano / Dólar
    "USDCAD=X",  # Dólar / Dólar canadiense
    "NZDUSD=X",  # Dólar neozelandés / Dólar
    "EURGBP=X",  # Euro / Libra
    "EURJPY=X",  # Euro / Yen
    "GBPJPY=X",  # Libra / Yen
    "USDMXN=X",  # Dólar / Peso mexicano
    "USDBRL=X",  # Dólar / Real brasileño
    "EURCHF=X",  # Euro / Franco suizo
    "GBPCHF=X",  # Libra / Franco suizo
    "AUDJPY=X",  # Dólar australiano / Yen
]

MERCADOS = {
    # ── Cuentas fondeadas ───────────────────────────────
    "🏦 FTMO":              FTMO,
    "🟠 DARWINEX":          DARWINEX,
    "🔵 ORION FUNDED":      ORION_FUNDED,
    # ── EE.UU. ──────────────────────────────────────────
    # ── Mini Futuros ─────────────────────────────────────
    "📉 Mini SP500":        MINI_FUTUROS[:1],
    "📉 Mini NASDAQ":       MINI_FUTUROS[1:2],
    "🥇 Oro":               MINI_FUTUROS[2:],
    # ── Inversores Value ────────────────────────────────
    "🧙 Buffett":           BUFFETT,
    "🌊 Dalio":             DALIO,
    "🎯 Ackman":            ACKMAN,
    "🔬 Terry Smith":       SMITH,
    "⚡ Tepper":            TEPPER,
    # ── EE.UU. ──────────────────────────────────────────
    "🇺🇸 NASDAQ 100":       NASDAQ100,
    "🇺🇸 S&P 500":          SP500_SAMPLE,
    "🇺🇸 400 MidCap":   SP400_MIDCAP,
    "🇺🇸 Russell 2000":     RUSSELL2000_SAMPLE,
    # ── Europa ──────────────────────────────────────────
    "🇪🇸 IBEX 35":          IBEX35,
    "🇪🇸 IBEX Medium":      IBEX_MEDIUM,
    "🇩🇪 DAX 40":           DAX40,
    "🇫🇷 CAC 40":           CAC40,
    "🇬🇧 FTSE 100":         FTSE100,
    "🇪🇺 EuroStoxx 50":     EUROSTOXX50,
    "🇮🇹 MIB 40":           MIB40,
    "🇳🇱 AEX 25":           AEX25,
    "🇨🇭 SMI 20":           SMI20,
    "🇸🇪 OMX 30":           OMX30,
    "🇵🇹 PSI 20":           PSI20,
    "🇧🇪 BEL 20":           BEL20,
    # ── Asia-Pacífico ───────────────────────────────────
    "🇯🇵 Nikkei 225":       NIKKEI_SAMPLE,
    "🇭🇰 Hang Seng":        HANG_SENG_SAMPLE,
    "🇦🇺 ASX 200":          ASX200_SAMPLE,
    "🇰🇷 KOSPI":            KOSPI_SAMPLE,
    "🇮🇳 BSE Sensex":       BSE_SAMPLE,
    # ── América ─────────────────────────────────────────
    "🇨🇦 TSX":              TSX_SAMPLE,
    "🇧🇷 Bovespa":          BOVESPA_SAMPLE,
    "🇲🇽 IPC México":       IPC_SAMPLE,
    # ── Otros ───────────────────────────────────────────
    "🪙 Crypto":            CRYPTO,
    "🛢️ Materias Primas":   COMMODITIES,
    # ── Divisas ─────────────────────────────────────────
    "💱 Divisas":           FOREX,
    # ── Índices CFD ─────────────────────────────────────
    "📈 Índices CFD":       INDICES_CFD,
    # ── Futuros ─────────────────────────────────────────
    "📊 Futuros":           FUTUROS,
}

# ── Perfiles de parámetros ────────────────────────────────────────────────────
#
#  CONSERVADOR  → Fiel al Pine Script original. Las 5 condiciones deben cumplirse
#                 en la misma barra. Volumen y momentum exigentes.
#
#  MODERADO     → Amplía el umbral de sobreventa, tolera volumen ligeramente bajo
#                 y acepta cruce en las últimas 2 barras.
#
#  AGRESIVO     → Detecta el inicio de giro antes de que se consolide. K puede
#                 estar hasta 40, volumen y ROC son orientativos, cruce en 3 barras.

PERFILES = {
    "🛡️ Conservador": {
        "desc": "Fiel al Pine Script original. Las 5 condiciones exactas. Pocas señales pero de alta calidad.",
        "stoch_k": 14, "stoch_d": 3,
        "vol_period": 20, "vol_mult": 1.0,
        "sr_period": 50,
        "roc_period": 10, "roc_min": 0.0,
        "oversold": 20, "overbought": 80,
        "cruce_ventana": 1,
    },
    "⚖️ Moderado": {
        "desc": "Amplía el umbral de sobreventa a 30 y acepta cruce en las últimas 2 barras. Más señales sin perder contexto.",
        "stoch_k": 14, "stoch_d": 3,
        "vol_period": 20, "vol_mult": 0.85,
        "sr_period": 35,
        "roc_period": 10, "roc_min": -2.0,
        "oversold": 30, "overbought": 75,
        "cruce_ventana": 2,
    },
    "🔥 Agresivo": {
        "desc": "Detecta giros tempranos. K hasta 40, volumen orientativo, cruce en las últimas 3 barras. Más señales, más ruido.",
        "stoch_k": 14, "stoch_d": 3,
        "vol_period": 20, "vol_mult": 0.70,
        "sr_period": 20,
        "roc_period": 10, "roc_min": -5.0,
        "oversold": 40, "overbought": 70,
        "cruce_ventana": 3,
    },
}

# ── UI ────────────────────────────────────────────────────────────────────────
col_title, col_lang, col_user = st.columns([7, 1, 2])
col_title.title(T["titulo"])
col_title.markdown(T["subtitulo"])
if col_lang.button(T["traducir_btn"], width="stretch"):
    st.session_state.idioma = "en" if ES else "es"
    st.rerun()

with col_user:
    _nombre_u = _usuario.get("nombre", "Usuario")
    _rol_u    = _usuario.get("rol", "usuario")
    st.markdown(
        f"<div style='text-align:right;font-size:12px;color:#787b86;margin-top:6px'>"
        f"{'👑 ' if _rol_u=='admin' else '👤 '}{_nombre_u}</div>",
        unsafe_allow_html=True,
    )
    if _es_admin:
        _c1, _c2 = st.columns(2)
        if _c1.button("👥 Usuarios", help="Panel de usuarios", width="stretch", type="primary"):
            st.session_state["_ver_usuarios"] = not st.session_state.get("_ver_usuarios", False)
        if _c2.button("🚪 Salir", help="Cerrar sesión", width="stretch"):
            del st.session_state["usuario_logado"]
            st.rerun()
    else:
        if st.button("🚪 Salir", help="Cerrar sesión", width="stretch"):
            del st.session_state["usuario_logado"]
            st.rerun()

# ── Panel de usuarios (solo admin) — siempre visible arriba ──────────────────
if _es_admin and st.session_state.get("_ver_usuarios"):
    st.markdown("### 👥 Panel de Usuarios")
    mod_usuarios.render()
    st.divider()

# ── Selector de perfil ────────────────────────────────────────────────────────
if "perfil_sel" not in st.session_state:
    st.session_state.perfil_sel = "🛡️ Conservador"

st.markdown(
    "<div style='font-size:11px;font-weight:700;color:var(--tv-muted);text-transform:uppercase;"
    "letter-spacing:1px;margin-bottom:10px'>🎚️ " + ("Perfil de detección" if ES else "Detection profile") + "</div>",
    unsafe_allow_html=True,
)

_PERFIL_META = {
    "🛡️ Conservador": {
        "icon": "🛡️", "label": "Conservador",
        "accent": "#4a9eff", "bg": "linear-gradient(145deg,#0d1f37,#0a172a)",
        "tag": "Alta precisión", "tag2": "Pocas señales",
    },
    "⚖️ Moderado": {
        "icon": "⚖️", "label": "Moderado",
        "accent": "#4aff88", "bg": "linear-gradient(145deg,#0f2a18,#081a10)",
        "tag": "Equilibrado", "tag2": "Señales medias",
    },
    "🔥 Agresivo": {
        "icon": "🔥", "label": "Agresivo",
        "accent": "#ff6644", "bg": "linear-gradient(145deg,#2a1008,#1a0a04)",
        "tag": "Máximas señales", "tag2": "Mayor ruido",
    },
}

_pcols = st.columns(3)
for _pi, (_pkey, _pmeta) in enumerate(_PERFIL_META.items()):
    _sel = st.session_state.perfil_sel == _pkey
    _acc = _pmeta["accent"]
    _bdr = "#ffffff" if _sel else f"{_acc}66"
    _shadow = f"box-shadow:0 0 0 2px {_acc},0 6px 20px {_acc}44" if _sel else f"box-shadow:0 4px 12px {_acc}22"
    _check = f"<div style='position:absolute;top:10px;right:10px;width:20px;height:20px;border-radius:50%;background:{_acc};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:900'>✓</div>" if _sel else ""
    with _pcols[_pi]:
        st.markdown(
            f"<div id='perfil-wrap-{_pi}' style='position:relative'>"
            f"<div style='position:relative;background:{_pmeta['bg']};border:2px solid {_bdr};"
            f"border-radius:14px;padding:20px 16px;cursor:pointer;{_shadow};transition:all .2s'>"
            f"{_check}"
            f"<div style='font-size:28px;margin-bottom:8px'>{_pmeta['icon']}</div>"
            f"<div style='color:#ffffff;font-size:16px;font-weight:800;margin-bottom:6px'>{_pmeta['label']}</div>"
            f"<div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px'>"
            f"<span style='background:{_acc}22;color:{_acc};font-size:10px;font-weight:700;"
            f"padding:2px 8px;border-radius:10px;border:1px solid {_acc}44'>{_pmeta['tag']}</span>"
            f"<span style='background:#ffffff11;color:#ffffff88;font-size:10px;padding:2px 8px;"
            f"border-radius:10px'>{_pmeta['tag2']}</span></div>"
            f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:6px'>"
            f"<div style='background:#ffffff0a;border-radius:8px;padding:8px'>"
            f"<div style='color:#ffffff55;font-size:9px;text-transform:uppercase;letter-spacing:.5px'>Sobreventa K</div>"
            f"<div style='color:{_acc};font-size:15px;font-weight:800'>&lt;{PERFILES[_pkey]['oversold']}</div></div>"
            f"<div style='background:#ffffff0a;border-radius:8px;padding:8px'>"
            f"<div style='color:#ffffff55;font-size:9px;text-transform:uppercase;letter-spacing:.5px'>Vol mín.</div>"
            f"<div style='color:{_acc};font-size:15px;font-weight:800'>{int(PERFILES[_pkey]['vol_mult']*100)}%</div></div>"
            f"</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        if st.button(" ", key=f"pfbtn_{_pi}", width="stretch"):
            st.session_state.perfil_sel = _pkey
            st.rerun()
        st.markdown(
            f"<style>"
            f"div[data-testid='stVerticalBlock']:has(#perfil-wrap-{_pi}) button[kind='secondary']"
            f"{{position:absolute;inset:0;opacity:0;cursor:pointer;border:none;"
            f"border-radius:14px;margin-top:-168px;height:168px}}"
            f"</style>",
            unsafe_allow_html=True,
        )

perfil_nombre = st.session_state.perfil_sel
p = PERFILES[perfil_nombre]

st.markdown(
    f"<div style='background:{_PERFIL_META[perfil_nombre]['bg']};border-left:3px solid "
    f"{_PERFIL_META[perfil_nombre]['accent']};padding:12px 16px;border-radius:8px;"
    f"margin-top:12px;margin-bottom:10px;font-size:13px;color:#d1d4dc;line-height:1.7'>"
    f"<b style='color:#ffffff'>{perfil_nombre}</b> — {p['desc']}<br>"
    f"<span style='color:#aaaaaa'>S/R lookback: <b style='color:#fff'>{p['sr_period']}</b> velas "
    f"· Cruce en últimas <b style='color:#fff'>{p['cruce_ventana']}</b> barra(s) "
    f"· ROC mín: <b style='color:#fff'>{p['roc_min']}%</b></span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Ajuste fino — en cabecera (no sidebar) ───────────────────────────────────
st.markdown(
    "<div style='background:var(--tv-panel);border:1px solid var(--tv-border);border-radius:8px 8px 0 0;"
    "padding:10px 16px;font-size:13px;font-weight:700;color:#d1d4dc'>⚙️ Ajuste fino (opcional)</div>",
    unsafe_allow_html=True,
)
with st.container(border=False):
    _period_opts = {
        "1d":  ["3mo", "6mo", "1y", "2y"],
        "4h":  ["1mo", "3mo", "6mo"],
        "1h":  ["7d", "14d", "1mo"],
        "15m": ["1d", "5d", "7d"],
        "5m":  ["1d", "5d"],
    }
    _hdr_cols = st.columns([1, 1, 1, 1, 1])
    interval = _hdr_cols[0].selectbox("Intervalo de velas", ["1d", "4h", "1h", "15m", "5m"], index=0)
    period   = _hdr_cols[1].selectbox("Período de datos", _period_opts.get(interval, ["6mo"]),
                                       index=min(1, len(_period_opts.get(interval, ["6mo"]))-1))
    st.markdown("<div style='margin-top:10px;font-size:11px;font-weight:700;color:#787b86;"
                "text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px'>📐 Parámetros técnicos</div>",
                unsafe_allow_html=True)
    _p1, _p2, _p3, _p4, _p5 = st.columns(5)
    stoch_k    = _p1.number_input("Estocástico K",    value=p["stoch_k"],    min_value=1)
    stoch_d    = _p2.number_input("Estocástico D",    value=p["stoch_d"],    min_value=1)
    vol_period = _p3.number_input("Volumen MA",       value=p["vol_period"], min_value=1)
    vol_mult   = _p4.number_input("Vol mín (x MA)",   min_value=0.5, max_value=2.0, value=float(p["vol_mult"]), step=0.05)
    sr_period  = _p5.number_input("S/R lookback",     value=p["sr_period"],  min_value=5)
    _p6, _p7, _p8, _p9, _p10 = st.columns(5)
    roc_period = _p6.number_input("ROC período",      value=p["roc_period"], min_value=1)
    roc_min    = _p7.number_input("ROC mín (%)",      value=float(p["roc_min"]), step=0.5)
    oversold   = _p8.number_input("Sobreventa K <",   value=p["oversold"],   min_value=1, max_value=60)
    overbought = _p9.number_input("Sobrecompra K >",  value=p["overbought"], min_value=40, max_value=99)
    cruce_ventana = _p10.number_input("Cruce K>D (barras)", value=p["cruce_ventana"], min_value=1, max_value=5)
    st.markdown("<div style='margin-top:10px;font-size:11px;font-weight:700;color:#787b86;"
                "text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px'>🔘 Filtros activos</div>",
                unsafe_allow_html=True)
    _f1, _f2, _f3, _f4, _f5 = st.columns(5)
    fil_c1 = _f1.checkbox("C1 · K < sobreventa",   value=True, key="filtro_c1")
    fil_c2 = _f2.checkbox("C2 · Cruce K > D",      value=True, key="filtro_c2")
    fil_c3 = _f3.checkbox("C3 · Volumen > Media",   value=True, key="filtro_c3")
    fil_c4 = _f4.checkbox("C4 · ROC positivo",      value=True, key="filtro_c4")
    fil_c5 = _f5.checkbox("C5 · Precio > Soporte",  value=True, key="filtro_c5")

# ── Selección de mercados ─────────────────────────────────────────────────────
st.subheader(T["mercados"])

REGIONES = {
    "📉 Mini Futuros":     ["📉 Mini SP500", "📉 Mini NASDAQ", "🥇 Oro"],
    "🧠 Inversores Value": ["🧙 Buffett", "🌊 Dalio", "🎯 Ackman", "🔬 Terry Smith", "⚡ Tepper"],
    "🇺🇸 EE.UU.":         ["🇺🇸 NASDAQ 100", "🇺🇸 S&P 500", "🇺🇸 400 MidCap", "🇺🇸 Russell 2000"],
    "🇪🇺 Europa":          ["🇪🇸 IBEX 35", "🇪🇸 IBEX Medium", "🇩🇪 DAX 40", "🇫🇷 CAC 40", "🇬🇧 FTSE 100", "🇪🇺 EuroStoxx 50", "🇮🇹 MIB 40", "🇳🇱 AEX 25", "🇨🇭 SMI 20", "🇸🇪 OMX 30", "🇵🇹 PSI 20", "🇧🇪 BEL 20"],
    "🌏 Asia-Pacífico":    ["🇯🇵 Nikkei 225", "🇭🇰 Hang Seng", "🇦🇺 ASX 200", "🇰🇷 KOSPI", "🇮🇳 BSE Sensex"],
    "🌎 América":          ["🇨🇦 TSX", "🇧🇷 Bovespa", "🇲🇽 IPC México"],
    "🪙 Otros":            ["🪙 Crypto", "🛢️ Materias Primas", "📊 Futuros", "📈 Índices CFD"],

    "💱 Divisas":          ["💱 Divisas"],
}

_COLS_POR_REGION = 4  # máximo por fila

mercados_sel = []
for region, mercados_region in REGIONES.items():
    st.markdown(
        f"<div style='background:var(--tv-panel);border-left:3px solid #2a4a6a;border-radius:6px;"
        f"padding:6px 14px 2px 14px;margin-bottom:4px;font-size:12px;color:var(--tv-muted);font-weight:700;letter-spacing:1px'>"
        f"{region}</div>",
        unsafe_allow_html=True,
    )
    n_cols = min(_COLS_POR_REGION, len(mercados_region))
    for fila_start in range(0, len(mercados_region), n_cols):
        fila = mercados_region[fila_start:fila_start + n_cols]
        cols = st.columns(n_cols)
        for i, nombre in enumerate(fila):
            default = nombre == "🇺🇸 NASDAQ 100"
            if cols[i].checkbox(nombre, value=default, key=f"chk_{nombre}"):
                mercados_sel.append(nombre)

st.markdown(
    "<div style='margin-top:12px;margin-bottom:4px;font-size:12px;font-weight:700;"
    "color:var(--tv-muted);text-transform:uppercase;letter-spacing:.8px'>"
    "➕ " + T["custom"] + "</div>",
    unsafe_allow_html=True,
)
raw_custom = st.text_input(
    label="tickers_custom",
    label_visibility="collapsed",
    placeholder="Ej: AUDUSD, XAUUSD, US500, BTC, AAPL  (separados por coma)",
    value="",
)
_CURRENCIES = {"USD","EUR","GBP","JPY","AUD","NZD","CAD","CHF","SEK","NOK",
               "SGD","MXN","BRL","HKD","CNY","ZAR","TRY","PLN","DKK","HUF"}
_BROKER_TO_YAHOO = {
    # Materias primas broker → yfinance
    "XAUUSD":"GC=F","XAGUSD":"SI=F","XTIUSD":"CL=F","USOIL":"CL=F",
    "UKOIL":"BZ=F","XNGUSD":"NG=F","XPTUSD":"PL=F","XPDUSD":"PA=F",
    # Índices broker → yfinance
    "SP500":"^GSPC","US500":"^GSPC","SPX":"^GSPC",
    "NDQ":"^NDX","NAS100":"^NDX","US100":"^NDX","NASDAQ":"^NDX",
    "WS30":"^DJI","US30":"^DJI","DOW":"^DJI",
    "GDAXI":"^GDAXI","GER40":"^GDAXI","DAX":"^GDAXI",
    "UK100":"^FTSE","FTSE":"^FTSE",
    "STOXX50E":"^STOXX50E","EU50":"^STOXX50E",
    "NI225":"^N225","JP225":"^N225","JPN225":"^N225",
    "AUS200":"^AXJO","ASX200":"^AXJO",
    "FCHI40":"^FCHI","FRA40":"^FCHI","CAC40":"^FCHI",
    "SPA35":"^IBEX","IBEX35":"^IBEX","ESP35":"^IBEX",
    "US2000":"^RUT","RUSSELL":"^RUT",
    "HK50":"^HSI","HKG33":"^HSI",
}

def _normalizar_ticker(t: str) -> str:
    t = t.strip().upper().replace(" ", "")
    # Ya tiene sufijo yfinance — devolver tal cual
    if t.endswith("=X") or t.endswith("=F") or t.endswith("-USD") or t.startswith("^"):
        return t
    # Mapeo directo broker → yfinance
    if t in _BROKER_TO_YAHOO:
        return _BROKER_TO_YAHOO[t]
    # Par forex de 6 letras (EURUSD, AUDJPY…)
    if len(t) == 6 and t[:3] in _CURRENCIES and t[3:] in _CURRENCIES:
        return t + "=X"
    # Crypto sin sufijo (BTC, ETH…)
    _CRYPTO_BASE = {"BTC","ETH","XRP","ADA","DOGE","SOL","BNB","DOT","LTC","AVAX","LINK","MATIC","DASH","XMR","NEO"}
    if t in _CRYPTO_BASE:
        return t + "-USD"
    return t

custom_tickers = [_normalizar_ticker(t) for t in raw_custom.split(",") if t.strip()]

tickers_mercado = []
for m in mercados_sel:
    tickers_mercado += MERCADOS[m]
tickers_all = list(dict.fromkeys(tickers_mercado + custom_tickers))

st.caption(f"**{len(tickers_all)} tickers** seleccionados para escanear")

# ── Filtro de resultados ──────────────────────────────────────────────────────
# ── Funciones auxiliares ──────────────────────────────────────────────────────

def generar_narrativa(row, oversold, overbought, vol_mult, roc_min, perfil_nombre):
    """Genera una explicación narrativa de la señal detectada."""
    ticker   = row["Ticker"]
    precio   = row["Precio"]
    k        = row["K"]
    d        = row["D"]
    vol_ma   = row["Vol/MA"]
    roc      = row["ROC%"]
    soporte  = row["Soporte"]
    resis    = row["Resistencia"]
    retroceso= row["_retroceso_pct"]
    nivel    = row["_nivel_cercano"]
    score    = row["_score_total"]
    fib_s    = row["_fib_score"]
    gatillo  = row["Gatillo💥"]
    vela_txt = row["VelaAnterior🕯️"]

    # Párrafo 1 — contexto técnico
    k_intensidad = "extrema" if k < 10 else "clara" if k < 15 else "moderada"
    vol_desc = f"un {vol_ma:.1f}x por encima" if vol_ma >= 1 else f"un {vol_ma:.1f}x de"
    roc_desc = "positivo y acelerado" if roc > 3 else "positivo aunque contenido" if roc > 0 else f"ligeramente negativo ({roc:.1f}%)"
    cruce_desc = "cruzando al alza" if row["Cruce K>D"] else "próximo a cruzar"

    p1 = (
        f"**{ticker}** ha activado una señal de entrada bajo el perfil **{perfil_nombre}**. "
        f"El oscilador estocástico K se encuentra en **{k:.1f}**, zona de sobreventa {k_intensidad} "
        f"(umbral {oversold}), {cruce_desc} su línea de señal D ({d:.1f}), lo que indica un posible "
        f"agotamiento de la presión vendedora y el inicio de un giro alcista."
    )

    # Párrafo 2 — volumen y momentum
    p2 = (
        f"El volumen de la sesión es {vol_desc} la media de los últimos 20 períodos, "
        f"{'confirmando la señal con participación institucional.' if vol_ma >= 1.2 else 'acompañando la señal con actividad por encima de lo habitual.' if vol_ma >= 1 else 'aunque sin confirmación plena de volumen, dentro del umbral permitido por el perfil seleccionado.'} "
        f"El momentum medido por el ROC es {roc_desc}, "
        f"{'lo que refuerza la dirección alcista esperada.' if roc > 0 else 'lo que exige mayor vigilancia en la confirmación del gatillo.'}"
    )

    # Párrafo 3 — soporte y fibonacci
    dist_sop_pct = round((precio - soporte) / soporte * 100, 2)
    fib_calidad  = "óptima" if 40 <= retroceso <= 60 else "favorable" if 30 <= retroceso <= 70 else "alejada del punto ideal"
    p3 = (
        f"El precio ({precio:.2f}) se sitúa un **{dist_sop_pct:.1f}%** por encima del soporte estructural "
        f"en {soporte:.2f}, con resistencia en {resis:.2f}. Desde el máximo histórico del período, "
        f"el activo lleva un retroceso del **{retroceso:.1f}%**, próximo al nivel Fibonacci **{nivel}** — "
        f"una posición {fib_calidad} para buscar el rebote. "
        f"El score Fibonacci de {fib_s:.0f}/100 {'refuerza significativamente' if fib_s >= 70 else 'apoya' if fib_s >= 40 else 'no refuerza decisivamente'} la confluencia técnica."
    )

    # Párrafo 4 — gatillo
    es_alcista = "Alcista" in vela_txt
    if es_alcista:
        p4 = (
            f"La vela anterior cerró en **verde (alcista)**, lo que activa el gatillo de entrada. "
            f"La operación se confirma cuando el precio supere **{gatillo:.2f}** (máximo de esa vela). "
            f"Mientras no se rompa ese nivel, la señal permanece en espera aunque las condiciones técnicas estén alineadas."
        )
    else:
        p4 = (
            f"⏳ La vela anterior cerró en **rojo (bajista)**, por lo que el gatillo de activación "
            f"**aún no está disponible**. Hay que esperar a que una sesión cierre en positivo y el precio "
            f"supere su máximo ({gatillo:.2f}) para confirmar la entrada. La señal técnica está activa pero pendiente de confirmación."
        )

    # Párrafo 5 — score global
    valoracion = "excelente" if score >= 80 else "buena" if score >= 60 else "moderada" if score >= 40 else "baja"
    p5 = (
        f"El **score total de la señal es {score:.0f}/100** ({valoracion}), combinando la calidad técnica "
        f"({row['_score_tecnico']:.0f}/100) con la posición en Fibonacci ({fib_s:.0f}/100). "
        f"{'Se trata de una de las señales de mayor calidad del escaneo actual.' if score >= 75 else 'La señal es operativa aunque conviene gestionar el riesgo con disciplina.' if score >= 50 else 'Operar con tamaño reducido dado el score moderado.'}"
    )

    return f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}"


def obtener_fundamentales(ticker: str) -> dict:
    """Obtiene datos fundamentales de yfinance. Devuelve dict vacío si no hay datos (crypto etc.)."""
    try:
        info = yf.Ticker(ticker).info
        if not info or info.get("quoteType") in ("CRYPTOCURRENCY", "CURRENCY"):
            return {}

        def fmt_num(v, decimals=2):
            if v is None: return "N/D"
            return f"{v:,.{decimals}f}"

        def fmt_pct(v):
            if v is None: return "N/D"
            return f"{v*100:.1f}%"

        def fmt_mil(v):
            if v is None: return "N/D"
            if abs(v) >= 1e12: return f"${v/1e12:.2f}T"
            if abs(v) >= 1e9:  return f"${v/1e9:.2f}B"
            if abs(v) >= 1e6:  return f"${v/1e6:.2f}M"
            return f"${v:,.0f}"

        rec_map = {
            "strongBuy":   "Compra fuerte", "strong_buy":   "Compra fuerte",
            "buy":         "Compra",
            "hold":        "Neutral",       "underperform": "Venta",
            "sell":        "Venta",
            "strongSell":  "Venta fuerte",  "strong_sell":  "Venta fuerte",
            "none":        None,            "":             None,
        }

        # Intentar derivar recomendación desde recommendations_summary si recommendationKey es nulo
        rec_key_raw = (info.get("recommendationKey") or "").lower()
        rec_derivada = rec_map.get(rec_key_raw)
        if rec_derivada is None:
            try:
                t_obj = yf.Ticker(ticker)
                rs = t_obj.recommendations_summary
                if rs is not None and not rs.empty:
                    row_rs = rs.iloc[0]
                    sb = int(row_rs.get("strongBuy", 0) or 0)
                    b  = int(row_rs.get("buy",       0) or 0)
                    h  = int(row_rs.get("hold",      0) or 0)
                    s  = int(row_rs.get("sell",      0) or 0)
                    ss = int(row_rs.get("strongSell",0) or 0)
                    total = sb + b + h + s + ss or 1
                    pct_buy  = (sb + b) / total
                    pct_sell = (s + ss) / total
                    if pct_buy >= 0.60:        rec_derivada = "Compra fuerte" if sb > b else "Compra"
                    elif pct_sell >= 0.40:     rec_derivada = "Venta fuerte"  if ss > s else "Venta"
                    else:                      rec_derivada = "Neutral"
            except Exception:
                rec_derivada = "Neutral"
        rec_final = rec_derivada or "Neutral"

        return {
            "nombre":           info.get("longName") or info.get("shortName", ticker),
            "sector":           info.get("sector", "N/D"),
            "industria":        info.get("industry", "N/D"),
            "pais":             info.get("country", "N/D"),
            "market_cap":       fmt_mil(info.get("marketCap")),
            "pe_trailing":      fmt_num(info.get("trailingPE")),
            "pe_forward":       fmt_num(info.get("forwardPE")),
            "pb":               fmt_num(info.get("priceToBook")),
            "roe":              fmt_pct(info.get("returnOnEquity")),
            "debt_equity":      fmt_num(info.get("debtToEquity")),
            "rev_growth":       fmt_pct(info.get("revenueGrowth")),
            "earn_growth":      fmt_pct(info.get("earningsGrowth")),
            "margen_neto":      fmt_pct(info.get("profitMargins")),
            "free_cashflow":    fmt_mil(info.get("freeCashflow")),
            "dividend_yield":   fmt_pct(info.get("dividendYield")),
            "beta":             fmt_num(info.get("beta")),
            "target_precio":    fmt_num(info.get("targetMeanPrice")),
            "upside":           fmt_pct((info.get("targetMeanPrice", 0) / info.get("currentPrice", 1) - 1)) if info.get("targetMeanPrice") and info.get("currentPrice") else "N/D",
            "recomendacion":    rec_final,
            "n_analistas":      info.get("numberOfAnalystOpinions", "N/D"),
            "_desc_original":   (info.get("longBusinessSummary") or "")[:600],
            "_raw_pe":          info.get("trailingPE"),
            "_raw_pb":          info.get("priceToBook"),
            "_raw_roe":         info.get("returnOnEquity"),
            "_raw_de":          info.get("debtToEquity"),
            "_raw_rg":          info.get("revenueGrowth"),
            "_raw_beta":        info.get("beta"),
        }
    except Exception:
        return {}


def narrativa_fundamental(ticker, f, precio_actual):
    """Genera párrafo narrativo con los datos fundamentales."""
    if not f:
        return "ℹ️ No hay datos fundamentales disponibles para este activo (crypto o datos no públicos)."

    partes = []

    # Valoración
    pe = f.get("_raw_pe")
    pb = f.get("_raw_pb")
    if pe:
        if pe < 15:
            partes.append(f"El PER de **{f['pe_trailing']}x** sugiere que la acción cotiza a un precio **atractivo** en relación a sus beneficios.")
        elif pe < 25:
            partes.append(f"El PER de **{f['pe_trailing']}x** refleja una valoración **razonable** para el sector.")
        else:
            partes.append(f"El PER de **{f['pe_trailing']}x** indica una valoración **exigente**, por lo que el crecimiento esperado deberá justificarla.")

    # Rentabilidad
    roe = f.get("_raw_roe")
    if roe:
        roe_desc = "**alta** (empresa eficiente en uso del capital)" if roe > 0.15 else "**moderada**" if roe > 0.08 else "**baja**, lo que invita a revisar la eficiencia operativa"
        partes.append(f"La rentabilidad sobre recursos propios (ROE) es {roe_desc} ({f['roe']}).")

    # Crecimiento
    rg = f.get("_raw_rg")
    if rg:
        rg_desc = "**sólido crecimiento de ingresos**" if rg > 0.1 else "**crecimiento moderado**" if rg > 0 else "**contracción de ingresos**, factor de riesgo a considerar"
        partes.append(f"La compañía muestra {rg_desc} ({f['rev_growth']} interanual).")

    # Deuda
    de = f.get("_raw_de")
    if de:
        de_desc = "bajo, con un balance sólido" if de < 50 else "moderado" if de < 100 else "**elevado**, lo que añade riesgo financiero en entornos de tipos altos"
        partes.append(f"El apalancamiento deuda/equity es {de_desc} ({f['debt_equity']}).")

    # Consenso analistas
    rec = f.get("recomendacion", "N/D")
    target = f.get("target_precio", "N/D")
    upside = f.get("upside", "N/D")
    n = f.get("n_analistas", "N/D")
    if rec != "N/D":
        partes.append(f"El consenso de **{n} analistas** es **{rec}** con precio objetivo en {target} (potencial {upside} desde el precio actual de {precio_actual:.2f}).")

    # Beta
    beta = f.get("_raw_beta")
    if beta:
        beta_desc = "alta volatilidad respecto al mercado" if beta > 1.3 else "volatilidad similar al mercado" if beta > 0.8 else "menor volatilidad que el mercado (activo defensivo)"
        partes.append(f"Con una beta de **{f['beta']}**, el activo presenta {beta_desc}.")

    return " ".join(partes) if partes else "Datos fundamentales disponibles pero incompletos para este período."


_FUTURES_TV = {
    # Metales
    "GC=F": "COMEX:GC1!",  "SI=F": "COMEX:SI1!",  "HG=F": "COMEX:HG1!",
    "PA=F": "NYMEX:PA1!",  "PL=F": "NYMEX:PL1!",
    "CC=F": "ICEUS:CC1!",  "KC=F": "ICEUS:KC1!",
    # Energía
    "CL=F": "NYMEX:CL1!",  "BZ=F": "NYMEX:BB1!",  "NG=F": "NYMEX:NG1!",
    # Agrícolas
    "ZW=F": "CBOT:ZW1!",   "ZC=F": "CBOT:ZC1!",   "ZS=F": "CBOT:ZS1!",
    # Índices EE.UU. — contratos estándar
    "ES=F":  "CME:ES1!",   "NQ=F":  "CME:NQ1!",   "RTY=F": "CME:RTY1!",
    "YM=F":  "CBOT:YM1!",  "EMD=F": "CME:EMD1!",
    # Micro contratos
    "MES=F": "CME:MES1!",  "MNQ=F": "CME:MNQ1!",
    "M2K=F": "CME:M2K1!",  "MYM=F": "CBOT:MYM1!",
    # Bonos
    "ZN=F":  "CBOT:ZN1!",  "ZB=F":  "CBOT:ZB1!",
    # Índices europeos/asiáticos — TVC es el feed de índices puros de TradingView
    "^GDAXI":    "TVC:DAX",    "^STOXX50E": "TVC:SX5E",
    "^FTSE":     "TVC:UKX",    "^N225":     "TVC:NI225",
    # Índices CFD adicionales
    "^GSPC":     "TVC:SPX",    "^NDX":      "TVC:NDX",
    "^DJI":      "TVC:DJI",    "^RUT":      "TVC:RUT",
    "^HSI":      "TVC:HSI",    "^AXJO":     "TVC:ASX200",
    # Índices Darwinex / Europa extra
    "^IBEX":     "TVC:IBEX",   "^FCHI":     "TVC:CAC40",
}
_ETFS_TV = {
    "GLD": "AMEX:GLD", "SLV": "AMEX:SLV", "USO": "AMEX:USO",
    "UNG": "AMEX:UNG", "PDBC": "NASDAQ:PDBC", "DBA": "AMEX:DBA",
    "DBB": "AMEX:DBB", "PALL": "AMEX:PALL", "PPLT": "AMEX:PPLT",
}

def tradingview_url(ticker: str) -> str:
    """Convierte un ticker de yfinance al enlace de TradingView."""
    t = ticker.upper()
    if t in _FUTURES_TV:
        sym = _FUTURES_TV[t]
    elif t in _ETFS_TV:
        sym = _ETFS_TV[t]
    elif t.endswith(".MC"):
        sym = "BME:" + t.replace(".MC", "")
    elif t.endswith(".DE"):
        sym = "XETR:" + t.replace(".DE", "")
    elif t.endswith(".PA"):
        sym = "EURONEXT:" + t.replace(".PA", "")
    elif t.endswith(".L"):
        sym = "LSE:" + t.replace(".L", "")
    elif t.endswith(".MI"):
        sym = "MIL:" + t.replace(".MI", "")
    elif t.endswith(".AS"):
        sym = "EURONEXT:" + t.replace(".AS", "")
    elif t.endswith(".T"):
        sym = "TSE:" + t.replace(".T", "")
    elif t.endswith(".HK"):
        sym = "HKEX:" + t.replace(".HK", "")
    elif t.endswith(".AX"):
        sym = "ASX:" + t.replace(".AX", "")
    elif t.endswith(".KS"):
        sym = "KRX:" + t.replace(".KS", "")
    elif t.endswith(".NS"):
        sym = "NSE:" + t.replace(".NS", "")
    elif t.endswith(".TO"):
        sym = "TSX:" + t.replace(".TO", "")
    elif t.endswith(".SA"):
        sym = "BMFBOVESPA:" + t.replace(".SA", "")
    elif t.endswith(".MX"):
        sym = "BMV:" + t.replace(".MX", "")
    elif t.endswith("-USD"):
        sym = t.replace("-USD", "") + "USD"
    elif t.endswith("=X"):
        sym = "FX:" + t.replace("=X", "")
    else:
        # Ticker sin sufijo → mercado americano.
        # Usamos el parámetro de búsqueda de TradingView que auto-resuelve
        # NASDAQ / NYSE / AMEX sin ambigüedad con mercados extranjeros.
        return f"https://www.tradingview.com/chart/?symbol={t}&exchange=US"
    return f"https://www.tradingview.com/chart/?symbol={sym}"

def stochastic(high, low, close, k_period, d_period):
    ll = low.rolling(k_period).min()
    hh = high.rolling(k_period).max()
    k  = 100 * (close - ll) / (hh - ll + 1e-10)
    d  = k.rolling(d_period).mean()
    return k, d

def roc(close, period):
    return ((close - close.shift(period)) / close.shift(period)) * 100

def cruce_reciente_up(a, b, ventana):
    """K cruzó por encima de D en las últimas `ventana` barras."""
    for i in range(1, ventana + 1):
        if len(a) > i and (a.iloc[-i] > b.iloc[-i]) and (a.iloc[-i-1] <= b.iloc[-i-1]):
            return True
    return False

def calcular_trade(precio, soporte, swing_high, swing_low):
    """Distribución de profits dentro del recorrido entrada → máximo histórico.

    El máximo histórico (swing_high) es el 100% del objetivo — no se va más allá.
    Las salidas parciales usan ratios Fibonacci sobre el recorrido pendiente.

    TP1 (50%):  38.2% del camino entrada → swing_high
    TP2 (30%):  61.8% del camino entrada → swing_high
    TP3 (20%):  swing_high — cierra el 100% de la posición
    """
    entrada = precio
    sl = round(soporte * 0.99, 6)
    riesgo = entrada - sl
    riesgo_pct = round((riesgo / entrada) * 100, 2)

    recorrido = swing_high - entrada  # distancia que queda hasta el máximo
    if recorrido <= 0:
        recorrido = riesgo * 2

    tp1 = round(entrada + recorrido * 0.382, 6)
    tp2 = round(entrada + recorrido * 0.618, 6)
    tp3 = round(swing_high, 6)

    rr1 = round((tp1 - entrada) / riesgo, 2) if riesgo > 0 else 0
    rr2 = round((tp2 - entrada) / riesgo, 2) if riesgo > 0 else 0
    rr3 = round((tp3 - entrada) / riesgo, 2) if riesgo > 0 else 0

    return dict(entrada=entrada, sl=sl, tp1=tp1, tp2=tp2, tp3=tp3,
                riesgo=round(riesgo, 6), riesgo_pct=riesgo_pct,
                rr1=rr1, rr2=rr2, rr3=rr3)


def calcular_trade_short(precio, resistencia, swing_high, swing_low):
    """Trade SHORT: entrada en gatillo bajista, SL sobre resistencia, TPs hacia abajo."""
    entrada    = precio
    sl         = round(resistencia * 1.01, 6)          # SL 1% sobre resistencia
    riesgo     = sl - entrada
    riesgo_pct = round((riesgo / entrada) * 100, 2)

    recorrido = entrada - swing_low                    # distancia hasta el mínimo
    if recorrido <= 0:
        recorrido = riesgo * 2

    tp1 = round(entrada - recorrido * 0.382, 6)
    tp2 = round(entrada - recorrido * 0.618, 6)
    tp3 = round(swing_low, 6)

    rr1 = round((entrada - tp1) / riesgo, 2) if riesgo > 0 else 0
    rr2 = round((entrada - tp2) / riesgo, 2) if riesgo > 0 else 0
    rr3 = round((entrada - tp3) / riesgo, 2) if riesgo > 0 else 0

    return dict(entrada=entrada, sl=sl, tp1=tp1, tp2=tp2, tp3=tp3,
                riesgo=round(riesgo, 6), riesgo_pct=riesgo_pct,
                rr1=rr1, rr2=rr2, rr3=rr3)


def ticker_para_pine(ticker: str) -> str:
    """Convierte ticker Yahoo → símbolo TradingView para usar en Pine Script."""
    url = tradingview_url(ticker)
    # Extrae el símbolo del parámetro ?symbol=XXX o la última parte de la URL
    if "symbol=" in url:
        sym = url.split("symbol=")[-1].split("&")[0]
        return sym
    return ticker

def generar_pinescript(ticker, t, stoch_k, stoch_d, vol_period, sr_period,
                       roc_period, oversold, overbought, vol_mult, roc_min,
                       cruce_ventana, interval, direccion="long"):
    """Genera Pine Script v5 estrategia lista para pegar en TradingView.
    direccion: 'long' para BUY, 'short' para SHORT.
    """
    tv_ticker = ticker_para_pine(ticker)
    e   = t["entrada"]
    sl  = t["sl"]
    tp1 = t["tp1"]
    tp2 = t["tp2"]
    tp3 = t["tp3"]
    is_short = (direccion == "short")

    if is_short:
        dir_label   = "SHORT"
        entry_dir   = "strategy.short"
        entry_icon  = "↓"
        cond_var    = "condiciones_short"
        cond_def    = (f'sobrecompra   = k > {overbought} and ta.crossunder(k, d)\n'
                       f'vela_roja_prev = close[1] < open[1]\n'
                       f'gatillo_short  = low[1]\n'
                       f'rotura_minimo  = close < gatillo_short')
        cond_line   = f'{cond_var} = sobrecompra and close < resistencia and vela_roja_prev and rotura_minimo'
        entry_label = '"SHORT", style=label.style_label_down, color=color.red'
        salida_cond = 'close <= soporte'
        salida_dir  = "abovebar" # label salida short arriba
        plotshape_loc_entry = "location.abovebar"
        plotshape_style_entry = "shape.triangledown"
        plotshape_loc_salida  = "location.belowbar"
        # TP van hacia abajo: tp1 < tp2 < tp3 (tp3 = mínimo)
        tp_entry_cond = lambda n, v: f'if en_posicion and low <= {v:.4f}'
    else:
        dir_label   = "BUY"
        entry_dir   = "strategy.long"
        entry_icon  = "↑"
        cond_var    = "condiciones_entrada"
        cond_def    = f'sobreventa = k < {oversold} and ta.crossover(k, d)'
        cond_line   = f'{cond_var} = sobreventa and filtro_volumen and close > soporte'
        entry_label = '"Entrada", style=label.style_label_up, color=color.green'
        salida_cond = 'close >= resistencia'
        salida_dir  = "belowbar"
        plotshape_loc_entry   = "location.belowbar"
        plotshape_style_entry = "shape.triangleup"
        plotshape_loc_salida  = "location.abovebar"
        tp_entry_cond = lambda n, v: f'if en_posicion and high >= {v:.4f}'

    lines = [
        '//@version=5',
        f'// Momento Dulce — {dir_label} {tv_ticker}',
        f'// Pega en Pine Editor > Nuevo script > Estrategia > Añadir al gráfico',
        f'strategy("Sistema Estocástico + Volumen + S/R — {dir_label} {tv_ticker}", overlay=true,',
        '         default_qty_type=strategy.percent_of_equity, default_qty_value=10)',
        '',
        '// === Indicadores base === //',
        f'k = ta.stoch(close, high, low, {stoch_k})',
        f'd = ta.sma(k, {stoch_d})',
        '',
        '// === Condición Estocástico === //',
        cond_def,
        '',
        '// === Filtro de volumen === //',
        'vol    = volume',
        f'vol_ma = ta.sma(volume, {vol_period})',
        f'filtro_volumen = vol > vol_ma * {vol_mult}',
        '',
        '// === Soporte y resistencia dinámica === //',
        f'lookback    = {sr_period}',
        'soporte     = ta.lowest(low,   lookback)',
        'resistencia = ta.highest(high, lookback)',
        '',
        '// === Condición de entrada === //',
        cond_line,
        '',
        '// === Salida por nivel opuesto === //',
        f'salida = {salida_cond}',
        '',
        '// === Entrada === //',
        f'if {cond_var}',
        f'    strategy.entry("MD_{dir_label}", {entry_dir})',
        f'    label.new(bar_index, {"low" if not is_short else "high"}, "{entry_icon} {dir_label}", style=label.style_label_{"up" if not is_short else "down"}, color={"color.green" if not is_short else "color.red"}, textcolor=color.white)',
        '',
        '// === Salida por nivel opuesto === //',
        'if salida',
        '    strategy.close_all()',
        f'    label.new(bar_index, {"high" if not is_short else "low"}, "SALIDA", style=label.style_label_{"down" if not is_short else "up"}, color={"color.red" if not is_short else "color.green"}, textcolor=color.white)',
        '',
        '// === Salidas parciales por TP (Stop + 3 niveles) === //',
        f'en_posicion = strategy.position_size {">" if not is_short else "<"} 0',
        'if en_posicion',
        f'    strategy.exit("SL", from_entry="MD_{dir_label}", stop={sl:.4f}, qty_percent=100, comment="Stop Loss")',
        tp_entry_cond(1, tp1),
        f'    strategy.close("MD_{dir_label}", qty_percent=50, comment="TP1 50%")',
        tp_entry_cond(2, tp2),
        f'    strategy.close("MD_{dir_label}", qty_percent=60, comment="TP2 30%")',
        tp_entry_cond(3, tp3),
        '    strategy.close_all(comment="TP3 — cierra todo")',
        '',
        '// === Dibujos de Soporte y Resistencia === //',
        'plot(soporte,     title="Soporte",     color=color.green, linewidth=1)',
        'plot(resistencia, title="Resistencia", color=color.red,   linewidth=1)',
        '',
        '// === Marcadores en el gráfico === //',
        f'plotshape({cond_var}, location={plotshape_loc_entry}, color={"color.green" if not is_short else "color.red"}, style=shape.{"triangleup" if not is_short else "triangledown"}, title="{dir_label}", text="{entry_icon}")',
        f'plotshape(salida, location={plotshape_loc_salida}, color={"color.red" if not is_short else "color.green"}, style=shape.labeldown, title="Salida", text="OUT")',
        '',
        '// === Líneas horizontales — se extienden hacia adelante === //',
        f'hline({e:.4f},   "📍 Entrada", color=color.white, linestyle=hline.style_solid,  linewidth=2)',
        f'hline({sl:.4f},  "🛑 Stop",    color=color.red,   linestyle=hline.style_dashed, linewidth=2)',
        f'hline({tp1:.4f}, "🎯 TP1",     color=color.lime,  linestyle=hline.style_dotted, linewidth=1)',
        f'hline({tp2:.4f}, "🏆 TP2",     color=color.green, linestyle=hline.style_solid,  linewidth=2)',
        f'hline({tp3:.4f}, "🚀 TP3",     color=color.teal,  linestyle=hline.style_solid,  linewidth=2)',
        '',
        '// === Labels con valores exactos en la última barra === //',
        'if barstate.islast',
        f'    label.new(bar_index + 2, {e:.4f},   "📍 ENTRADA\\n{e:.4f}",   color=color.new(color.gray,  10), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 2, {sl:.4f},  "🛑 STOP\\n{sl:.4f}",    color=color.new(color.red,   10), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 2, {tp1:.4f}, "🎯 TP1 50%\\n{tp1:.4f}",color=color.new(color.lime,  10), textcolor=color.black, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 2, {tp2:.4f}, "🏆 TP2 30%\\n{tp2:.4f}",color=color.new(color.green, 10), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 2, {tp3:.4f}, "🚀 TP3 20%\\n{tp3:.4f}",color=color.new(color.teal,  10), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        '',
        '// === Alertas === //',
        f'alertcondition({cond_var}, "{dir_label} {tv_ticker}", "{dir_label} {tv_ticker} — precio: {{{{close}}}}")',
        f'alertcondition(salida,     "SALIDA {tv_ticker}", "Salida {tv_ticker}")',
    ]
    return '\n'.join(lines)


def generar_pinescript_estrategia(ticker, tr):
    """Genera Pine Script v5 estrategia con SL/TP1/TP2/TP3 configurados para backtesting."""
    entrada = tr["entrada"]
    sl      = tr["sl"]
    tp1     = tr["tp1"]
    tp2     = tr["tp2"]
    tp3     = tr["tp3"]
    lines = [
        '//@version=5',
        f'// Momento Dulce — ESTRATEGIA {ticker}',
        f'// Pega en Pine Editor > Nuevo script > Estrategia > Añadir al gráfico',
        f'strategy("Momento Dulce {ticker}", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1)',
        '',
        '// ══════════════════════════════════════════════',
        '// NIVELES DE OPERACIÓN — editables en el panel',
        '// ══════════════════════════════════════════════',
        f'p_entrada = input.float({entrada:.2f}, "📍 Entrada",              step=0.01)',
        f'p_sl      = input.float({sl:.2f},      "🛑 Stop Loss",            step=0.01)',
        f'p_tp1     = input.float({tp1:.2f},     "🎯 TP1  50% pos | 38.2% recorrido", step=0.01)',
        f'p_tp2     = input.float({tp2:.2f},     "🏆 TP2  30% pos | 61.8% recorrido", step=0.01)',
        f'p_tp3     = input.float({tp3:.2f},     "🚀 TP3  20% pos | Máximo histórico", step=0.01)',
        '',
        '// ══════════════════════════════════════════════',
        '// ENTRADA — precio cruza al alza el nivel entrada',
        '// ══════════════════════════════════════════════',
        'comprado = strategy.position_size > 0',
        'if not comprado and close >= p_entrada',
        '    strategy.entry("BUY", strategy.long, comment="Entrada " + str.tostring(p_entrada))',
        '',
        '// ══════════════════════════════════════════════',
        '// GESTIÓN DE POSICIÓN — salidas escalonadas',
        '// ══════════════════════════════════════════════',
        '// Stop Loss — cierra el 100% si se activa',
        'if comprado',
        '    strategy.exit("SL", from_entry="BUY", stop=p_sl, qty_percent=100, comment="Stop Loss")',
        '',
        '// TP1: cierra 50% al llegar al 38.2% del recorrido',
        'if comprado and high >= p_tp1 and strategy.opentrades.size(0) > 0',
        '    strategy.close("BUY", qty_percent=50, comment="TP1 50% | " + str.tostring(p_tp1))',
        '',
        '// TP2: cierra 30% de lo que queda (= 60% del restante 50%) al 61.8%',
        'if comprado and high >= p_tp2 and strategy.opentrades.size(0) > 0',
        '    strategy.close("BUY", qty_percent=60, comment="TP2 30% | " + str.tostring(p_tp2))',
        '',
        '// TP3: cierra todo lo que queda en el máximo histórico',
        'if comprado and high >= p_tp3',
        '    strategy.close_all(comment="TP3 todo | " + str.tostring(p_tp3))',
        '',
        '// ══════════════════════════════════════════════',
        '// LÍNEAS Y ETIQUETAS VISUALES',
        '// ══════════════════════════════════════════════',
        'var line l_e   = na',
        'var line l_sl  = na',
        'var line l_tp1 = na',
        'var line l_tp2 = na',
        'var line l_tp3 = na',
        '',
        'if barstate.islast',
        '    x1 = bar_index - 40',
        '    x2 = bar_index + 20',
        '    l_e   := line.new(x1, p_entrada, x2, p_entrada, extend=extend.right, color=color.new(color.white,  0), width=2, style=line.style_solid)',
        '    l_sl  := line.new(x1, p_sl,      x2, p_sl,      extend=extend.right, color=color.new(color.red,    0), width=2, style=line.style_dashed)',
        '    l_tp1 := line.new(x1, p_tp1,     x2, p_tp1,     extend=extend.right, color=color.new(color.lime,   0), width=1, style=line.style_dotted)',
        '    l_tp2 := line.new(x1, p_tp2,     x2, p_tp2,     extend=extend.right, color=color.new(color.green,  0), width=2, style=line.style_solid)',
        '    l_tp3 := line.new(x1, p_tp3,     x2, p_tp3,     extend=extend.right, color=color.new(color.teal,   0), width=2, style=line.style_solid)',
        f'    label.new(bar_index + 21, p_entrada, "ENTRADA\\n{entrada:.2f}",          color=color.new(color.gray,  20), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 21, p_sl,      "🛑 STOP\\n{sl:.2f}",               color=color.new(color.red,   20), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 21, p_tp1,     "🎯 TP1  50%\\n{tp1:.2f}",          color=color.new(color.lime,  20), textcolor=color.black, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 21, p_tp2,     "🏆 TP2  30%\\n{tp2:.2f}",          color=color.new(color.green, 20), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        f'    label.new(bar_index + 21, p_tp3,     "🚀 TP3  20% — TODO\\n{tp3:.2f}",   color=color.new(color.teal,  20), textcolor=color.white, style=label.style_label_left, size=size.normal)',
        '',
        '// ══════════════════════════════════════════════',
        '// ALERTAS',
        '// ══════════════════════════════════════════════',
        f'alertcondition(close >= p_entrada and not comprado, "BUY {ticker}",  "{{{{ticker}}}} ENTRADA en {{{{close}}}}")',
        f'alertcondition(low   <= p_sl       and comprado,    "STOP {ticker}", "{{{{ticker}}}} STOP LOSS en {{{{close}}}}")',
        f'alertcondition(high  >= p_tp1      and comprado,    "TP1 {ticker}",  "{{{{ticker}}}} TP1 alcanzado {{{{close}}}}")',
        f'alertcondition(high  >= p_tp2      and comprado,    "TP2 {ticker}",  "{{{{ticker}}}} TP2 alcanzado {{{{close}}}}")',
        f'alertcondition(high  >= p_tp3      and comprado,    "TP3 {ticker}",  "{{{{ticker}}}} TP3 — CIERRE TOTAL {{{{close}}}}")',
    ]
    return '\n'.join(lines)


def cruce_reciente_down(a, b, ventana):
    for i in range(1, ventana + 1):
        if len(a) > i and (a.iloc[-i] < b.iloc[-i]) and (a.iloc[-i-1] >= b.iloc[-i-1]):
            return True
    return False

# ── Palabras clave de sentimiento ────────────────────────────────────────────
_BULL_5  = {"surge","soar","breakout","skyrocket","record","beat","upgrade","outperform","buy","bullish","rally","boom","explode","highest","strong"}
_BULL_3  = {"rise","gain","grow","up","above","positive","good","improve","recover","bounce","upside","profit","high","advance","exceed","lift","jump","climb","momentum"}
_BEAR_5  = {"crash","plunge","recession","bankrupt","fraud","collapse","warning","panic","crisis","meltdown","sink","rout","tumble","tank","scandal","investigation"}
_BEAR_3  = {"fall","drop","miss","cut","downgrade","sell","weak","decline","loss","bearish","risk","concern","trouble","below","negative","slow","debt","warn","disappoint","lower","slide","slip"}

import math as _math
import datetime as _dt

_INFO_TOOLTIP = {
    "analistas": (
        "📊 Consenso de Analistas",
        "CÓMO SE CALCULA: Se recopilan todas las recomendaciones publicadas por los analistas "
        "que cubren el valor en los últimos 3 meses (strongBuy, buy, hold, sell, strongSell). "
        "El donut divide ese total en 3 grupos: Comprar (strongBuy+buy), Mantener (hold) y Vender (sell+strongSell), "
        "mostrando el % de cada uno. El consenso final (COMPRAR / MANTENER / VENDER) se determina "
        "por el grupo mayoritario: si Comprar supera el 60% → COMPRAR, si Mantener supera el 40% → MANTENER, resto → VENDER. "
        "Los precios objetivo son la media, mínimo y máximo de los targets individuales de cada analista para los próximos 12 meses. "
        "El % potencial es (precio objetivo medio / precio actual - 1) × 100."
    ),
    "insiders": (
        "🔍 Transacciones de Insiders",
        "Registra las compras y ventas de acciones realizadas por directivos, consejeros y accionistas mayoritarios "
        "(comunicadas a la SEC en EE.UU. o al regulador local). "
        "Cuando los insiders compran con su propio dinero suele ser señal de confianza interna. "
        "El gauge muestra el ratio compras vs ventas en valor monetario de los últimos 3 meses. "
        "Fuente: reportes públicos de la SEC."
    ),
    "noticias": (
        "📰 Últimas Noticias",
        "Noticias recientes de fuentes financieras contrastadas (Bloomberg, Reuters, CNBC, Yahoo Finance, MarketWatch, WSJ, Seeking Alpha…). "
        "Cada noticia recibe un score de sentimiento individual basado en el análisis semántico del titular y resumen. "
        "Las noticias se muestran en castellano. Fuente: yfinance news feed."
    ),
    "sentimiento": (
        "🌡️ Sentimiento de Mercado",
        "CÓMO SE CALCULA: Se analizan los titulares y resúmenes de las noticias filtradas para este valor. "
        "Cada palabra se puntúa según dos diccionarios: "
        "MUY ALCISTAS (+5 pts): surge, soar, breakout, beat, record, upgrade, bullish, rally... "
        "ALCISTAS (+3 pts): rise, gain, improve, bounce, profit, jump, climb, momentum... "
        "MUY BAJISTAS (-5 pts): crash, plunge, recession, fraud, collapse, panic, meltdown... "
        "BAJISTAS (-3 pts): fall, drop, miss, cut, downgrade, warn, decline, debt, disappoint... "
        "El score total es la suma de todos los puntos de todas las noticias. "
        "El gauge convierte ese score a un % entre 0 (muy bajista) y 100 (muy alcista): "
        "pct = (score + máx_posible) / (2 × máx_posible) × 100. "
        "El mapa de calor muestra las palabras más frecuentes: tamaño = frecuencia, color = carga semántica."
    ),
}

def _tooltip_popup(uid: str, desc_safe: str, width: int = 300, right: bool = False) -> str:
    """Icono 🔍 clicable (CSS checkbox) que abre popup con ✕. Sin scroll."""
    # uid limpio: solo alfanumérico para evitar problemas con selectores CSS
    import re as _re
    safe = _re.sub(r'[^a-zA-Z0-9]', '', uid)[:32]
    pos = "right:0" if right else "left:0"
    return (
        # CSS primero: selector hermano ~ solo funciona hacia adelante en el DOM
        f"<style>"
        f"#c{safe}{{display:none;position:absolute;pointer-events:none}}"
        f"#c{safe}:checked~.p{safe}{{display:block!important}}"
        f"</style>"
        # Checkbox oculto (display:none en el DOM pero CSS sigue funcionando)
        f"<input type='checkbox' id='c{safe}'>"
        # Label = botón 🔍
        f"<label for='c{safe}' "
        f"style='cursor:pointer;background:#1e3a5f;color:#2962ff;border-radius:50%;"
        f"width:18px;height:18px;font-size:12px;display:inline-flex;align-items:center;"
        f"justify-content:center;border:1px solid #2962ff66;font-weight:900;line-height:1;"
        f"flex-shrink:0;user-select:none'>🔍</label>"
        # Popup — oculto por defecto con inline style
        f"<div class='p{safe}' "
        f"style='display:none;position:absolute;{pos};top:24px;z-index:9999;width:{width}px;"
        f"background:#0d1829;border:1px solid #1e3a5f;border-radius:10px;"
        f"padding:14px 16px;color:#94a3b8;font-size:11px;line-height:1.7;"
        f"white-space:pre-line;box-shadow:0 8px 24px rgba(0,0,0,.7)'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;"
        f"margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #1e3a5f'>"
        f"<span style='color:#d1d4dc;font-size:12px;font-weight:700'>Cómo se calcula</span>"
        # Label ✕ = desmarca el checkbox, cierra el popup
        f"<label for='c{safe}' "
        f"style='cursor:pointer;color:#888;font-size:15px;font-weight:700;"
        f"padding:0 6px;line-height:1;margin-left:12px'>✕</label>"
        f"</div>"
        f"{desc_safe}"
        f"</div>"
    )

def _section_header(key: str) -> str:
    """Título de sección + 🔍 que abre/cierra tooltip al hacer click."""
    titulo, desc = _INFO_TOOLTIP[key]
    desc_safe = desc.replace("<","&lt;").replace(">","&gt;")
    uid = key
    return (
        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:10px'>"
        f"<span style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;"
        f"letter-spacing:1px;font-weight:700'>{titulo}</span>"
        f"<div style='position:relative;display:inline-block'>"
        + _tooltip_popup(uid, desc_safe, width=300)
        + f"</div>"
        f"</div>"
    )

def _score_headline(text: str) -> float:
    words = set(text.lower().split())
    return (sum(5 for w in words if w in _BULL_5) +
            sum(3 for w in words if w in _BULL_3) -
            sum(5 for w in words if w in _BEAR_5) -
            sum(3 for w in words if w in _BEAR_3))

def _polar(cx, cy, r, deg):
    rad = (deg - 90) * _math.pi / 180
    return cx + r * _math.cos(rad), cy + r * _math.sin(rad)

def _arc(cx, cy, r, a1, a2):
    sx, sy = _polar(cx, cy, r, a1)
    ex, ey = _polar(cx, cy, r, a2)
    la = 1 if (a2 - a1) > 180 else 0
    return f"M {sx:.1f} {sy:.1f} A {r} {r} 0 {la} 1 {ex:.1f} {ey:.1f}"

def _gauge_svg(pct, label, color, uid="g", titulo="", subtitulo=""):
    """Gauge semicircular con 5 etiquetas estilo TradingView/TipRanks."""
    a   = _math.radians(180 - pct * 1.8)
    nx  = 100 + 70 * _math.cos(a)
    ny  = 100 - 70 * _math.sin(a)
    # 5 puntos del arco para etiquetas (0%=izq, 25%, 50%=top, 75%, 100%=der)
    return (
        f"<svg viewBox='0 0 200 145' xmlns='http://www.w3.org/2000/svg' style='width:100%;max-width:280px;display:block;margin:0 auto'>"
        f"<defs>"
        f"<linearGradient id='gg{uid}' x1='0%' y1='0%' x2='100%' y2='0%'>"
        f"<stop offset='0%'   stop-color='var(--tv-red)'/>"
        f"<stop offset='25%'  stop-color='#f97316'/>"
        f"<stop offset='50%'  stop-color='var(--tv-yellow)'/>"
        f"<stop offset='75%'  stop-color='#84cc16'/>"
        f"<stop offset='100%' stop-color='var(--tv-green)'/>"
        f"</linearGradient>"
        f"<mask id='gm{uid}'>"
        f"<path d='M 14 100 A 86 86 0 0 1 186 100' stroke='white' stroke-width='20' fill='none' stroke-linecap='round'/>"
        f"</mask>"
        f"</defs>"
        f"<path d='M 14 100 A 86 86 0 0 1 186 100' stroke='var(--tv-border)' stroke-width='20' fill='none' stroke-linecap='round'/>"
        f"<rect x='0' y='0' width='200' height='110' fill='url(#gg{uid})' mask='url(#gm{uid})'/>"
        f"<line x1='100' y1='100' x2='{nx:.1f}' y2='{ny:.1f}' stroke='white' stroke-width='3' stroke-linecap='round'/>"
        f"<circle cx='100' cy='100' r='5' fill='white'/>"
        # Label central
        f"<text x='100' y='120' fill='{color}' font-size='14' font-weight='900' text-anchor='middle' font-family='sans-serif'>{label}</text>"
        + (f"<text x='100' y='133' fill='var(--tv-muted)' font-size='8.5' text-anchor='middle' font-family='sans-serif'>{subtitulo}</text>" if subtitulo else "")
        + f"</svg>"
    )

def _donut_svg(bull_pct, hold_pct, bear_pct, label, sublabel):
    """Donut chart SVG estilo TipRanks."""
    cx, cy, r = 80, 80, 58
    total = bull_pct + hold_pct + bear_pct
    if total == 0:
        return "<div style='color:var(--tv-muted);font-size:12px;text-align:center'>Sin datos</div>"
    b_deg  = bull_pct / total * 360
    h_deg  = hold_pct / total * 360
    br_deg = bear_pct / total * 360
    segs = []
    cur = 0
    for deg, col in [(b_deg,"var(--tv-green)"),(h_deg,"var(--tv-yellow)"),(br_deg,"var(--tv-red)")]:
        if deg < 1: cur += deg; continue
        end = cur + deg
        if deg >= 359.9:
            segs.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{col}' stroke-width='18'/>")
        else:
            segs.append(f"<path d='{_arc(cx,cy,r,cur,end)}' fill='none' stroke='{col}' stroke-width='18' stroke-linecap='butt'/>")
        cur = end
    segs_html = "".join(segs)
    return (
        f"<svg viewBox='0 0 160 160' xmlns='http://www.w3.org/2000/svg' style='width:160px;display:block'>"
        f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='var(--tv-border)' stroke-width='18'/>"
        f"{segs_html}"
        f"<text x='{cx}' y='{cy-8}' fill='white' font-size='18' font-weight='900' text-anchor='middle' font-family='sans-serif'>{label}</text>"
        f"<text x='{cx}' y='{cy+12}' fill='var(--tv-muted)' font-size='9' text-anchor='middle' font-family='sans-serif'>{sublabel}</text>"
        f"</svg>"
    )

def _es_relevante(texto: str, ticker: str, nombre: str) -> bool:
    """Comprueba si una noticia está relacionada con el ticker o empresa."""
    t = texto.lower()
    # Construir términos de búsqueda desde el ticker
    tk = ticker.upper()
    # Variantes del ticker: quitar sufijos de mercado (.MC .DE .PA etc.) y guiones
    tk_base = tk.split(".")[0].replace("-USD","").replace("-","")
    terminos = {tk_base.lower()}
    # Añadir palabras relevantes del nombre de la empresa (>3 chars, no genéricas)
    SKIP_WORDS = {"the","inc","corp","co","ltd","sa","plc","group","holding",
                  "holdings","fund","etf","trust","shares","index"}
    for w in nombre.lower().split():
        w = w.strip(".,()-&")
        if len(w) > 3 and w not in SKIP_WORDS:
            terminos.add(w)
    return any(term in t for term in terminos)

@st.cache_data(show_spinner=False, ttl=1800)
def obtener_noticias(ticker: str, nombre: str = "") -> list:
    try:
        t_obj = yf.Ticker(ticker)
        raw   = t_obj.news or []
        # Si no tenemos nombre, intentar obtenerlo
        if not nombre:
            try:
                info = t_obj.info or {}
                nombre = info.get("longName") or info.get("shortName") or ticker
            except Exception:
                nombre = ticker
        def _parse(n):
            c = n.get("content", {})
            titulo    = c.get("title", n.get("title",""))
            resumen   = c.get("summary","") or n.get("summary","")
            proveedor = (c.get("provider",{}).get("displayName","") or
                         n.get("publisher","") or
                         (n.get("source",{}) or {}).get("name",""))
            url       = c.get("canonicalUrl",{}).get("url","") or n.get("link","") or n.get("url","")
            ts        = c.get("pubDate","") or n.get("providerPublishTime","")
            if isinstance(ts, (int,float)):
                ts = _dt.datetime.utcfromtimestamp(ts).strftime("%d/%m/%Y")
            elif ts:
                ts = str(ts)[:10]
            texto = titulo + " " + resumen
            return {"titulo": titulo, "resumen": resumen[:220], "fuente": proveedor,
                    "url": url, "fecha": ts, "score": _score_headline(texto),
                    "_texto": texto}

        todos = [_parse(n) for n in raw[:30] if n.get("content",{}).get("title") or n.get("title")]
        # Primero las relevantes, luego rellenar con el resto hasta 6
        relevantes = [n for n in todos if _es_relevante(n["_texto"], ticker, nombre)]
        resto      = [n for n in todos if n not in relevantes]
        noticias   = (relevantes + resto)[:6]
        for n in noticias:
            n.pop("_texto", None)
        return noticias
    except Exception:
        return []

@st.cache_data(show_spinner=False, ttl=3600)
def obtener_analistas_insiders(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        target_high = info.get("targetHighPrice")
        target_low  = info.get("targetLowPrice")
        target_mean = info.get("targetMeanPrice")
        current     = info.get("currentPrice") or info.get("regularMarketPrice")
        n_analysts  = info.get("numberOfAnalystOpinions", 0) or 0
        sbuy = buy_r = hold_r = sell_r = ssell = total_rec = 0
        try:
            rec = t.recommendations_summary
            if rec is not None and not rec.empty:
                row = rec.iloc[0]
                sbuy  = int(row.get("strongBuy",  0))
                buy_r = int(row.get("buy",         0))
                hold_r= int(row.get("hold",        0))
                sell_r= int(row.get("sell",        0))
                ssell = int(row.get("strongSell",  0))
                total_rec = sbuy + buy_r + hold_r + sell_r + ssell
        except Exception:
            pass
        ins_buy = ins_sell = 0
        ins_rows = []
        try:
            ins = t.insider_transactions
            if ins is not None and not ins.empty:
                for _, r in ins.head(20).iterrows():
                    val  = float(r.get("Value", 0) or 0)
                    nm   = str(r.get("Insider", r.get("Name","")) or "")[:28]
                    pos  = str(r.get("Position", r.get("Title","")) or "")[:22]
                    dt   = str(r.get("Start Date", r.get("Date","")) or "")[:10]
                    txn  = str(r.get("Transaction", r.get("Type","")) or "").lower()
                    is_buy = any(k in txn for k in ("buy","purchase","acqui"))
                    is_sell = any(k in txn for k in ("sale","sell","disposed"))
                    if not is_buy and not is_sell:
                        continue
                    ttype = "BUY" if is_buy else "SELL"
                    ins_rows.append({"name":nm,"pos":pos,"type":ttype,"val":abs(val),"date":dt})
                    if is_buy:  ins_buy  += abs(val)
                    else:       ins_sell += abs(val)
        except Exception:
            pass
        return {
            "target_high":target_high,"target_low":target_low,
            "target_mean":target_mean,"current":current,
            "n_analysts":n_analysts,
            "sbuy":sbuy,"buy":buy_r,"hold":hold_r,"sell":sell_r,"ssell":ssell,"total_rec":total_rec,
            "ins_buy":ins_buy,"ins_sell":ins_sell,"ins_rows":ins_rows,
        }
    except Exception:
        return {}

def render_noticias_sentimiento(ticker: str, noticias: list, analistas: dict, score_color: str, sesion_iso: str = ""):

    # ── Calcular sentimiento de noticias ─────────────────────────────────────
    total_sc = sent_color = sent_label = sent_icon = pct = bubbles = ""
    gauge_news = ""
    if noticias:
        total_sc = sum(n["score"] for n in noticias)
        max_pos  = len(noticias) * 8
        pct      = max(0, min(100, int((total_sc + max_pos) / (2 * max_pos) * 100)))
        if pct >= 65:   sent_label, sent_color, sent_icon = "Fuerte compra", "var(--tv-green)", "🚀"
        elif pct >= 55: sent_label, sent_color, sent_icon = "Compra",        "#44dd88", "📈"
        elif pct >= 45: sent_label, sent_color, sent_icon = "Neutral",       "var(--tv-yellow)", "⚖️"
        elif pct >= 35: sent_label, sent_color, sent_icon = "Venta",         "#f97316", "📉"
        else:           sent_label, sent_color, sent_icon = "Fuerte venta",  "var(--tv-red)", "🔻"
        gauge_news = _gauge_svg(pct, sent_label, sent_color,
                                uid=f"news{ticker[:3]}",
                                subtitulo=f"Basado en {len(noticias)} noticias")
        # Mapa de calor
        all_words: dict = {}
        STOP = {"that","this","with","from","have","will","were","been","they","their","more","also",
                "when","what","into","than","over","some","just","its","can","for","the","and","but",
                "not","are","was","has","said","says","after","about","would","could","should"}
        for n in noticias:
            for w in (n["titulo"]+" "+n["resumen"]).lower().split():
                w = w.strip(".,;:!?\"'()-")
                if len(w) < 4 or w in STOP: continue
                sc2 = 5 if w in _BULL_5 else 3 if w in _BULL_3 else -5 if w in _BEAR_5 else -3 if w in _BEAR_3 else 0
                all_words[w] = all_words.get(w, 0) + (abs(sc2) if sc2 else 0.4)
        top_words = sorted(all_words.items(), key=lambda x: -x[1])[:40]
        max_freq  = max((f for _,f in top_words), default=1)
        def wc(w):
            if w in _BULL_5: return ("#00ff88","#003d14")
            if w in _BULL_3: return ("#44dd88","#0a2618")
            if w in _BEAR_5: return ("#ff4444","#3d0000")
            if w in _BEAR_3: return ("#ff8844","#2e1000")
            return ("var(--tv-muted)","#1a2233")
        bubbles = ""
        for word, freq in top_words:
            size = int(10 + (freq / max_freq) * 15)
            fc, bg = wc(word)
            bubbles += (f"<span style='background:{bg};color:{fc};font-size:{size}px;"
                        f"padding:3px 9px;border-radius:20px;border:1px solid {fc}33;"
                        f"display:inline-block;margin:3px 2px;font-weight:600'>{word}</span>")

    # ── Calcular consenso analistas ───────────────────────────────────────────
    gauge_analistas = ""
    target_block    = ""
    cons_col        = "var(--tv-muted)"
    consensus       = "Sin datos"
    bull_pct = hold_pct = bear_pct = 0
    if analistas and analistas.get("total_rec", 0) > 0:
        a         = analistas
        total_rec = a["total_rec"]
        bull_pct  = round((a["sbuy"] + a["buy"]) / total_rec * 100)
        hold_pct  = round(a["hold"] / total_rec * 100)
        bear_pct  = round((a["sell"] + a["ssell"]) / total_rec * 100)
        # Convertir a escala 0-100 para el gauge (0=fuerte venta, 100=fuerte compra)
        # strongBuy=100, buy=75, hold=50, sell=25, strongSell=0
        a_pct = round(
            (a["sbuy"]*100 + a["buy"]*75 + a["hold"]*50 + a["sell"]*25 + a["ssell"]*0)
            / max(total_rec, 1)
        )
        if a_pct >= 80:   consensus, cons_col = "Fuerte compra", "var(--tv-green)"
        elif a_pct >= 62: consensus, cons_col = "Compra",        "#84cc16"
        elif a_pct >= 45: consensus, cons_col = "Neutral",       "var(--tv-yellow)"
        elif a_pct >= 28: consensus, cons_col = "Venta",         "#f97316"
        else:             consensus, cons_col = "Fuerte venta",  "var(--tv-red)"
        gauge_analistas = _gauge_svg(a_pct, consensus, cons_col,
                                     uid=f"anal{ticker[:3]}",
                                     subtitulo=f"Según {a['n_analysts']} analistas")
        th = a.get("target_high"); tl = a.get("target_low"); tm = a.get("target_mean")
        cur = a.get("current") or 0
        def fmt(v): return f"{v:.2f}" if v else "N/D"
        upside_pct = f"{((tm/cur)-1)*100:+.1f}%" if tm and cur else ""
        target_block = (
            f"<div style='display:flex;gap:10px;margin-top:14px;padding-top:12px;border-top:1px solid var(--tv-border)'>"
            f"<div style='flex:1;text-align:center;background:var(--tv-bg);border-radius:8px;padding:10px 6px'>"
            f"<div style='color:var(--tv-muted);font-size:9px;text-transform:uppercase;letter-spacing:1px'>Est. baja</div>"
            f"<div style='color:var(--tv-red);font-size:17px;font-weight:900;margin-top:3px'>{fmt(tl)}</div></div>"
            f"<div style='flex:1;text-align:center;background:var(--tv-panel);border-radius:8px;padding:10px 6px;border:1px solid {cons_col}44'>"
            f"<div style='color:var(--tv-muted);font-size:9px;text-transform:uppercase;letter-spacing:1px'>Objetivo</div>"
            f"<div style='color:{cons_col};font-size:19px;font-weight:900;margin-top:3px'>{fmt(tm)}</div>"
            f"<div style='color:{cons_col};font-size:10px'>{upside_pct}</div></div>"
            f"<div style='flex:1;text-align:center;background:var(--tv-bg);border-radius:8px;padding:10px 6px'>"
            f"<div style='color:var(--tv-muted);font-size:9px;text-transform:uppercase;letter-spacing:1px'>Est. alta</div>"
            f"<div style='color:var(--tv-green);font-size:17px;font-weight:900;margin-top:3px'>{fmt(th)}</div></div>"
            f"</div>"
        )

    # ══ BLOQUE 1: DOS GAUGES LADO A LADO ════════════════════════════════════
    left_gauge  = gauge_analistas or "<div style='color:var(--tv-subtle);font-size:12px;padding:20px;text-align:center'>Sin datos de analistas</div>"
    right_gauge = gauge_news      or "<div style='color:var(--tv-subtle);font-size:12px;padding:20px;text-align:center'>Sin noticias</div>"

    st.markdown(
        "<div style='background:var(--tv-panel);border:1px solid var(--tv-border);border-radius:14px;padding:20px;margin-bottom:12px'>"
        # Cabeceras con desplegable ℹ — fuera del grid para que no solapen los SVG
        + "<div style='display:grid;grid-template-columns:1fr 1fr;gap:0;margin-bottom:4px'>"
        + f"<div style='padding-right:20px'>{_section_header('analistas')}</div>"
        + f"<div style='padding-left:20px'>{_section_header('sentimiento')}</div>"
        + "</div>"
        # Grid de los dos gauges
        + "<div style='display:grid;grid-template-columns:1fr 1px 1fr;gap:0;align-items:start'>"
        + f"<div style='padding-right:20px'>{left_gauge}{target_block}</div>"
        + "<div style='background:var(--tv-border);width:1px;align-self:stretch'></div>"
        + "<div style='padding-left:20px'>"
        + right_gauge
        + (f"<div style='margin-top:12px;padding-top:10px;border-top:1px solid var(--tv-border)'>"
           f"<div style='color:var(--tv-subtle);font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Mapa de calor</div>"
           f"<div style='line-height:2.2'>{bubbles}</div></div>" if bubbles else "")
        + "</div>"
        + "</div></div>",
        unsafe_allow_html=True,
    )

    # ══ BLOQUE 2: INSIDERS ══════════════════════════════════════════════════
    if analistas and (analistas.get("ins_buy",0) + analistas.get("ins_sell",0)) > 0:
        a = analistas
        total_ins = a["ins_buy"] + a["ins_sell"]
        ins_pct   = int(a["ins_buy"] / total_ins * 100) if total_ins else 50
        ins_label = "Fuerte compra" if ins_pct>=80 else "Compra" if ins_pct>=62 else "Neutral" if ins_pct>=45 else "Venta" if ins_pct>=28 else "Fuerte venta"
        ins_col   = "var(--tv-green)" if ins_pct>=62 else "var(--tv-red)" if ins_pct<=38 else "var(--tv-yellow)"
        def fmt_val(v):
            if v >= 1e6: return f"${v/1e6:.1f}M"
            if v >= 1e3: return f"${v/1e3:.0f}K"
            return f"${v:.0f}"
        ins_gauge = _gauge_svg(ins_pct, ins_label, ins_col,
                               uid=f"ins{ticker[:3]}",
                               subtitulo=f"Compras {fmt_val(a['ins_buy'])} · Ventas {fmt_val(a['ins_sell'])}")
        # Métricas agregadas de insiders — filtradas a la sesión de entrada
        ins_rows_all = a.get("ins_rows", [])
        ins_rows = [r for r in ins_rows_all if r["date"] == sesion_iso] if sesion_iso else ins_rows_all
        if not ins_rows:  # fallback si no hay transacciones en esa sesión
            ins_rows = ins_rows_all
        ins_buy_s  = sum(r["val"] for r in ins_rows if r["type"] == "BUY")
        ins_sell_s = sum(r["val"] for r in ins_rows if r["type"] == "SELL")
        n_buy  = sum(1 for r in ins_rows if r["type"] == "BUY")
        n_sell = sum(1 for r in ins_rows if r["type"] == "SELL")
        total_vol = (ins_buy_s + ins_sell_s) or 1
        ratio_buy  = round(ins_buy_s  / total_vol * 100)
        ratio_sell = round(ins_sell_s / total_vol * 100)
        ultima_fecha = ins_rows[0]["date"] if ins_rows else "—"
        # señal neta
        if ratio_buy >= 70:   net_label, net_color, net_icon = "Acumulación fuerte", "#00ff88", "🚀"
        elif ratio_buy >= 50: net_label, net_color, net_icon = "Presión compradora",  "#44dd88", "📈"
        elif ratio_sell >= 70:net_label, net_color, net_icon = "Distribución fuerte", "#ff4444", "🔻"
        else:                 net_label, net_color, net_icon = "Actividad mixta",     "#ffdd44", "⚖️"

        def _ins_card(icon, titulo, valor, sub, bg1, bg2, bdr, col):
            return (
                f"<div style='background:linear-gradient(145deg,{bg1},{bg2});border:1px solid {bdr};"
                f"border-top:3px solid {col};border-radius:14px;padding:16px 14px'>"
                f"<div style='font-size:22px;margin-bottom:8px'>{icon}</div>"
                f"<div style='color:{col};font-size:9px;font-weight:800;text-transform:uppercase;"
                f"letter-spacing:1px;margin-bottom:6px'>{titulo}</div>"
                f"<div style='color:#ffffff;font-size:22px;font-weight:900;letter-spacing:-.5px'>{valor}</div>"
                f"<div style='color:#94a3b888;font-size:11px;margin-top:6px'>{sub}</div>"
                f"</div>"
            )

        # barra buy/sell
        bar_html = (
            f"<div style='margin:14px 0 4px'>"
            f"<div style='display:flex;justify-content:space-between;font-size:10px;"
            f"color:var(--tv-muted);margin-bottom:4px'>"
            f"<span style='color:#00ff88;font-weight:700'>▲ Compras {ratio_buy}%</span>"
            f"<span style='color:#ff4444;font-weight:700'>Ventas {ratio_sell}% ▼</span></div>"
            f"<div style='height:8px;border-radius:6px;overflow:hidden;background:#1e2a3a'>"
            f"<div style='height:100%;width:{ratio_buy}%;background:linear-gradient(90deg,#089981,#00ff88);"
            f"border-radius:6px;transition:width .5s'></div></div></div>"
        )

        cards_ins = (
            _ins_card("💚","Volumen compras", fmt_val(ins_buy_s), f"{n_buy} operaciones",
                      "#071a0f","#0a2416","#1a6640","#00ff88")
            + _ins_card("🔴","Volumen ventas", fmt_val(ins_sell_s), f"{n_sell} operaciones",
                        "#1a0707","#260a0a","#7a1a1a","#ff4444")
            + _ins_card("📅","Última actividad", ultima_fecha, "Fecha más reciente",
                        "#0d1020","#111828","#2a3a5a","#4a9eff")
            + _ins_card(net_icon,"Señal neta", net_label, f"Ratio compra {ratio_buy}% / venta {ratio_sell}%",
                        "#0d100d","#121812","#1a3a2a",net_color)
        )

        st.markdown(
            "<div style='background:var(--tv-panel);border:1px solid var(--tv-border);border-radius:14px;padding:18px 20px;margin-bottom:12px'>"
            + _section_header("insiders")
            + "<div style='display:grid;grid-template-columns:220px 1fr;gap:24px;align-items:start'>"
            + f"<div>{ins_gauge}</div>"
            + f"<div><div style='display:grid;grid-template-columns:repeat(4,1fr);gap:10px'>{cards_ins}</div>{bar_html}</div>"
            + "</div></div>",
            unsafe_allow_html=True,
        )

    # ══ BLOQUE 3: NOTICIAS EN GRID ══════════════════════════════════════════
    if not noticias:
        st.caption("No se encontraron noticias relacionadas con este activo.")
        return

    FUENTES_ICON = {
        "bloomberg":"🟦","yahoo":"🟣","reuters":"🔶","cnbc":"🔵","marketwatch":"🟢",
        "financial times":"🔴","wsj":"⚫","seeking alpha":"🟡","motley fool":"🟠",
        "benzinga":"🟤","barron":"🔷","zacks":"🟩","alphastreet":"🔸","thestreet":"🔹",
    }
    cards_html = "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px'>"
    for n in noticias:
        sc  = n["score"]
        nc  = "var(--tv-green)" if sc>4 else "#84cc16" if sc>0 else "var(--tv-red)" if sc<-4 else "#f97316" if sc<0 else "var(--tv-yellow)"
        sl  = "Alcista" if sc>0 else "Bajista" if sc<0 else "Neutral"
        src = n["fuente"].lower()
        fi  = next((v for k,v in FUENTES_ICON.items() if k in src), "📰")
        lr  = (f"<a href='{n['url']}' target='_blank' style='color:var(--tv-blue);font-size:11px;"
               f"text-decoration:none;font-weight:600'>Leer →</a>" if n["url"] else "")
        tit_es = traducir(n["titulo"], "es") if n["titulo"] else n["titulo"]
        res_es = traducir(n["resumen"], "es") if n["resumen"] else ""
        rh = (f"<div style='color:var(--tv-muted);font-size:12px;margin:6px 0 8px;line-height:1.55;flex:1'>{res_es}…</div>"
              if res_es else "<div style='flex:1'></div>")
        cards_html += (
            f"<div style='background:var(--tv-bg);border:1px solid var(--tv-border);border-radius:12px;"
            f"padding:14px 16px;display:flex;flex-direction:column'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>"
            f"<div style='display:flex;align-items:center;gap:6px'>"
            f"<span style='font-size:15px'>{fi}</span>"
            f"<span style='color:var(--tv-muted);font-size:11px;font-weight:600'>{n['fuente']}</span>"
            f"</div>"
            f"<span style='background:{nc}18;color:{nc};font-size:10px;font-weight:700;"
            f"padding:2px 9px;border-radius:12px;border:1px solid {nc}33'>{sl} {sc:+d}</span>"
            f"</div>"
            f"<div style='color:var(--tv-text);font-size:13px;font-weight:700;line-height:1.45;margin-bottom:4px'>{tit_es}</div>"
            f"{rh}"
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-top:auto;"
            f"padding-top:8px;border-top:1px solid var(--tv-border)'>"
            f"<span style='color:var(--tv-subtle);font-size:10px'>📅 {n['fecha']}</span>{lr}"
            f"</div></div>"
        )
    cards_html += "</div>"
    st.markdown(
        "<div style='background:var(--tv-panel);border:1px solid var(--tv-border);border-radius:14px;padding:18px 20px;margin-bottom:12px'>"
        + _section_header("noticias")
        + cards_html
        + "</div>",
        unsafe_allow_html=True,
    )

def analizar_ticker(ticker):
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        if df is None or len(df) < sr_period + 10:
            return None

        # Eliminar velas incompletas (sesión abierta → NaN en OHLC)
        df = df.dropna(subset=["Close", "High", "Low", "Open"])
        if len(df) < sr_period + 10:
            return None

        close  = df["Close"]
        high   = df["High"]
        low    = df["Low"]
        volume = df["Volume"]

        k, d    = stochastic(high, low, close, stoch_k, stoch_d)
        vol_ma  = volume.rolling(vol_period).mean()
        soporte = low.rolling(sr_period).min()
        resis   = high.rolling(sr_period).max()
        mom     = roc(close, roc_period)

        c1 = bool(k.iloc[-1] < oversold)
        c2 = cruce_reciente_up(k, d, int(cruce_ventana))
        # Forex, índices (^) y crypto no reportan volumen OTC — ignorar filtro C3
        es_sin_volumen = ticker.endswith("=X") or ticker.endswith("-USD") or ticker.startswith("^")
        c3 = True if es_sin_volumen else float(volume.iloc[-1]) > float(vol_ma.iloc[-1]) * vol_mult
        c4 = float(mom.iloc[-1]) > roc_min
        c5 = float(close.iloc[-1]) > float(soporte.iloc[-1])

        # Gatillo de activación — última sesión cerrada (viernes si hoy es sábado)
        vela_alcista   = float(close.iloc[-1]) > float(df["Open"].iloc[-1])
        gatillo_precio = float(high.iloc[-1])

        # Aplica solo los filtros activos (checkboxes sidebar)
        filtros_activos = (
            (c1 or not fil_c1) and
            (c2 or not fil_c2) and
            (c3 or not fil_c3) and
            (c4 or not fil_c4) and
            (c5 or not fil_c5)
        )
        entrada = filtros_activos
        cond_ok = sum([c1, c2, c3, c4, c5])

        c_res  = float(close.iloc[-1]) >= float(resis.iloc[-1])
        c_sob  = k.iloc[-1] > overbought and cruce_reciente_down(k, d, int(cruce_ventana))
        salida = c_res or c_sob

        # ── Señal SHORT — desactivada (solo largo) ──────────────────────────
        es_shortable=False
        s1=s2=s3=s4=s5=s6=False
        short_cond_ok=0; short_signal=False; gatillo_short=0.0

        # ── Fibonacci: 52 semanas en diario, rango del período en intradiario ──
        precio_actual = float(close.iloc[-1])
        _es_intraday = interval in ("4h", "1h", "15m", "5m")
        try:
            if _es_intraday:
                # En intradiario usamos el rango ya descargado
                swing_high = float(high.max())
                swing_low  = float(low.min())
            else:
                df_hist = yf.Ticker(ticker).history(period="1y", interval="1d")
                swing_high = float(df_hist["High"].max()) if df_hist is not None and not df_hist.empty else float(high.max())
                swing_low  = float(df_hist["Low"].min())  if df_hist is not None and not df_hist.empty else float(low.min())
        except Exception:
            swing_high = float(high.max())
            swing_low  = float(low.min())
        rango_fib = swing_high - swing_low

        FIB_NIVELES = {
            "0%":    swing_high,
            "23.6%": swing_high - rango_fib * 0.236,
            "38.2%": swing_high - rango_fib * 0.382,
            "50%":   swing_high - rango_fib * 0.500,
            "61.8%": swing_high - rango_fib * 0.618,
            "78.6%": swing_high - rango_fib * 0.786,
            "100%":  swing_low,
        }

        # Retroceso actual = % de caída desde el máximo del período (intuitivo)
        # Ej: precio 80 con máximo 142 → cayó un 43.3% desde el máximo
        # Retroceso Fibonacci real: % caída desde el máximo DENTRO del rango (0%=máximo, 100%=mínimo)
        retroceso_pct = ((swing_high - precio_actual) / rango_fib * 100) if rango_fib > 0 else 0
        retroceso_pct = max(0.0, min(100.0, retroceso_pct))

        # Nivel Fibonacci de precio más cercano al precio actual
        nivel_mas_cercano = min(FIB_NIVELES, key=lambda n: abs(FIB_NIVELES[n] - precio_actual))

        # Score Fibonacci: 100 cuando el precio está en el nivel 50% Fibonacci (precio medio del rango)
        # Se degrada proporcionalmente según la distancia al nivel 50% en términos de precio
        fib_50_precio = FIB_NIVELES["50%"]
        dist_precio   = abs(precio_actual - fib_50_precio)
        umbral        = rango_fib * 0.50  # mitad del rango = score 0 en los extremos

        if umbral > 0:
            fib_score = max(0.0, round(100 - (dist_precio / umbral) * 100, 1))
        else:
            fib_score = 0.0

        fib_score = round(fib_score, 1)

        # Score combinado: señal técnica (60%) + fibonacci (40%)
        score_tecnico  = (cond_ok / 5) * 100
        score_total    = round(score_tecnico * 0.60 + fib_score * 0.40, 1)

        ultima_sesion = df.index[-1]
        if hasattr(ultima_sesion, "tz_localize"):
            ultima_sesion = ultima_sesion
        ultima_sesion_str = pd.Timestamp(ultima_sesion).strftime("%d/%m/%Y")
        ultima_sesion_iso = pd.Timestamp(ultima_sesion).strftime("%Y-%m-%d")

        return {
            "Ticker":           ticker,
            "📈":               tradingview_url(ticker),
            "Última sesión":    ultima_sesion_str,
            "Última sesión ISO": ultima_sesion_iso,
            "Precio":           round(precio_actual, 2),
            "K":                round(float(k.iloc[-1]), 2),
            "D":                round(float(d.iloc[-1]), 2),
            "Vol/MA":           round(float(volume.iloc[-1]) / float(vol_ma.iloc[-1]), 2) if float(vol_ma.iloc[-1]) > 0 else 0.0,
            "ROC%":             round(float(mom.iloc[-1]), 2),
            "Soporte":          round(float(soporte.iloc[-1]), 2),
            "Resistencia":      round(float(resis.iloc[-1]), 2),
            "K<umbral":         c1,
            "Cruce K>D":        c2,
            "Vol>MA":           c3,
            "ROC ok":           c4,
            "Close>Sop":        c5,
            "VelaAnterior🕯️":  "🟢 Alcista" if vela_alcista else "🔴 Bajista",
            "Gatillo💥":        round(gatillo_precio, 4),
            "Cond.OK":          cond_ok,
            "🎯 BUY":           entrada,
            "🔴 SELL":          salida,
            "📉 SHORT":         short_signal,
            "_es_shortable":    es_shortable,
            "_short_cond_ok":   short_cond_ok,
            "_s1": s1, "_s2": s2, "_s4": s4, "_s5": s5,
            "_gatillo_short":   round(gatillo_short, 2),
            # Fibonacci
            "_swing_high":      round(swing_high, 2),
            "_swing_low":       round(swing_low, 2),
            "_fib_niveles":     {k: round(v, 2) for k, v in FIB_NIVELES.items()},
            "_retroceso_pct":   round(retroceso_pct, 1),
            "_nivel_cercano":   nivel_mas_cercano,
            "_fib_score":       fib_score,
            "_score_tecnico":   round(score_tecnico, 1),
            "_score_total":     score_total,
        }
    except Exception:
        return None

# ── Escanear ──────────────────────────────────────────────────────────────────
if not tickers_all:
    st.warning("Selecciona al menos un mercado o añade tickers personalizados.")
    st.stop()

if st.button(T["escanear"], type="primary", width="stretch"):
    resultados = []
    bar  = st.progress(0)
    stat = st.empty()

    for i, ticker in enumerate(tickers_all):
        stat.text(f"{T['analizando']} {ticker}... ({i+1}/{len(tickers_all)})")
        r = analizar_ticker(ticker)
        if r:
            r["_es_custom"] = ticker in custom_tickers
            resultados.append(r)
        bar.progress((i + 1) / len(tickers_all))

    stat.empty()
    bar.empty()
    st.session_state["df_res_cache"] = resultados
    st.session_state.filtro_activo = "todos"

if "df_res_cache" not in st.session_state or not st.session_state["df_res_cache"]:
    st.stop()

resultados = st.session_state["df_res_cache"]

if not resultados:
    st.error("No se obtuvieron datos.")
    st.stop()

df_res = pd.DataFrame(resultados)

# Si hay filtros desactivados, forzar vista "todos" y avisar
_filtros_desactivados = not (fil_c1 and fil_c2 and fil_c3 and fil_c4 and fil_c5)
if _filtros_desactivados:
    st.session_state.filtro_activo = "todos"
    _fil_names = [n for n, a in [("C1 K<umbral", fil_c1), ("C2 Cruce K>D", fil_c2),
                                   ("C3 Vol>MA", fil_c3), ("C4 ROC", fil_c4),
                                   ("C5 Precio>Sop", fil_c5)] if not a]
    st.info(f"⚠️ Filtros desactivados: **{', '.join(_fil_names)}** — mostrando todos los tickers para que puedas revisar el informe de cada uno.")

# ── Botones de filtro ─────────────────────────────────────────────────────
buys   = int(df_res["🎯 BUY"].sum())
sells  = int(df_res["🔴 SELL"].sum())
shorts = int(df_res["📉 SHORT"].sum()) if "📉 SHORT" in df_res.columns else 0
parc   = int((df_res["Cond.OK"] >= 3).sum())
total  = len(df_res)

if "filtro_activo" not in st.session_state:
    st.session_state.filtro_activo = "todos"
if "ticker_detalle" not in st.session_state:
    st.session_state.ticker_detalle = None

FILTROS = [
    ("todos",    "Total analizados",    total,  "#2962ff"),
    ("buy",      "BUY — Momento Dulce", buys,   "#089981"),
    ("sell",     "SELL salida largo",   sells,  "#ff8844"),
    ("parciales","Parciales (≥3/5)",    parc,   "#f5c518"),
]

ICONOS = {"todos": "📊", "buy": "🎯", "sell": "🔴", "parciales": "⚠️"}

cols_f = st.columns(4)
for i, (key, label, val, accent) in enumerate(FILTROS):
    activo = st.session_state.filtro_activo == key
    fondo  = accent + "22" if activo else "var(--tv-panel)"
    borde  = accent        if activo else "var(--tv-border2)"
    icono  = ICONOS[key]
    badge  = ('<span style="background:' + accent + ';color:#000;font-size:9px;font-weight:800;'
              'padding:2px 8px;border-radius:10px;letter-spacing:.5px">● ACTIVO</span>'
              if activo else
              '<span style="color:var(--tv-subtle);font-size:10px">Filtrar →</span>')
    with cols_f[i]:
        st.markdown(
            f"<div id='wrap-fbtn-{key}' style='position:relative'>"
            f"<div style='background:{fondo};border:2px solid {borde};border-radius:10px;"
            f"padding:20px 20px 16px 20px;transition:all .2s;"
            f"background-image:linear-gradient(135deg,{fondo},{accent}08)'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px'>"
            f"<span style='font-size:22px'>{icono}</span>"
            f"{badge}"
            f"</div>"
            f"<div style='color:{accent};font-size:36px;font-weight:900;line-height:1;letter-spacing:-1px'>{val}</div>"
            f"<div style='color:var(--tv-muted);font-size:11px;font-weight:600;text-transform:uppercase;"
            f"letter-spacing:.6px;margin-top:6px'>{label}</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button(" ", key=f"fbtn_{key}", width="stretch"):
            st.session_state.filtro_activo = key
            st.rerun()
        st.markdown(
            f"<style>"
            f"div[data-testid='stVerticalBlock']:has(#wrap-fbtn-{key}) button[kind='secondary']"
            f"{{position:absolute;inset:0;opacity:0;cursor:pointer;border:none;"
            f"border-radius:10px;margin-top:-116px;height:116px}}"
            f"</style>",
            unsafe_allow_html=True,
        )

fa = st.session_state.filtro_activo

# Columnas visibles Fibonacci (antes del filtro para que df_view las herede)
df_res["Fib%"]       = df_res["_retroceso_pct"]
df_res["NivelFib"]   = df_res["_nivel_cercano"]
df_res["FibScore"]   = df_res["_fib_score"]
df_res["ScoreTotal"] = df_res["_score_total"]

# ── Aplicar filtro (los tickers manuales siempre se incluyen) ────────────
_custom_mask = df_res["_es_custom"] if "_es_custom" in df_res.columns else pd.Series(False, index=df_res.index)

if fa == "buy":
    df_view = df_res[df_res["🎯 BUY"] | _custom_mask].copy()
elif fa == "short":
    _short_mask = df_res["📉 SHORT"] if "📉 SHORT" in df_res.columns else pd.Series(False, index=df_res.index)
    df_view = df_res[_short_mask | _custom_mask].copy()
elif fa == "sell":
    df_view = df_res[df_res["🔴 SELL"] | _custom_mask].copy()
elif fa == "parciales":
    df_view = df_res[(df_res["Cond.OK"] >= 3) | _custom_mask].copy()
else:
    df_view = df_res.copy()

# BUY primero → mayor score total → más condiciones OK
df_view = df_view.sort_values(
    by=["🎯 BUY", "ScoreTotal", "Cond.OK"],
    ascending=[False, False, False],
).reset_index(drop=True)
df_view.index = df_view.index + 1

# ── Tabla ─────────────────────────────────────────────────────────────────
BOOL_COLS = ["K<umbral", "Cruce K>D", "Vol>MA", "ROC ok", "Close>Sop", "🎯 BUY", "📉 SHORT", "🔴 SELL"]

def fmt(val):
    if isinstance(val, bool):
        return "✅" if val else "❌"
    return val

def highlight(row):
    buy   = row.get("🎯 BUY")    == "✅"
    short = row.get("📉 SHORT")  == "✅"
    sell  = row.get("🔴 SELL")   == "✅"
    ok    = row.get("Cond.OK", 0)
    n     = len(row)
    if buy:
        return ["background-color:#0d3b1e;color:#00ff88;font-weight:bold"] * n
    if short:
        return ["background-color:#3b0d20;color:#ff6699;font-weight:bold"] * n
    if sell:
        return ["background-color:#3b0d0d;color:#ff6666"] * n
    if isinstance(ok, (int, float)) and ok >= 3:
        return ["background-color:#1c2a1c;color:#99ddaa"] * n
    return ["background-color:#131722;color:#4c525e"] * n

display = df_view.copy()
for col in BOOL_COLS:
    if col in display.columns:
        display[col] = display[col].apply(fmt)

st.subheader(f"📊 Resultados — {len(df_view)} acciones  |  Perfil: {perfil_nombre}")

_col_order_base = ["Ticker", "ScoreTotal", "FibScore", "Fib%", "NivelFib",
                   "Precio", "VelaAnterior🕯️", "Gatillo💥", "K", "D", "Vol/MA", "ROC%",
                   "Soporte", "Resistencia"]
if fil_c1: _col_order_base.append("K<umbral")
if fil_c2: _col_order_base.append("Cruce K>D")
if fil_c3: _col_order_base.append("Vol>MA")
if fil_c4: _col_order_base.append("ROC ok")
if fil_c5: _col_order_base.append("Close>Sop")
_col_order_base += ["Cond.OK", "🎯 BUY", "📉 SHORT", "🔴 SELL", "📈"]
_col_order_base = [c for c in _col_order_base if c in display.columns]

_CTR_COLS = [c for c in ["K<umbral", "Cruce K>D", "Vol>MA", "ROC ok",
             "Close>Sop", "Cond.OK", "🎯 BUY", "📉 SHORT", "🔴 SELL", "📈"] if c in display.columns]

st.dataframe(
    display.style.apply(highlight, axis=1)
           .set_properties(subset=_CTR_COLS, **{"text-align": "center"}),
    width="stretch",
    height=560,
    column_order=_col_order_base,
    column_config={
        "📈": st.column_config.LinkColumn(
            label="📈 Chart", display_text="📈",
            help="Abre el gráfico en TradingView",
        ),
        "ScoreTotal": st.column_config.ProgressColumn(
            label="⭐ Score Total", min_value=0, max_value=100, format="%.1f%%",
            help="Señal técnica (60%) + Fibonacci (40%)",
        ),
        "FibScore": st.column_config.ProgressColumn(
            label="📐 Fib Score", min_value=0, max_value=100, format="%.1f%%",
            help="100% = precio en retroceso 50% Fibonacci",
        ),
        "Precio":        st.column_config.NumberColumn(label="Precio",       format="%.2f"),
        "Soporte":       st.column_config.NumberColumn(label="Soporte",      format="%.2f"),
        "Resistencia":   st.column_config.NumberColumn(label="Resistencia",  format="%.2f"),
        "VelaAnterior🕯️": st.column_config.NumberColumn(label="Vela ant.",  format="%.2f"),
        "Gatillo💥":     st.column_config.NumberColumn(label="Gatillo",      format="%.2f"),
        "K":             st.column_config.NumberColumn(label="K",            format="%.2f"),
        "D":             st.column_config.NumberColumn(label="D",            format="%.2f"),
        "Vol/MA":        st.column_config.NumberColumn(label="Vol/MA",       format="%.2f"),
        "ROC%":          st.column_config.NumberColumn(label="ROC%",         format="%.2f"),
        "Fib%": st.column_config.NumberColumn(label="Retroceso %", format="%.1f%%"),
        "NivelFib": st.column_config.TextColumn(label="Nivel Fib"),
    },
)

# ── Detalle: solo tickers con señal activa (BUY o SHORT) ─────────────────
_has_buy   = "🎯 BUY"   in df_view.columns
_has_short  = "📉 SHORT" in df_view.columns
_custom_view = df_view["_es_custom"] if "_es_custom" in df_view.columns else pd.Series(False, index=df_view.index)
if fa == "todos":
    _mask = pd.Series(False, index=df_view.index)
    if _has_buy:   _mask = _mask | df_view["🎯 BUY"]
    if _has_short: _mask = _mask | df_view["📉 SHORT"]
    _mask = _mask | _custom_view   # manuales siempre en cards
    buy_df = df_view[_mask].sort_values("_score_total", ascending=False)
else:
    buy_df = df_view.sort_values("_score_total", ascending=False)
if not buy_df.empty:
    st.markdown("---")
    st.success(f"### 🎯 {len(buy_df)} {T['buy_titulo']}  [{perfil_nombre}]")
    st.caption(f"{T['informe_fecha']} {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

    # ── Heatmap grid de resultados ────────────────────────────────────────
    n_cols = min(len(buy_df), 5)
    hm_rows = [buy_df.iloc[i:i+n_cols] for i in range(0, len(buy_df), n_cols)]
    for hm_row in hm_rows:
        hm_cols = st.columns(n_cols)
        for ci, (_, hrow) in enumerate(hm_row.iterrows()):
            _t   = hrow["Ticker"]
            _sc  = hrow["_score_total"]
            _pr  = hrow["Precio"]
            _ret = hrow["_retroceso_pct"]
            _niv = hrow["_nivel_cercano"]
            _fund_hm = obtener_fundamentales(_t)
            _nom = (_fund_hm.get("nombre", _t) if _fund_hm else _t)[:18]
            def _lc(c1, c2, t):
                """Interpola entre dos colores hex según t (0=c1, 1=c2)."""
                r = int(int(c1[1:3],16)+(int(c2[1:3],16)-int(c1[1:3],16))*t)
                g = int(int(c1[3:5],16)+(int(c2[3:5],16)-int(c1[3:5],16))*t)
                b = int(int(c1[5:7],16)+(int(c2[5:7],16)-int(c1[5:7],16))*t)
                return f"#{r:02x}{g:02x}{b:02x}"
            if _sc >= 75:
                t = (_sc - 75) / 25.0  # 0 en score=75, 1 en score=100
                _bg1 = _lc("#0a1a0f", "#043d20", t)
                _bg2 = _lc("#0d2a18", "#075c30", t)
                _bdr = _lc("#1a6640", "#00ff88", t)
                _sc_c = _lc("#33aa66", "#00ff88", t)
            elif _sc >= 50:
                t = (_sc - 50) / 25.0  # 0 en score=50, 1 en score=74
                _bg1 = _lc("#0f0e05", "#3d2d00", t)
                _bg2 = _lc("#181408", "#5c4400", t)
                _bdr = _lc("#554400", "#ffdd44", t)
                _sc_c = _lc("#887722", "#ffdd44", t)
            else:
                t = _sc / 50.0  # 0 en score=0, 1 en score=49
                _bg1 = _lc("#0a0805", "#3d1200", t)
                _bg2 = _lc("#12100a", "#5c1e00", t)
                _bdr = _lc("#332211", "#ff8844", t)
                _sc_c = _lc("#664433", "#ff8844", t)
            _bg = f"linear-gradient(145deg,{_bg1},{_bg2})"
            _activo = st.session_state.ticker_detalle == _t
            _bdr2 = "#ffffff" if _activo else _bdr
            _ring = f"box-shadow:0 0 0 3px {_bdr},0 4px 16px {_bdr}44" if _activo else f"box-shadow:0 4px 16px {_bdr}22"
            with hm_cols[ci]:
                st.markdown(
                    f"<div id='hm-wrap-{_t}' style='position:relative'>"
                    f"<div style='background:{_bg};border:2px solid {_bdr2};border-radius:12px;"
                    f"padding:16px 14px;cursor:pointer;{_ring};transition:all .2s'>"
                    f"<div style='color:{_sc_c};font-size:22px;font-weight:900;letter-spacing:-.5px;"
                    f"line-height:1;margin-bottom:4px'>{_t}</div>"
                    f"<div style='color:#ffffffaa;font-size:10px;font-weight:500;margin-bottom:10px;"
                    f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{_nom}</div>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                    f"<div><div style='color:#ffffff99;font-size:9px;text-transform:uppercase;letter-spacing:.5px'>Score</div>"
                    f"<div style='color:{_sc_c};font-size:18px;font-weight:900;line-height:1'>{_sc:.0f}</div></div>"
                    f"<div style='text-align:right'><div style='color:#ffffff99;font-size:9px;text-transform:uppercase;letter-spacing:.5px'>Precio</div>"
                    f"<div style='color:#ffffff;font-size:13px;font-weight:700'>${_pr:.2f}</div></div>"
                    f"</div>"
                    f"<div style='margin-top:8px;background:#ffffff18;border-radius:6px;padding:4px 8px;"
                    f"font-size:10px;color:#ffffffcc;font-weight:600'>Fib {_niv} · {_ret:.1f}%</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
                if st.button(" ", key=f"hmbtn_{_t}", width="stretch"):
                    if st.session_state.ticker_detalle == _t:
                        st.session_state.ticker_detalle = None
                    else:
                        st.session_state.ticker_detalle = _t
                    st.rerun()
                st.markdown(
                    f"<style>"
                    f"div[data-testid='stVerticalBlock']:has(#hm-wrap-{_t}) button[kind='secondary']"
                    f"{{position:absolute;inset:0;opacity:0;cursor:pointer;border:none;"
                    f"border-radius:12px;margin-top:-130px;height:130px}}"
                    f"</style>",
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── Detalle del ticker seleccionado ──────────────────────────────────
    for _, row in buy_df.iterrows():
        url        = tradingview_url(row["Ticker"])
        score_tot  = row["_score_total"]
        fib_score  = row["_fib_score"]
        retroceso  = row["_retroceso_pct"]
        nivel      = row["_nivel_cercano"]
        fibs       = row["_fib_niveles"]
        sh         = row["_swing_high"]
        sl         = row["_swing_low"]
        ticker     = row["Ticker"]
        precio     = row["Precio"]

        if st.session_state.ticker_detalle != ticker:
            continue

        if not _admin:
            st.markdown(
                "<div style='background:#1a1e2e;border:1px solid #2a3550;border-radius:10px;"
                "padding:20px 24px;text-align:center;color:#787b86;font-size:14px'>"
                "🔒 El informe detallado solo está disponible para administradores."
                "</div>",
                unsafe_allow_html=True,
            )
            continue

        score_color = "#00ff88" if score_tot >= 75 else "#ffdd44" if score_tot >= 50 else "#ff8844"

        fund = obtener_fundamentales(ticker)
        nombre_empresa = fund.get("nombre", ticker) if fund else ticker
        sector_txt     = f"{fund['sector']} · {fund['industria']}" if fund else ""

        ultima_ses = row.get("Última sesión", "")

        # Cabecera del detalle con botón cerrar
        st.markdown(
            f"<div style='background:var(--tv-panel);border:1px solid {score_color}44;"
            f"border-top:3px solid {score_color};border-radius:12px;padding:16px 20px;"
            f"margin-bottom:16px;display:flex;justify-content:space-between;align-items:center'>"
            f"<div>"
            f"<span style='color:{score_color};font-size:20px;font-weight:900'>{ticker}</span>"
            f"<span style='color:var(--tv-muted);font-size:13px;margin-left:12px'>${precio}"
            f" · Score {score_tot:.0f}/100 · Fib {nivel} ({retroceso:.1f}%)"
            + (f" · 📅 {ultima_ses}" if ultima_ses else "")
            + f"</span></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button("✕ Cerrar detalle", key=f"close_{ticker}"):
            st.session_state.ticker_detalle = None
            st.rerun()

        if True:

            # ══ CABECERA EMPRESA ══════════════════════════════════════════
            if fund:
                # Valoración propia basada en nuestro sistema de filtros + Fibonacci
                # — Todos los filtros pasan (siempre, ya que aparece en resultados): base 3 ★
                # — Retroceso Fibonacci en zona óptima (38.2%, 50%, 61.8%): +1 ★
                # — Retroceso exactamente en el 50% (±5pp): 5 ★ "Compra fuerte"
                dist_50 = abs(retroceso - 50.0)
                en_zona_optima = (
                    abs(retroceso - 38.2) <= 6 or
                    abs(retroceso - 50.0) <= 8 or
                    abs(retroceso - 61.8) <= 6
                )
                if dist_50 <= 5:
                    rec = "Compra fuerte"
                else:
                    rec = "Compra"

                REC_META = {
                    "Compra fuerte": ("#004d1a", "#00ff66", "⭐⭐⭐⭐⭐", "🏆", 5),
                    "Compra":        ("#1a7a3a", "#44dd88", "⭐⭐⭐⭐✩", "📈", 4),
                }
                rec_bg, rec_glow, rec_stars, rec_icon, rec_n = REC_META.get(
                    rec, REC_META["Compra"]
                )
                rec_color = rec_glow
                desc_orig  = fund.get("_desc_original", "")
                desc_corta = traducir(desc_orig, "es") if (ES and desc_orig) else desc_orig
                desc_corta = desc_corta[:400] if desc_corta else ""

                # Detectar si es commodity/ETF sin datos corporativos
                es_commodity = fund.get("sector", "N/D") == "N/D" and fund.get("industria", "N/D") == "N/D"

                if es_commodity:
                    _tipo_label = "Futuro" if ticker.endswith("=F") else "Divisa" if ticker.endswith("=X") else "ETF / Fondo"
                    _precio_actual = f"{precio:.2f}"
                    st.markdown(
                        "<div style='background:linear-gradient(135deg,#0f172a 60%,#12100a 100%);border:1px solid " + score_color + "44;border-radius:16px;overflow:hidden;margin-bottom:18px;box-shadow:0 0 24px " + score_color + "18'>"
                        + "<div style='height:4px;background:linear-gradient(90deg," + score_color + ",#ffaa33," + score_color + ")'></div>"
                        + "<div style='padding:20px 24px'>"
                        + "<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
                        + "<div>"
                        + "<div style='font-size:22px;font-weight:900;color:#ffffff;margin-bottom:8px'>" + fund.get('nombre', ticker) + "</div>"
                        + "<span style='background:var(--tv-border);color:var(--tv-muted);font-size:11px;padding:3px 10px;border-radius:20px;border:1px solid #334155'>🛢️ " + _tipo_label + "</span>"
                        + "<span style='background:var(--tv-border);color:var(--tv-muted);font-size:11px;padding:3px 10px;border-radius:20px;border:1px solid #334155;margin-left:6px'>🌍 Mercado global</span>"
                        + "<div style='display:flex;gap:24px;margin-top:14px'>"
                        + "<div><div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px'>Precio actual</div><div style='color:" + score_color + ";font-size:18px;font-weight:900'>" + _precio_actual + "</div></div>"
                        + "<div><div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px'>Score señal</div><div style='color:" + score_color + ";font-size:18px;font-weight:900'>" + f"{score_tot:.0f}/100" + "</div></div>"
                        + "<div><div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px'>Retroceso Fib</div><div style='color:#ffdd44;font-size:18px;font-weight:900'>" + f"{retroceso:.1f}%" + "</div></div>"
                        + "</div>"
                        + ("" if not desc_corta else "<div style='background:var(--tv-bg);border-radius:10px;padding:12px 16px;border-left:3px solid " + score_color + "44;margin-top:14px'><div style='color:#cbd5e1;font-size:13px;line-height:1.65'>" + desc_corta + "</div></div>")
                        + "</div>"
                        + "<div style='text-align:center;padding:12px'>"
                        + "<div style='font-size:36px'>🛢️</div>"
                        + "<div style='color:" + score_color + ";font-size:13px;font-weight:700;margin-top:6px'>Sin análisis<br>fundamental</div>"
                        + "</div>"
                        + "</div>"
                        + "</div>"
                        + "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                  st.markdown(
                    "<div style='background:linear-gradient(135deg,#0f172a 60%,#0d1f0f 100%);border:1px solid " + rec_glow + "44;border-radius:16px;overflow:hidden;margin-bottom:18px;box-shadow:0 0 32px " + rec_glow + "18'>"
                    + "<div style='height:4px;background:linear-gradient(90deg," + rec_glow + "," + score_color + "," + rec_glow + ")'></div>"
                    + "<div style='display:flex;align-items:stretch'>"
                    + "<div style='flex:1;padding:22px 24px'>"
                    + "<div style='font-size:22px;font-weight:900;color:#ffffff;letter-spacing:-0.3px;line-height:1.2;margin-bottom:10px'>" + fund['nombre'] + "</div>"
                    + "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px'>"
                    + "<span style='background:var(--tv-border);color:var(--tv-muted);font-size:11px;padding:3px 10px;border-radius:20px;border:1px solid #334155'>🏭 " + fund['sector'] + "</span>"
                    + "<span style='background:var(--tv-border);color:var(--tv-muted);font-size:11px;padding:3px 10px;border-radius:20px;border:1px solid #334155'>" + fund['industria'] + "</span>"
                    + "<span style='background:var(--tv-border);color:var(--tv-muted);font-size:11px;padding:3px 10px;border-radius:20px;border:1px solid #334155'>🌍 " + fund['pais'] + "</span>"
                    + "</div>"
                    + "<div style='display:flex;gap:24px;margin-bottom:16px'>"
                    + "<div><div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px'>Cap. bursátil</div><div style='color:var(--tv-text);font-size:15px;font-weight:700'>" + fund['market_cap'] + "</div></div>"
                    + "<div><div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px'>Dividendo</div><div style='color:var(--tv-text);font-size:15px;font-weight:700'>" + fund['dividend_yield'] + "</div></div>"
                    + "<div><div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px'>Precio obj.</div><div style='color:var(--tv-text);font-size:15px;font-weight:700'>" + fund['target_precio'] + "</div></div>"
                    + "<div><div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px'>Potencial</div><div style='color:" + rec_glow + ";font-size:15px;font-weight:900'>" + fund['upside'] + "</div></div>"
                    + "</div>"
                    + "<div style='background:var(--tv-bg);border-radius:10px;padding:14px 16px;border-left:3px solid " + score_color + "44'>"
                    + "<div style='color:var(--tv-muted);font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>" + T['empresa_label'] + "</div>"
                    + "<div style='color:#cbd5e1;font-size:13px;line-height:1.65'>" + desc_corta + ("…" if len(desc_orig) > 400 else "") + "</div>"
                    + "</div>"
                    + "</div>"
                    + "<div style='width:150px;min-width:150px;background:linear-gradient(180deg," + rec_bg + "cc," + rec_bg + "55);border-left:1px solid " + rec_glow + "33;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px 12px;gap:6px'>"
                    + "<div style='font-size:36px;line-height:1'>" + rec_icon + "</div>"
                    + "<div style='color:#ffffff;font-size:16px;font-weight:900;text-align:center;margin-top:4px'>" + rec + "</div>"
                    + "<div style='color:" + rec_glow + ";font-size:20px;letter-spacing:4px'>" + rec_stars + "</div>"
                    + ""
                    + "</div>"
                    + "</div>"
                    + "</div>",
                    unsafe_allow_html=True,
                  )  # cierre else (no es_commodity)
            else:
                st.markdown(
                    f"""<div style="background:#111827;border-radius:10px;padding:14px 20px;margin-bottom:16px;border-left:4px solid {score_color}">
                    <div style="font-size:18px;font-weight:800;color:#ffffff">{ticker}</div>
                    <div style="color:#6b7280;font-size:13px">Crypto / sin datos fundamentales públicos</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            # ── Última sesión analizada ──────────────────────────────────
            if ultima_ses:
                st.markdown(
                    f"<div style='background:var(--tv-panel);border:1px solid var(--tv-panel);border-radius:8px;"
                    f"padding:8px 16px;margin-bottom:12px;display:inline-block'>"
                    f"<span style='color:var(--tv-muted);font-size:11px;text-transform:uppercase;letter-spacing:1px'>📅 Última sesión analizada&nbsp;&nbsp;</span>"
                    f"<span style='color:var(--tv-blue);font-size:15px;font-weight:800'>{ultima_ses}</span>"
                    f"<span style='color:var(--tv-subtle);font-size:11px;margin-left:10px'>— datos de cierre usados para la señal</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            # ══ ANÁLISIS TÉCNICO NARRATIVO ════════════════════════════════
            st.markdown(T["tec_titulo"])
            narrativa = generar_narrativa(row, oversold, overbought, vol_mult, roc_min, perfil_nombre)
            st.markdown(narrativa)

            # ══ ANÁLISIS FUNDAMENTAL NARRATIVO ═══════════════════════════
            if fund:
                st.markdown(T["fund_titulo"])
                st.markdown(narrativa_fundamental(ticker, fund, precio))

                st.markdown("---")
                # Métricas fundamentales con tooltips explicativos
                HELPS = {
                    "per_t": "📌 PER Trailing (Price-to-Earnings)\nCuántas veces el precio recoge el beneficio de los últimos 12 meses.\n< 15 = barato · 15-25 = razonable · > 25 = exigente",
                    "per_f": "📌 PER Forward\nIgual que el PER trailing pero usando el beneficio estimado del próximo año.\nRefleja las expectativas del mercado. Si es menor que el trailing, se espera crecimiento.",
                    "pb":    "📌 P/Valor Contable (Price-to-Book)\nCompara el precio de mercado con el valor en libros (activos - deudas).\n< 1 = cotiza por debajo de su valor contable · > 3 = prima elevada",
                    "beta":  "📌 Beta\nMide la volatilidad respecto al mercado (S&P500 = 1).\n< 0.8 = defensivo · 0.8-1.2 = similar al mercado · > 1.3 = muy volátil",
                    "roe":   "📌 ROE — Rentabilidad sobre Fondos Propios\nBeneficios generados por cada euro invertido por los accionistas.\n> 15% = empresa eficiente · < 8% = rentabilidad baja",
                    "mn":    "📌 Margen Neto\nPorcentaje de ingresos que queda como beneficio después de todos los gastos e impuestos.\n> 20% = excelente · 10-20% = bueno · < 5% = ajustado",
                    "ri":    "📌 Crecimiento de Ingresos (YoY)\nVariación porcentual de las ventas respecto al mismo período del año anterior.\n> 10% = crecimiento sólido · < 0% = contracción de negocio",
                    "rb":    "📌 Crecimiento de Beneficio (YoY)\nVariación del beneficio neto respecto al año anterior.\nSi crece más que los ingresos, la empresa mejora su eficiencia operativa.",
                    "de":    "📌 Deuda / Equity (Apalancamiento)\nRelación entre la deuda total y los fondos propios.\n< 50 = balance sólido · 50-100 = moderado · > 100 = apalancamiento elevado",
                    "fcf":   "📌 Free Cash Flow (Flujo de Caja Libre)\nDinero que genera la empresa después de pagar sus inversiones.\nPositivo y creciente = empresa sana que puede pagar dividendos, recomprar acciones o invertir.",
                    "div":   "📌 Rentabilidad por Dividendo\nPorcentaje del precio que se recibe como dividendo anual.\n> 4% = rentabilidad alta · 1-3% = moderada · 0% = no reparte dividendo",
                    "obj":   "📌 Precio Objetivo de Analistas\nMedia de los precios objetivo fijados por los analistas que cubren el valor.\nEl potencial mostrado es la diferencia respecto al precio actual.",
                }
                def _fcard(label, value, tooltip, accent=None, badge=None, _uid_prefix="f"):
                    col = accent or "var(--tv-blue)"
                    vcolor = "var(--tv-text)"
                    if value and value != "N/D":
                        if value.startswith("+") or (value.endswith("%") and not value.startswith("-") and not value.startswith("0")):
                            vcolor = "var(--tv-green)"
                        elif value.startswith("-"):
                            vcolor = "var(--tv-red)"
                    badge_html = ""
                    if badge and badge != "N/D":
                        bc = "var(--tv-green)" if "+" in badge else "var(--tv-red)"
                        badge_html = f"<span style='margin-left:8px;background:{bc}22;color:{bc};font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;border:1px solid {bc}44;vertical-align:middle'>{badge}</span>"
                    tooltip_safe = tooltip.replace("<","&lt;").replace(">","&gt;")
                    uid = f"{_uid_prefix}_{ticker}_{label}".replace(" ","_").replace("/","_")
                    info_html = (
                        f"<div style='position:relative;display:inline-block'>"
                        + _tooltip_popup(uid, tooltip_safe, width=270, right=True)
                        + f"</div>"
                    )
                    return (
                        f"<div style='background:var(--tv-panel);border:1px solid var(--tv-border);border-top:2px solid {col};"
                        f"border-radius:8px;padding:14px 16px;position:relative'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px'>"
                        f"<span style='color:var(--tv-muted);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px'>{label}</span>"
                        f"{info_html}"
                        f"</div>"
                        f"<div style='color:{vcolor};font-size:20px;font-weight:800;letter-spacing:-.3px'>{value if value else 'N/D'}{badge_html}</div>"
                        f"</div>"
                    )

                METRICAS = [
                    ("PER trailing",    fund["pe_trailing"],   HELPS["per_t"], "#6366f1"),
                    ("PER forward",     fund["pe_forward"],    HELPS["per_f"], "#8b5cf6"),
                    ("P/Libro",         fund["pb"],            HELPS["pb"],    "#06b6d4"),
                    ("Beta",            fund["beta"],          HELPS["beta"],  "#0ea5e9"),
                    ("ROE",             fund["roe"],           HELPS["roe"],   "var(--tv-green)"),
                    ("Margen neto",     fund["margen_neto"],   HELPS["mn"],    "var(--tv-green)"),
                    ("Crec. ingresos",  fund["rev_growth"],    HELPS["ri"],    "#84cc16"),
                    ("Crec. beneficio", fund["earn_growth"],   HELPS["rb"],    "#84cc16"),
                    ("Deuda/Equity",    fund["debt_equity"],   HELPS["de"],    "#f97316"),
                    ("Free Cash Flow",  fund["free_cashflow"], HELPS["fcf"],   "#22d3ee"),
                    ("Dividendo",       fund["dividend_yield"],HELPS["div"],   "#a78bfa"),
                    ("Obj. analistas",  fund["target_precio"], HELPS["obj"],   "var(--tv-blue)",
                     f"{fund['upside']}" if fund["upside"] != "N/D" else None),
                ]

                rows = [METRICAS[i:i+4] for i in range(0, len(METRICAS), 4)]
                for row_m in rows:
                    cols = st.columns(4)
                    for ci, item in enumerate(row_m):
                        badge = item[4] if len(item) > 4 else None
                        cols[ci].markdown(
                            _fcard(item[0], item[1], item[2], item[3], badge),
                            unsafe_allow_html=True,
                        )

            st.markdown("---")

            # ══ NOTICIAS + SENTIMIENTO ════════════════════════════════════
            st.markdown("### 📰 Análisis de mercado · Noticias & Sentimiento")
            with st.spinner("Cargando noticias y datos de analistas…"):
                _nombre_emp = fund.get("nombre", ticker) if fund else ticker
                noticias   = obtener_noticias(ticker, _nombre_emp)
                analistas  = obtener_analistas_insiders(ticker)
            render_noticias_sentimiento(ticker, noticias, analistas, score_color, row.get("Última sesión ISO",""))

            st.markdown("---")

            # Gráfico TradingView embebido + botón
            tv_sym = tradingview_url(row["Ticker"]).split("symbol=")[-1].split("&")[0]
            st.components.v1.html(
                f"""<div style="border-radius:10px;overflow:hidden;">
                <iframe
                  src="https://www.tradingview.com/widgetembed/?frameElementId=tv_chart_{row['Ticker'].replace('-','_')}&symbol={tv_sym}&interval=D&hidesidetoolbar=1&hidetoptoolbar=0&theme=dark&style=1&timezone=exchange&withdateranges=1&showpopupbutton=1&studies=[]&locale=es"
                  style="width:100%;height:400px;border:none;"
                  allowtransparency="true"
                  allowfullscreen=""
                ></iframe></div>""",
                height=410,
            )
            st.markdown(
                f'<a href="{url}" target="_blank" style="'
                'display:inline-block;background:#1a3a5c;color:#4a9eff;'
                'padding:6px 16px;border-radius:6px;text-decoration:none;'
                'font-weight:600;font-size:14px;margin-bottom:14px;">'
                f'📈 Ver {row["Ticker"]} en TradingView ↗</a>',
                unsafe_allow_html=True,
            )

            # ── Gatillo de activación ────────────────────────────────────
            gatillo_val    = row["Gatillo💥"]
            vela_prev_txt  = row["VelaAnterior🕯️"]
            es_alcista     = "Alcista" in vela_prev_txt
            gatillo_color  = "#00ff88" if es_alcista else "#ffaa33"
            gatillo_estado = "✅ Vela anterior ALCISTA — gatillo activo" if es_alcista else "⏳ Vela anterior BAJISTA — espera vela alcista para activar"
            st.markdown(
                f"""<div style="background:#0a0a0a;border:2px solid {gatillo_color};border-radius:8px;
                padding:12px 18px;margin-bottom:12px">
                <div style="color:{gatillo_color};font-size:13px;font-weight:700;margin-bottom:4px">
                💥 GATILLO DE ACTIVACIÓN</div>
                <div style="color:#ffffff;font-size:15px;font-weight:800">
                Entrada cuando precio supere: <span style="color:{gatillo_color}">{gatillo_val:.2f}</span>
                &nbsp;(máximo vela anterior)</div>
                <div style="color:#aaaaaa;font-size:12px;margin-top:4px">{gatillo_estado}</div>
                <div style="color:#666666;font-size:11px;margin-top:6px">
                ⚠️ El scanner detecta la señal técnica — la entrada real se confirma cuando el precio
                rompa el máximo de una vela diaria alcista cerrada. Hasta entonces, la señal está en espera.
                </div></div>""",
                unsafe_allow_html=True,
            )

            # ── Score general ─────────────────────────────────────────────
            st.markdown(
                f"""<div style="background:#111;border-radius:10px;padding:14px 18px;margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                  <span style="color:#cccccc;font-size:14px">⭐ SCORE TOTAL DE LA SEÑAL</span>
                  <span style="color:{score_color};font-size:26px;font-weight:800">{score_tot:.0f} / 100</span>
                </div>
                <div style="background:#333;border-radius:4px;height:10px">
                  <div style="background:{score_color};width:{score_tot}%;height:10px;border-radius:4px"></div>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:#888">
                  <span>Señal técnica ({row['_score_tecnico']:.0f}/100) × 60%</span>
                  <span>Fibonacci ({fib_score:.0f}/100) × 40%</span>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

            # ── Señal técnica con tooltips ────────────────────────────────
            HELPS_TEC = {
                "k":    f"📌 Estocástico K ({stoch_k} períodos)\nOscilador de momentum entre 0-100.\n< {oversold} = zona de sobreventa donde se buscan rebotes alcistas.\nUn valor bajo + cruce al alza de D = señal de entrada.",
                "vol":  f"📌 Volumen relativo (Volumen actual ÷ Media {vol_period} períodos)\n> 1.0x = por encima de la media habitual.\nConfirma que hay interés real detrás del movimiento.\nUmbral mínimo configurado: {vol_mult:.0%}x",
                "roc":  f"📌 ROC — Rate of Change ({roc_period} períodos)\nMide el % de cambio del precio respecto a N velas atrás.\n> 0% = momentum positivo, el precio sube.\n> {roc_min}% = umbral mínimo configurado.",
                "sop":  f"📌 Soporte estructural (mínimo de {sr_period} velas)\nNivel de precio donde históricamente el mercado ha encontrado compradores.\nEl precio debe estar por encima para confirmar la señal.",
                "res":  f"📌 Resistencia estructural (máximo de {sr_period} velas)\nNivel de precio donde históricamente el mercado ha encontrado vendedores.\nEs el objetivo natural del movimiento alcista.",
                "prec": "📌 Precio actual de cierre\nÚltimo precio de cierre disponible. Es el precio de referencia para calcular la entrada y los niveles del patrón de trade.",
            }
            def _tcard(label, value, help_txt, accent, badge=None):
                badge_html = ""
                if badge:
                    badge_html = (f"<div style='margin-top:6px;display:inline-block;"
                                  f"background:{accent}22;color:{accent};font-size:10px;"
                                  f"font-weight:700;padding:3px 10px;border-radius:10px;"
                                  f"border:1px solid {accent}44'>↑ {badge}</div>")
                help_safe = help_txt.replace("<","&lt;").replace(">","&gt;")
                uid = f"t_{ticker}_{label}".replace(" ","_").replace("/","_")
                info = (
                    f"<div style='position:relative;display:inline-block'>"
                    + _tooltip_popup(uid, help_safe, width=260)
                    + f"</div>"
                )
                return (
                    f"<div style='background:var(--tv-panel);border:1px solid var(--tv-border);"
                    f"border-top:3px solid {accent};border-radius:8px;padding:14px 16px'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>"
                    f"<span style='color:var(--tv-muted);font-size:10px;font-weight:700;"
                    f"text-transform:uppercase;letter-spacing:.6px'>{label}</span>"
                    f"{info}</div>"
                    f"<div style='color:{accent};font-size:22px;font-weight:900;letter-spacing:-.3px'>{value}</div>"
                    f"{badge_html}</div>"
                )

            k_val   = row['K']
            vol_val = row['Vol/MA']
            roc_val = row['ROC%']
            k_col   = "#089981" if k_val < oversold   else "#f23645"
            vol_col = "#089981" if vol_val >= vol_mult else "#f97316"
            roc_col = "#089981" if roc_val >= roc_min  else "#f97316"

            ta, tb, tc = st.columns(3)
            ta.markdown(_tcard("K Estocástico", f"{k_val:.1f}",       HELPS_TEC["k"],   k_col,   f"< {oversold} ✅"), unsafe_allow_html=True)
            tb.markdown(_tcard("Vol / MA Vol",  f"{vol_val:.2f}x",    HELPS_TEC["vol"], vol_col, f"> {vol_mult:.0%} ✅"), unsafe_allow_html=True)
            tc.markdown(_tcard("ROC Momentum",  f"{roc_val:.2f}%",    HELPS_TEC["roc"], roc_col, f"> {roc_min}% ✅"), unsafe_allow_html=True)
            ta.markdown(_tcard("Soporte",       f"{row['Soporte']:.2f}",     HELPS_TEC["sop"],  "#6366f1"), unsafe_allow_html=True)
            tb.markdown(_tcard("Resistencia",   f"{row['Resistencia']:.2f}", HELPS_TEC["res"],  "#f59e0b"), unsafe_allow_html=True)
            tc.markdown(_tcard("Precio actual", f"{row['Precio']:.2f}",      HELPS_TEC["prec"], "#06b6d4"), unsafe_allow_html=True)

            # ── Fibonacci ─────────────────────────────────────────────────
            st.markdown("---")
            st.markdown(
                f"**📐 Análisis Fibonacci** — Retroceso desde máximo histórico del período"
            )
            st.caption(
                "📅 Referencia: máximo y mínimo de las últimas **52 semanas** (1 año). "
                "Es el estándar en swing trading en gráfico diario — captura el ciclo completo "
                "de precio reciente sin distorsiones de mínimos históricos lejanos. "
                "El nivel óptimo de entrada es el retroceso del **50%** dentro de ese rango, "
                "donde compradores y vendedores están en máximo equilibrio."
            )

            # Barra visual de retroceso
            fib_bar_color = "#00ff88" if 40 <= retroceso <= 60 else \
                            "#ffdd44" if 30 <= retroceso <= 70 else "#ff8844"
            st.markdown(
                f"""<div style="background:#1a1a1a;border-radius:8px;padding:12px 16px;margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                  <span style="color:#888;font-size:12px">Swing Low ({sl:.2f})</span>
                  <span style="color:{fib_bar_color};font-size:14px;font-weight:700">
                    Retroceso actual: {retroceso:.1f}%
                  </span>
                  <span style="color:#888;font-size:12px">Swing High ({sh:.2f})</span>
                </div>
                <div style="position:relative;background:#2a2a2a;border-radius:4px;height:18px;margin-bottom:8px">
                  <div style="position:absolute;left:{retroceso:.1f}%;top:0;width:3px;height:18px;background:{fib_bar_color};border-radius:2px"></div>
                  <div style="position:absolute;left:23.6%;top:0;width:2px;height:18px;background:#555"></div>
                  <div style="position:absolute;left:38.2%;top:0;width:2px;height:18px;background:#666"></div>
                  <div style="position:absolute;left:50%;top:0;width:2px;height:18px;background:#aaa"></div>
                  <div style="position:absolute;left:61.8%;top:0;width:2px;height:18px;background:#666"></div>
                  <div style="position:absolute;left:78.6%;top:0;width:2px;height:18px;background:#555"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:11px;color:#666">
                  <span>0%</span><span>23.6%</span><span>38.2%</span>
                  <span style="color:#ffffff;font-weight:700">50% ★</span>
                  <span>61.8%</span><span>78.6%</span><span>100%</span>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

            # Tabla de niveles Fibonacci
            fib_cols = st.columns(len(fibs))
            for idx, (nivel_name, nivel_precio) in enumerate(fibs.items()):
                es_cercano  = nivel_name == nivel
                es_optimo   = nivel_name == "50%"
                # Score por proximidad al 50% Fib: verde en centro, rojo en extremos
                _dist_frac = {"0%": 1.0, "23.6%": 0.528, "38.2%": 0.236,
                              "50%": 0.0, "61.8%": 0.236, "78.6%": 0.572, "100%": 1.0}
                _blk_score = max(0, 100 - _dist_frac.get(nivel_name, 1.0) * 100)
                # Color continuo: rojo(0) → naranja(50) → verde(100) via HSL hue 0→120
                _hue = int(_blk_score * 1.2)   # 0→red, 60→yellow, 120→green
                _sat = 80
                _lit_bg  = 12
                _lit_txt = 55
                _bg_col  = f"hsl({_hue},{_sat}%,{_lit_bg}%)"
                _txt_col = f"hsl({_hue},{_sat}%,{_lit_txt}%)"
                marcador = " ★" if es_optimo else ""
                _border = f"border:1.5px solid hsl({_hue},{_sat}%,35%);" if es_cercano else ""
                fib_cols[idx].markdown(
                    f"""<div style="background:{_bg_col};border-radius:6px;padding:8px 4px;
                    text-align:center;{_border}">
                    <div style="color:{_txt_col};font-size:12px;font-weight:700">{nivel_name}{marcador}</div>
                    <div style="color:#cccccc;font-size:11px">{nivel_precio:.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            # Score Fibonacci detallado
            _score_color = "#00cc44" if fib_score >= 75 else "#ff8c00" if fib_score >= 40 else "#ff3333"
            _fib50_precio = fibs.get("50%", 0)
            st.markdown(
                f"""<div style="background:#111;border-radius:8px;padding:14px 16px;margin-top:10px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                  <span style="color:#cccccc;font-size:13px;font-weight:700">📐 Fibonacci Score</span>
                  <span style="color:{_score_color};font-size:22px;font-weight:900">{fib_score:.0f} / 100</span>
                </div>
                <div style="position:relative;background:linear-gradient(90deg,#550000,#885500,#006600);border-radius:4px;height:10px;margin-bottom:10px">
                  <div style="position:absolute;left:calc({fib_score:.0f}% - 5px);top:-3px;width:10px;height:16px;
                       background:{_score_color};border-radius:3px;box-shadow:0 0 6px {_score_color}"></div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:4px">
                  <div style="background:#1a0000;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#ff3333;font-size:11px;font-weight:700">🔴 Zona fría</div>
                    <div style="color:#888;font-size:10px;margin-top:2px">0% o 100% Fib<br>Extremos del rango<br>Score 0–25</div>
                  </div>
                  <div style="background:#1a1000;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#ff8c00;font-size:11px;font-weight:700">🟠 Zona media</div>
                    <div style="color:#888;font-size:10px;margin-top:2px">23.6% o 78.6% Fib<br>Rebote posible<br>Score 25–65</div>
                  </div>
                  <div style="background:#001a00;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#00cc44;font-size:11px;font-weight:700">🟢 Zona ideal</div>
                    <div style="color:#888;font-size:10px;margin-top:2px">38.2% – 61.8% Fib<br>Máxima probabilidad<br>Score 65–100</div>
                  </div>
                </div>
                <div style="color:#555;font-size:10px;margin-top:8px;border-top:1px solid #222;padding-top:8px;text-align:center">
                  Score 100 = precio exactamente en el nivel 50% Fibonacci ({_fib50_precio:.2f}) — punto de máximo equilibrio entre compradores y vendedores dentro del rango del último año.
                  El score baja cuanto más se aleja el precio de ese nivel óptimo.
                  Precio actual: <span style="color:#aaa">{precio:.2f}</span>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

            # ── Patrón de Trade + Códigos ─────────────────────────────────
            st.markdown("---")
            _es_short_row = bool(row.get("📉 SHORT", False)) and not bool(row.get("🎯 BUY", False))
            if _es_short_row:
                tr = calcular_trade_short(
                    row["_gatillo_short"] if row.get("_gatillo_short", 0) > 0 else row["Precio"],
                    row["Resistencia"],
                    row["_swing_high"], row["_swing_low"]
                )
            else:
                tr = calcular_trade(
                    row["Gatillo💥"], row["Soporte"],
                    row["_swing_high"], row["_swing_low"]
                )

            # Generar todos los códigos
            import json as _json
            trade_json = _json.dumps({
                "ticker": ticker,
                "fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "perfil": perfil_nombre,
                "score_total": row["_score_total"],
                "entrada": tr["entrada"],
                "stop_loss": tr["sl"],
                "riesgo_pct": tr["riesgo_pct"],
                "take_profit": {
                    "tp1": {"precio": tr["tp1"], "size_pct": 50, "rr": tr["rr1"], "criterio": "Fib 38.2% del recorrido entrada→máximo"},
                    "tp2": {"precio": tr["tp2"], "size_pct": 30, "rr": tr["rr2"], "criterio": "Fib 61.8% del recorrido entrada→máximo"},
                    "tp3": {"precio": tr["tp3"], "size_pct": 20, "rr": tr["rr3"], "criterio": "Máximo histórico — cierra el 100% de la posición"},
                },
                "fibonacci": {
                    "swing_high": row["_swing_high"], "swing_low": row["_swing_low"],
                    "retroceso_pct": row["_retroceso_pct"],
                    "nivel_cercano": row["_nivel_cercano"],
                    "niveles": row["_fib_niveles"],
                },
            }, indent=2, ensure_ascii=False)

            def _mql_header(plat):
                return [
                    f"// Momento Dulce — {ticker} | {plat}",
                    f"// Generado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} | Score: {row['_score_total']:.0f}/100",
                    "#property strict", "",
                    f'string SYMBOL    = "{ticker}";',
                    f"double ENTRADA   = {tr['entrada']};",
                    f"double SL        = {tr['sl']};",
                    f"double TP1       = {tr['tp1']};  // 50%  Fib 38.2% recorrido  R:R {tr['rr1']:.1f}x",
                    f"double TP2       = {tr['tp2']};  // 30%  Fib 61.8% recorrido  R:R {tr['rr2']:.1f}x",
                    f"double TP3       = {tr['tp3']};  // 20%  Máximo histórico      R:R {tr['rr3']:.1f}x",
                    "double LOT_SIZE  = 0.1;",
                    "int    MAGIC     = 20250101;",
                    f'string COMMENT   = "MD_{ticker}";', "",
                ]

            mql4 = "\n".join(_mql_header("MetaTrader 4") + [
                "int OnInit() { return INIT_SUCCEEDED; }",
                "void OnStart()",
                "{",
                "   double lot1 = NormalizeDouble(LOT_SIZE*0.500, 2);",
                "   double lot2 = NormalizeDouble(LOT_SIZE*0.286, 2);",
                "   double lot3 = NormalizeDouble(LOT_SIZE*0.214, 2);",
                "   int digits  = (int)MarketInfo(SYMBOL, MODE_DIGITS);",
                "",
                "   // Orden 1 — TP1 (50%) Fib 50% recuperación",
                "   int t1 = OrderSend(SYMBOL, OP_BUYSTOP, lot1, ENTRADA, 3,",
                '             NormalizeDouble(SL,digits), NormalizeDouble(TP1,digits), COMMENT+"_TP1", MAGIC, 0, clrGreen);',
                "   // Orden 2 — TP2 (28.6%) Máx histórico  →  acumulado 78.6% liquidado",
                "   int t2 = OrderSend(SYMBOL, OP_BUYSTOP, lot2, ENTRADA, 3,",
                '             NormalizeDouble(SL,digits), NormalizeDouble(TP2,digits), COMMENT+"_TP2", MAGIC, 0, clrGreen);',
                "   // Orden 3 — TP3 (21.4%) Ext. Fib 38.2%",
                "   int t3 = OrderSend(SYMBOL, OP_BUYSTOP, lot3, ENTRADA, 3,",
                '             NormalizeDouble(SL,digits), NormalizeDouble(TP3,digits), COMMENT+"_TP3", MAGIC, 0, clrGreen);',
                '   Print("MT4 Ordenes: TP1=",t1," TP2=",t2," TP3=",t3);',
                "}",
            ])

            mql5 = "\n".join(_mql_header("MetaTrader 5") + [
                "void OnStart()",
                "{",
                "   double lot1 = NormalizeDouble(LOT_SIZE*0.500, 2);",
                "   double lot2 = NormalizeDouble(LOT_SIZE*0.286, 2);",
                "   double lot3 = NormalizeDouble(LOT_SIZE*0.214, 2);",
                "   MqlTradeRequest req = {}; MqlTradeResult res = {};",
                "   req.action = TRADE_ACTION_PENDING;",
                "   req.type   = ORDER_TYPE_BUY_STOP;",
                "   req.symbol = SYMBOL; req.price = ENTRADA; req.sl = SL;",
                "   req.magic  = MAGIC;  req.expiration = 0;",
                "   req.volume = lot1; req.tp = TP1;",
                '   req.comment = COMMENT+"_TP1"; OrderSend(req,res);',
                "   req.volume = lot2; req.tp = TP2;",
                '   req.comment = COMMENT+"_TP2"; OrderSend(req,res);',
                "   req.volume = lot3; req.tp = TP3;",
                '   req.comment = COMMENT+"_TP3"; OrderSend(req,res);',
                '   Print("MT5 Ordenes enviadas OK");',
                "}",
            ])

            pine = generar_pinescript(
                row["Ticker"], tr,
                stoch_k, stoch_d, vol_period, sr_period,
                roc_period, oversold, overbought,
                vol_mult, roc_min, cruce_ventana, interval,
                direccion="short" if _es_short_row else "long"
            )

            rr1_color = "#00ff88" if tr["rr1"] >= 1.0 else "#ffdd44"
            rr2_color = "#00ff88" if tr["rr2"] >= 2.0 else "#ffdd44"
            rr3_color = "#00ff88" if tr["rr3"] >= 3.0 else "#ffdd44"

            _tv_url_trade = tradingview_url(row["Ticker"])
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">'
                f'<span style="font-size:1.3em;font-weight:700">🎯 Patrón de Trade</span>'
                f'<a href="{_tv_url_trade}" target="_blank" style="'
                f'background:#1a56db;color:#fff;text-decoration:none;border-radius:8px;'
                f'padding:6px 16px;font-size:13px;font-weight:700;'
                f'box-shadow:0 2px 10px #2563eb44">'
                f'📈 Ver en TradingView</a>'
                f'</div>',
                unsafe_allow_html=True
            )
            # ── Texto WhatsApp ────────────────────────────────────────────────
            _nombre_ticker = fund.get("nombre", ticker) if fund else ticker
            _fecha_señal   = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
            _es_futuro     = ticker.endswith("=F")
            _es_crypto     = ticker.endswith("-USD")
            _tipo_activo   = "Futuro" if _es_futuro else "Crypto" if _es_crypto else "Acción"
            _estrellas     = "⭐⭐⭐⭐⭐" if score_tot >= 80 else "⭐⭐⭐⭐" if score_tot >= 65 else "⭐⭐⭐"

            _decimales = 5 if ticker.endswith("=X") else 4 if _es_crypto and tr["entrada"] < 1 else 2
            _fmt = f"{{:.{_decimales}f}}"

            texto_whatsapp = (
                f"🚨 *SEÑAL DE ENTRADA — MOMENTO DULCE* 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 *{_nombre_ticker}* ({ticker})\n"
                f"📅 {_fecha_señal}  |  {_tipo_activo}\n"
                f"🏆 Score señal: {score_tot:.0f}/100  {_estrellas}\n"
                f"\n"
                f"📈 *OPERATIVA LARGO*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📍 *Entrada:*   {_fmt.format(tr['entrada'])}\n"
                f"🛑 *Stop Loss:* {_fmt.format(tr['sl'])}  (-{tr['riesgo_pct']:.2f}%)\n"
                f"\n"
                f"🎯 *Take Profit 1:* {_fmt.format(tr['tp1'])}  (R:R {tr['rr1']:.1f}x — 50% posición)\n"
                f"🏆 *Take Profit 2:* {_fmt.format(tr['tp2'])}  (R:R {tr['rr2']:.1f}x — 30% posición)\n"
                f"🚀 *Take Profit 3:* {_fmt.format(tr['tp3'])}  (R:R {tr['rr3']:.1f}x — 20% posición)\n"
                f"\n"
                f"📊 *Fibonacci:* retroceso {row['_retroceso_pct']:.1f}%  |  nivel {row['_nivel_cercano']}\n"
                f"📉 Swing Low: {_fmt.format(row['_swing_low'])}  |  Swing High: {_fmt.format(row['_swing_high'])}\n"
                f"\n"
                f"⚙️ *Condiciones activas:*\n"
                + (f"  ✅ K < umbral sobreventa\n" if row.get('K<umbral') else f"  ⬜ K < umbral sobreventa\n")
                + (f"  ✅ Cruce K > D reciente\n" if row.get('Cruce K>D') else f"  ⬜ Cruce K > D reciente\n")
                + (f"  ✅ Volumen > Media\n"       if row.get('Vol>MA')   else f"  ⬜ Volumen > Media\n")
                + (f"  ✅ ROC momentum positivo\n" if row.get('ROC ok')   else f"  ⬜ ROC momentum positivo\n")
                + (f"  ✅ Precio > Soporte\n"      if row.get('Close>Sop') else f"  ⬜ Precio > Soporte\n")
                + f"\n"
                f"⚠️ _Esto no es asesoramiento financiero. Opera siempre con gestión de riesgo._\n"
                f"🤖 _Generado por Momento Dulce Scanner_"
            )

            tab_pat, tab_wa, tab_json, tab_mt4, tab_mt5, tab_pine = st.tabs([
                "🎯 Patrón", "📱 WhatsApp", "📄 JSON", "🖥️ MT4", "🖥️ MT5", "📈 PineScript"
            ])

            with tab_pat:
                _rng   = tr['tp3'] - tr['sl']
                _pct_e  = round((tr['entrada'] - tr['sl']) / _rng * 100, 1) if _rng else 25
                _pct_t1 = round((tr['tp1']    - tr['sl']) / _rng * 100, 1) if _rng else 55
                _pct_t2 = round((tr['tp2']    - tr['sl']) / _rng * 100, 1) if _rng else 78

                def _nivel_card(icon, titulo, color, bg1, bg2, bdr, precio_str,
                                badge_txt, badge_color, desc1, desc2, peso=None, ayuda=""):
                    peso_html = (f"<span style='background:{color}22;color:{color};font-size:10px;"
                                 f"font-weight:700;padding:3px 10px;border-radius:20px;"
                                 f"border:1px solid {color}44'>{peso}</span>" if peso else "")
                    return f"""
<div style="background:linear-gradient(145deg,{bg1},{bg2});border:1px solid {bdr};
     border-radius:16px;padding:20px 18px;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
       background:linear-gradient(90deg,{color},{color}88)"></div>
  <div style="font-size:26px;margin-bottom:10px">{icon}</div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap">
    <span style="color:{color};font-size:11px;font-weight:800;text-transform:uppercase;
          letter-spacing:1.2px">{titulo}</span>
    {peso_html}
  </div>
  <div style="color:#ffffff;font-size:28px;font-weight:900;letter-spacing:-1px;
       line-height:1;margin-bottom:8px">{precio_str}</div>
  <div style="display:inline-block;background:{badge_color}22;color:{badge_color};
       font-size:12px;font-weight:800;padding:4px 12px;border-radius:20px;
       border:1px solid {badge_color}44;margin-bottom:14px">{badge_txt}</div>
  <div style="border-top:1px solid {bdr};padding-top:12px">
    <div style="color:{color}bb;font-size:11px;font-weight:700;margin-bottom:4px">{desc1}</div>
    <div style="color:#94a3b8;font-size:11px;line-height:1.6">{desc2}</div>
  </div>
</div>"""

                st.markdown(f"""
<div style="margin-bottom:14px">
  <!-- BARRA PROGRESO -->
  <div style="position:relative;height:12px;border-radius:8px;overflow:hidden;
       background:linear-gradient(90deg,
         #5a0a0a 0%,
         #cc2222 {_pct_e:.0f}%,
         #1a8844 {_pct_e:.0f}%,
         #22bb66 {_pct_t1:.0f}%,
         #11ee77 {_pct_t2:.0f}%,
         #00ffaa 100%);
       box-shadow:0 2px 16px #00000088;margin-bottom:6px">
    <div style="position:absolute;left:{_pct_e:.1f}%;top:0;width:3px;height:100%;
         background:#fff;box-shadow:0 0 8px #fff"></div>
    <div style="position:absolute;left:{_pct_t1:.1f}%;top:2px;width:2px;height:8px;background:#88ffcc88"></div>
    <div style="position:absolute;left:{_pct_t2:.1f}%;top:2px;width:2px;height:8px;background:#44ffaa88"></div>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:9px;color:#555;padding:0 2px">
    <span>SL {tr['sl']:.2f}</span>
    <span style="color:#aaa">▲ Entrada {tr['entrada']:.2f}</span>
    <span>TP3 {tr['tp3']:.2f}</span>
  </div>
</div>

<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px">
{_nivel_card("🟢","Entrada","#00ff88","#071a0f","#0a2416","#1a6640",
    f"{tr['entrada']:.2f}",
    f"−{tr['riesgo_pct']:.2f}% hasta SL","#ff6644",
    "Cómo se calcula","Máximo de la última vela alcista cerrada (gatillo de activación). Es el nivel de ruptura que confirma la señal — entras cuando el precio supera este punto.",
    ayuda="Máximo de la última sesión alcista cerrada.\n\nEs el nivel de ruptura: el precio debe superar este punto para confirmar la señal de entrada.\n\nRiesgo asumido: −{:.2f}% desde aquí hasta el Stop Loss.".format(tr['riesgo_pct']))}
{_nivel_card("🛑","Stop Loss","#ff4444","#1a0707","#260a0a","#7a1a1a",
    f"{tr['sl']:.2f}",
    f"Riesgo: −{tr['riesgo_pct']:.2f}%","#ff4444",
    "Cómo se calcula",f"Soporte dinámico ({row['Soporte']:.2f}) menos un buffer del 1% para evitar stops prematuros.",
    ayuda="Soporte estructural ({:.2f}) menos un buffer del 1%.\n\nEl buffer evita que un movimiento de ruido active el stop prematuramente.\n\nPérdida máxima si se activa: −{:.2f}% sobre la entrada.".format(row['Soporte'], tr['riesgo_pct']))}
{_nivel_card("🎯","TP1 — 50%","#44dd88","#081510","#0a1e16","#1a6635",
    f"{tr['tp1']:.2f}",
    f"R:R  {tr['rr1']:.1f}x",rr1_color,
    "Fib 38.2% del recorrido","Cierra el 50% de la posición al completar el 38.2% del camino entre la entrada y el máximo histórico. Primera zona de resistencia natural donde el mercado suele tomarse un respiro.",
    ayuda="Fib 38.2% aplicado al recorrido pendiente.\n\nCálculo: entrada ({:.2f}) + recorrido ({:.2f}) × 0.382 = {:.2f}\n\nDonde recorrido = máximo ({:.2f}) − entrada ({:.2f}) = {:.2f}\n\nCierras el 50% de la posición — aseguras la mitad del beneficio potencial.\n\nR:R actual: {:.1f}x".format(tr['entrada'], row['_swing_high']-tr['entrada'], tr['tp1'], row['_swing_high'], tr['entrada'], row['_swing_high']-tr['entrada'], tr['rr1']))}
{_nivel_card("🏆","TP2 — 30%","#22cc77","#061210","#081a12","#155530",
    f"{tr['tp2']:.2f}",
    f"R:R  {tr['rr2']:.1f}x",rr2_color,
    "Fib 61.8% del recorrido","Cierras otro 30% al alcanzar el 61.8% del camino — el ratio áureo. Acumulado: 80% de la posición liquidada. El precio está ya muy cerca del máximo.",
    ayuda="Fib 61.8% (ratio áureo) aplicado al recorrido pendiente.\n\nCálculo: entrada ({:.2f}) + recorrido ({:.2f}) × 0.618 = {:.2f}\n\nCierras 30% más → liquidado acumulado: 80%.\n\nZona donde el precio históricamente encuentra mayor resistencia antes del objetivo final.\n\nR:R actual: {:.1f}x".format(tr['entrada'], row['_swing_high']-tr['entrada'], tr['tp2'], tr['rr2']))}
{_nivel_card("🚀","TP3 — 20%","#00ffaa","#040e0c","#061410","#0d4428",
    f"{tr['tp3']:.2f}",
    f"R:R  {tr['rr3']:.1f}x",rr3_color,
    "Máximo histórico — cierra todo","El 20% restante lo cierras en el máximo histórico de la acción. Es el 100% del objetivo. En operativa diaria no tiene sentido ir más allá — es donde el precio ya demostró su límite.",
    ayuda="Máximo histórico de la acción = objetivo final del trade.\n\nPrecio: {:.2f}\n\nCierras el último 20% aquí → 100% de la posición liquidada.\n\nOperando en gráfico diario, el máximo histórico es el techo natural. No perseguir más allá.\n\nR:R actual: {:.1f}x".format(row['_swing_high'], tr['rr3']))}
</div>""", unsafe_allow_html=True)

            with tab_wa:
                _wa_id = f"wa_msg_{ticker.replace('=','_').replace('^','_').replace('-','_')}"
                _wa_escaped = texto_whatsapp.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                st.markdown(
                    f"""
<div style='background:linear-gradient(135deg,#064e3b,#065f46);border:1px solid #10b981;
border-radius:14px;padding:20px 22px;margin-bottom:4px'>
  <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
    <span style='font-size:26px'>📱</span>
    <span style='color:#34d399;font-size:15px;font-weight:700'>Mensaje listo para WhatsApp</span>
  </div>
  <pre id='{_wa_id}' style='background:#022c22;color:#d1fae5;font-size:12.5px;line-height:1.7;
    border-radius:10px;padding:16px;white-space:pre-wrap;word-break:break-word;
    border:1px solid #065f46;max-height:380px;overflow-y:auto;margin:0 0 14px 0'>{texto_whatsapp}</pre>
  <button onclick="
    var el = document.getElementById('{_wa_id}');
    navigator.clipboard.writeText(el.innerText).then(function(){{
      var btn = document.getElementById('btn_{_wa_id}');
      btn.innerText = '✅ ¡Copiado!';
      btn.style.background = '#059669';
      setTimeout(function(){{ btn.innerText = '📋 Copiar mensaje'; btn.style.background = '#10b981'; }}, 2000);
    }});
  "
  id='btn_{_wa_id}'
  style='background:#10b981;color:#fff;border:none;border-radius:8px;padding:10px 28px;
    font-size:14px;font-weight:700;cursor:pointer;width:100%'>
    📋 Copiar mensaje
  </button>
</div>
""",
                    unsafe_allow_html=True
                )

            with tab_json:
                st.caption("Integra en bots, webhooks o sistemas propios.")
                st.code(trade_json, language="json")

            with tab_mt4:
                st.caption("MetaEditor MT4 → Nuevo Script → F7 → Ejecuta en el gráfico.")
                st.code(mql4, language="cpp")

            with tab_mt5:
                st.caption("MetaEditor MT5 → Nuevo Script → F7 → Ejecuta en el gráfico.")
                st.code(mql5, language="cpp")

            with tab_pine:
                st.caption(T["pine_caption"])
                st.code(pine, language="javascript")

else:
    st.info(f"Ninguna acción cumple el perfil **{perfil_nombre}** ahora mismo.")
