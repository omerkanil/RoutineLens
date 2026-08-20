# -*- coding: utf-8 -*-
"""RoutineLens — web paneli (ince orkestratör).

Sayfaları ui/pages içinden çağırır; oturum, tema ve güvenlik katmanlarını
ui paketinden yönetir.
"""
import streamlit as st

import db
from database.manager import db_manager
from ui.security import oturum_zaman_asimi_kontrol, oturum_denetim_fragmani
from ui.styles import genel_stil
from ui.pages.login import login_ekrani
from ui.pages.personel import calisan_paneli
from ui.pages.admin import admin_paneli

st.set_page_config(page_title="RoutineLens", layout="wide")


@st.cache_resource
def _schema_bir_kez_kur():
    """Şemayı ve indeksleri yalnızca bir kez kurar (her istekte tekrar etmez)."""
    db_manager.schema_kur()


def main():
    _schema_bir_kez_kur()
    conn = db_manager.baglan()
    genel_stil()
    if "giris" not in st.session_state:
        st.session_state.giris = None

    token = st.query_params.get("token")

    # Sayfa yenilendiğinde oturumu token ile geri yükle (kalıcı giriş)
    if st.session_state.giris is None and token:
        kullanici = db.oturum_dogrula(conn, token)
        if kullanici:
            st.session_state.giris = kullanici

    # Oturum zaman aşımı denetimi (süre girişten itibaren sabittir)
    if st.session_state.giris is not None:
        oturum_zaman_asimi_kontrol(conn, token)
        oturum_denetim_fragmani()

    # Zaman aşımı / çıkış mesajını göster
    if "cikis_mesaji" in st.session_state:
        st.warning(st.session_state.pop("cikis_mesaji"))

    if st.session_state.giris is None:
        login_ekrani(conn)
    elif st.session_state.giris["rol"] == "admin":
        admin_paneli(conn, st.session_state.giris)
    else:
        calisan_paneli(conn, st.session_state.giris)


main()
