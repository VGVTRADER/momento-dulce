"""Núcleo compartido: almacenamiento (Supabase o JSON local), login y tickets."""
import hashlib
import json
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
TICKETS_FILE = os.path.join(BASE_DIR, "tickets.json")
SOPORTE_EMAIL = "soporte@patrimonioinfinito.com"


def secret(clave, defecto=""):
    try:
        v = st.secrets.get(clave, None)
    except Exception:
        v = None
    if v in (None, ""):
        v = os.environ.get(clave, defecto)
    return v


# ── Supabase (si hay SUPABASE_URL + SUPABASE_KEY); si no, JSON local ─────────
def _sb_conf():
    url = secret("SUPABASE_URL") or ""
    key = secret("SUPABASE_KEY") or ""
    return str(url).rstrip("/"), str(key)


def _sb_req(method, path, params=None, json_body=None, prefer=None):
    url, key = _sb_conf()
    h = {"apikey": key, "Content-Type": "application/json"}
    if key.startswith("eyJ"):
        h["Authorization"] = f"Bearer {key}"
    if prefer:
        h["Prefer"] = prefer
    r = requests.request(method, f"{url}/rest/v1/{path}", headers=h, params=params, json=json_body, timeout=15)
    r.raise_for_status()
    return r.json() if r.text.strip() else []


def _usa_supabase():
    url, key = _sb_conf()
    return bool(url and key and url != "None" and key != "None" and url.startswith("http"))


def _leer_json(path, defecto):
    if not os.path.exists(path):
        return defecto
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _escribir_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Usuarios ──────────────────────────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def _usuarios_desde_secret():
    """Lee usuarios del secret USUARIOS_JSON (Streamlit Cloud). None si no existe."""
    raw = secret("USUARIOS_JSON", "")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def load_users():
    # 1. Secret USUARIOS_JSON (Streamlit Cloud — sin BD externa)
    uu = _usuarios_desde_secret()
    if uu is not None:
        return uu
    # 2. Supabase (si está configurado y activo)
    if _usa_supabase():
        try:
            return {r["usuario"]: (r.get("datos") or {}) for r in _sb_req("GET", "usuarios", params={"select": "usuario,datos"})}
        except Exception:
            pass
    # 3. Fichero local
    return _leer_json(USERS_FILE, {})


def save_users(data):
    # Si usamos secret JSON, no podemos escribir de vuelta (secrets son read-only)
    # → guardamos en fichero local como cache; el admin actualiza el secret manualmente
    if _usuarios_desde_secret() is not None:
        _escribir_json(USERS_FILE, data)
        return
    if _usa_supabase():
        try:
            prev = set(load_users())
            if data:
                _sb_req("POST", "usuarios", params={"on_conflict": "usuario"},
                        json_body=[{"usuario": k, "datos": v} for k, v in data.items()],
                        prefer="resolution=merge-duplicates,return=minimal")
            for k in prev - set(data):
                _sb_req("DELETE", "usuarios", params={"usuario": f"eq.{k}"})
            return
        except Exception:
            pass
    _escribir_json(USERS_FILE, data)


def check_login(usuario, password):
    """Devuelve {'nombre','rol'} si las credenciales son válidas, si no None.
    Orden: admin (Secrets) -> usuarios guardados (activos)."""
    u = (usuario or "").strip().lower()
    p = (password or "").strip()
    admin_user = str(secret("ADMIN_USER", "boss")).strip().lower()
    admin_pass = str(secret("ADMIN_PASS", "")).strip()
    admin_hash = "501e84111da8dd3a0a29b5894e50826cb48254f16023194ef3004a2f2679aeea"
    if u == admin_user and ((admin_pass and p == admin_pass) or (not admin_pass and hash_pw(p) == admin_hash)):
        return {"nombre": "Admin", "rol": "admin"}
    # Usuarios definidos en Secrets: [USERS.nombre] password=..., nombre=..., rol=...
    try:
        sec = {str(k).strip().lower(): dict(v) for k, v in dict(st.secrets.get("USERS", {})).items()}
    except Exception:
        sec = {}
    su = sec.get(u)
    if su and su.get("activo", True):
        sp = str(su.get("password", "")).strip()
        if sp and (p == sp or hash_pw(p) == sp):
            return {"nombre": su.get("nombre", u), "rol": su.get("rol", "usuario")}
    users ={str(k).strip().lower(): v for k, v in load_users().items()}
    d = users.get(u)
    if d and d.get("activo") and d.get("password") == hash_pw(p):
        return {"nombre": d.get("nombre", u), "rol": d.get("rol", "usuario")}
    return None


def cuenta_pendiente(usuario, password):
    d = {str(k).strip().lower(): v for k, v in load_users().items()}.get((usuario or "").strip().lower())
    return bool(d and not d.get("activo") and d.get("password") == hash_pw((password or "").strip()))


# ── Tickets ───────────────────────────────────────────────────────────────────
def load_tickets():
    if _usa_supabase():
        rows = _sb_req("GET", "tickets", params={"select": "id,datos"})
        return sorted([dict(r.get("datos") or {}, id=r["id"]) for r in rows], key=lambda t: str(t.get("id", "")))
    return _leer_json(TICKETS_FILE, [])


def save_tickets(tickets):
    if _usa_supabase():
        if tickets:
            _sb_req("POST", "tickets", params={"on_conflict": "id"},
                    json_body=[{"id": str(t["id"]), "datos": t} for t in tickets],
                    prefer="resolution=merge-duplicates,return=minimal")
        return
    _escribir_json(TICKETS_FILE, tickets)


def crear_ticket(nombre, email, asunto, mensaje):
    """Guarda el ticket y avisa por email a soporte (si hay SMTP). Devuelve (id, email_enviado)."""
    ahora = datetime.now()
    t = {
        "id": f"PI-{ahora:%Y%m%d%H%M%S}",
        "fecha": f"{ahora:%d/%m/%Y %H:%M}",
        "nombre": nombre, "email": email, "asunto": asunto, "mensaje": mensaje,
        "estado": "abierto",
    }
    if _usa_supabase():
        save_tickets([t])
    else:
        save_tickets(load_tickets() + [t])
    return t["id"], _avisar_soporte(t)


def n_tickets_abiertos():
    try:
        return sum(1 for t in load_tickets() if t.get("estado", "abierto") != "resuelto")
    except Exception:
        return 0


def _avisar_soporte(t):
    smtp_user, smtp_pass = str(secret("SMTP_USER")), str(secret("SMTP_PASS"))
    if not smtp_user:
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[{t['id']}] {t['asunto']} — {t['nombre']}"
    msg["From"] = smtp_user
    msg["To"] = SOPORTE_EMAIL
    msg["Reply-To"] = t["email"]
    cuerpo = t["mensaje"].replace("\n", "<br>")
    msg.attach(MIMEText(
        f"<p><b>Ticket {t['id']}</b> · {t['fecha']}</p>"
        f"<p><b>{t['nombre']}</b> &lt;{t['email']}&gt;<br>Asunto: {t['asunto']}</p>"
        f"<p>{cuerpo}</p>", "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as srv:
            srv.login(smtp_user, smtp_pass)
            srv.sendmail(smtp_user, SOPORTE_EMAIL, msg.as_string())
        return True
    except Exception:
        return False
