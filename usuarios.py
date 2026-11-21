"""👥 Usuarios (solo admin): alta, pagado/activo y baja."""
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from core import hash_pw, load_users, save_users


def _usuarios_de_secrets():
    """Lee los usuarios definidos en [USERS] de Streamlit Secrets."""
    try:
        sec = {str(k).strip().lower(): dict(v) for k, v in dict(st.secrets.get("USERS", {})).items()}
    except Exception:
        sec = {}
    result = {}
    for k, v in sec.items():
        result[k] = {
            "nombre": v.get("nombre", k),
            "rol": v.get("rol", "usuario"),
            "activo": bool(v.get("activo", True)),
            "creado": v.get("creado", "Secrets"),
            "_de_secrets": True,
        }
    return result


def render():
    st.markdown(
        "<div style='font-size:20px;font-weight:800;color:#f3efe8;margin:8px 0 2px'>👥 USUARIOS</div>"
        "<div style='color:#8e8a83;font-size:12px;margin-bottom:12px'>"
        "Marca ✅ Pagado para dar acceso. Si no está marcado, no entra.</div>",
        unsafe_allow_html=True,
    )
    try:
        uu = load_users()
    except Exception as e:
        st.error(f"No se pudo leer la lista de usuarios ({type(e).__name__}).")
        return

    # Combinar con usuarios de Secrets (solo lectura — se muestran pero no se editan)
    uu_secrets = _usuarios_de_secrets()
    uu_combinado = {**uu_secrets, **uu}  # los del JSON/Supabase tienen prioridad

    flash = st.session_state.pop("_nu_flash", None)
    if flash:
        st.success(flash)

    # ── Alta ──
    with st.container(border=True):
        st.markdown("**➕ Dar de alta usuario**")
        with st.form("form_nuevo_usuario", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nu_user = c1.text_input("Email / usuario")
            nu_pass = c2.text_input("Contraseña", type="password")
            c3, c4 = st.columns(2)
            nu_nombre = c3.text_input("Nombre (opcional)")
            nu_rol = c4.selectbox("Rol", ["usuario", "admin"])
            nu_pagado = st.checkbox("✅ Pagado (acceso activo)", value=True)
            ok = st.form_submit_button("➕ Dar de alta", type="primary", use_container_width=True)
        if ok:
            u, p = (nu_user or "").strip().lower(), (nu_pass or "").strip()
            if not u or not p:
                st.error("Usuario y contraseña son obligatorios.")
            elif u in {str(k).strip().lower() for k in uu}:
                st.error(f"El usuario «{u}» ya existe.")
            elif len(p) < 4:
                st.error("La contraseña debe tener al menos 4 caracteres.")
            else:
                uu[u] = {"password": hash_pw(p), "nombre": nu_nombre.strip() or u, "rol": nu_rol,
                         "activo": bool(nu_pagado), "creado": f"{datetime.now():%d/%m/%Y %H:%M}"}
                if "@" in u:
                    uu[u]["email"] = u
                try:
                    save_users(uu)
                    st.session_state["_nu_flash"] = f"✅ Usuario «{u}» creado."
                    st.rerun()
                except Exception as e:
                    st.error(f"No se pudo crear el usuario ({type(e).__name__}).")

    if not uu_combinado:
        st.info("Todavía no hay usuarios registrados.")
        return

    # ── Tabla pagado ──
    filas = [{"Email": k,
              "Nombre": v.get("nombre", ""),
              "Rol": v.get("rol", "usuario"),
              "Alta": v.get("creado", ""),
              "Pagado": bool(v.get("activo")),
              "Origen": "🔒 Secrets" if v.get("_de_secrets") else "📋 Panel"}
             for k, v in uu_combinado.items()]
    pend = sum(1 for f in filas if not f["Pagado"])
    st.markdown(f"Total: **{len(filas)}** · Pendientes: **:orange[{pend}]**")
    _disabled = ["Email", "Nombre", "Rol", "Alta", "Origen"]
    # Los de Secrets no se pueden editar desde el panel (son read-only)
    ed = st.data_editor(
        pd.DataFrame(sorted(filas, key=lambda f: (f["Pagado"], f["Email"]))),
        hide_index=True, use_container_width=True, disabled=_disabled,
        column_config={"Pagado": st.column_config.CheckboxColumn("✅ Pagado")}, key="tabla_usuarios",
    )
    if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
        for _, row in ed.iterrows():
            if row["Email"] in uu:  # solo los del panel, no los de Secrets
                uu[row["Email"]]["activo"] = bool(row["Pagado"])
        try:
            save_users(uu)
            st.session_state["_nu_flash"] = "✅ Cambios guardados."
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo guardar ({type(e).__name__}).")

    # ── Baja ──
    c_del1, c_del2 = st.columns([3, 1])
    borrar = c_del1.selectbox("Eliminar usuario", ["—"] + sorted(uu), label_visibility="collapsed")
    if c_del2.button("🗑️ Eliminar", use_container_width=True) and borrar != "—":
        uu.pop(borrar, None)
        try:
            save_users(uu)
            st.session_state["_nu_flash"] = f"🗑️ Usuario «{borrar}» eliminado."
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo eliminar ({type(e).__name__}).")

    # ── Copia de seguridad ──
    with st.expander("💾 Copia de seguridad"):
        # JSON completo (panel + secrets)
        backup_json = json.dumps(uu_combinado, indent=2, ensure_ascii=False).encode("utf-8")
        st.download_button("⬇️ Descargar copia JSON (todos los usuarios)",
                           data=backup_json,
                           file_name=f"usuarios_backup_{datetime.now():%Y%m%d_%H%M}.json",
                           mime="application/json", use_container_width=True)
        # TOML listo para pegar en Streamlit Secrets
        lineas_toml = []
        for k, v in uu_combinado.items():
            lineas_toml.append(f'\n[USERS.{k}]')
            lineas_toml.append(f'nombre = "{v.get("nombre", k)}"')
            lineas_toml.append(f'rol = "{v.get("rol", "usuario")}"')
            lineas_toml.append(f'activo = {"true" if v.get("activo") else "false"}')
            if not v.get("_de_secrets"):
                lineas_toml.append(f'# password guardado con hash (no visible)')
        toml_txt = "\n".join(lineas_toml)
        st.download_button("⬇️ Descargar TOML para Streamlit Secrets",
                           data=toml_txt.encode("utf-8"),
                           file_name=f"secrets_users_{datetime.now():%Y%m%d_%H%M}.toml",
                           mime="text/plain", use_container_width=True)
        fich = st.file_uploader("⬆️ Restaurar copia (.json) — añade/actualiza, no borra", type=["json"])
        if fich is not None and st.button("Restaurar", type="primary"):
            try:
                data = json.loads(fich.getvalue().decode("utf-8"))
                if not isinstance(data, dict) or not data:
                    raise ValueError("el archivo no contiene usuarios")
                save_users({**uu, **data})
                st.session_state["_nu_flash"] = f"✅ Copia restaurada ({len(data)} usuarios)."
                st.rerun()
            except Exception as e:
                st.error(f"Archivo no válido: {e}")
