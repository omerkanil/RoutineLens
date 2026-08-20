# -*- coding: utf-8 -*-
"""Admin paneli (dağıtıcı / dispatcher)."""
import streamlit as st

import db
from ui.security import admin_gerekli, guvenli_metin
from ui.session import cikis
from ui.styles import admin_stil
from ui.components.geri_sayim import geri_sayim, oturum_bitis_hesapla
from ui.components.marka import marka_basligi
from ui.pages.admin.canli_monitor import canli_monitor
from ui.pages.admin.liderlik import liderlik
from ui.pages.admin.video_merkezi import video_merkezi
from ui.pages.admin.kullanici_yonetimi import kullanici_yonetimi
from ui.pages.admin.takim_analitigi import takim_analitigi
from ui.pages.admin.sistem_ayarlari import sistem_ayarlari


@admin_gerekli
def admin_paneli(conn, kullanici):
    ad = kullanici.get("ad_soyad") or kullanici["kullanici_adi"]
    admin_stil()

    baslik = "#ffffff"

    marka_basligi()
    st.sidebar.caption(f"Yönetici: {guvenli_metin(ad)}")

    st.sidebar.divider()

    # --- Oturum geri sayımı ---
    bitis, sure_dk = oturum_bitis_hesapla(conn, st.query_params.get("token"))
    if bitis is not None:
        with st.sidebar:
            geri_sayim(bitis, sure_dk)

    st.sidebar.divider()

    secenekler = [
        ("Canlı Monitör", ":material/sensors:"),
        ("Liderlik Tablosu", ":material/emoji_events:"),
        ("Video Kanıt Merkezi", ":material/video_library:"),
        ("Kullanıcı Yönetimi", ":material/group:"),
        ("Takım Analitiği", ":material/analytics:"),
        ("Sistem Ayarları", ":material/settings:"),
    ]

    if "admin_bolum" not in st.session_state:
        st.session_state.admin_bolum = "Canlı Monitör"

    for etiket, ikon in secenekler:
        aktif_mi = st.session_state.admin_bolum == etiket
        if st.sidebar.button(
            etiket,
            icon=ikon,
            type="primary" if aktif_mi else "secondary",
            width="stretch",
        ):
            st.session_state.admin_bolum = etiket
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("Çıkış Yap", icon=":material/logout:", width="stretch"):
        cikis(conn)

    bolum = st.session_state.admin_bolum

    st.markdown(
        f"<div style='padding:0.1rem 0 0.4rem;'>"
        f"<span style='font-weight:800; font-size:2.2rem; letter-spacing:-0.03em; color:{baslik};'>Routine</span>"
        f"<span style='font-weight:800; font-size:2.2rem; letter-spacing:-0.03em; "
        f"background:linear-gradient(90deg,#60a5fa,#a78bfa); -webkit-background-clip:text; "
        f"background-clip:text; -webkit-text-fill-color:transparent; color:transparent;'>Lens</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown("Tüm ekip için tam yetkili yönetim paneli.")

    with st.container(border=True):
        if bolum == "Canlı Monitör":
            canli_monitor(conn)
        elif bolum == "Liderlik Tablosu":
            liderlik(conn)
        elif bolum == "Video Kanıt Merkezi":
            video_merkezi(conn)
        elif bolum == "Kullanıcı Yönetimi":
            kullanici_yonetimi(conn)
        elif bolum == "Takım Analitiği":
            takim_analitigi(conn)
        else:
            sistem_ayarlari(conn)
