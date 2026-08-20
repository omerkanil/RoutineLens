# -*- coding: utf-8 -*-
"""Oturum (giriş/çıkış) yönetimi."""
import streamlit as st

import db
def cikis(conn):
    token = st.query_params.get("token")
    if token:
        db.oturum_sil(conn, token)
    try:
        st.query_params.pop("token", None)
    except Exception:
        pass
    st.session_state.giris = None
    st.rerun()
