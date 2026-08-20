# -*- coding: utf-8 -*-
"""Sistem ayarları sayfası."""
import streamlit as st

import db
from ui.security import admin_gerekli
@admin_gerekli
def sistem_ayarlari(conn):
    st.subheader(":material/settings: Sistem Ayarları")
    st.caption("Kayıt, Pomodoro, oturum ve depolama ayarları.")

    min_kayit = db.ayar_oku(conn, "min_kayit_suresi_sn", 10)
    pomodoro_sn = db.ayar_oku(conn, "pomodoro_calisma_sn", 25 * 60)
    oturum_dk = db.ayar_oku(conn, "oturum_zaman_asimi_dk", 15)
    depo_limit_gb = db.ayar_oku(conn, "depo_limit_gb", db.DEPO_LIMIT_GB_VARSAYILAN)
    video_omur_gun = db.ayar_oku(conn, "video_omur_gun", db.VIDEO_OMUR_GUN_VARSAYILAN)

    yeni_min = st.number_input("Minimum klip süresi (sn)", min_value=1, max_value=300, value=min_kayit, step=1)
    yeni_pom = st.number_input("Pomodoro süresi (dakika)", min_value=1, max_value=180, value=pomodoro_sn // 60, step=1)
    yeni_oturum = st.number_input(
        "Oturum zaman aşımı (dakika)", min_value=1, max_value=1440, value=oturum_dk, step=1,
        help="Kullanıcı bu süre boyunca hiçbir işlem yapmazsa oturumu otomatik kapatılır.",
    )
    yeni_depo = st.number_input(
        "Depolama limiti (GB)", min_value=1, max_value=1024, value=depo_limit_gb, step=1,
        help="Video klasörü bu boyutu aşarsa en eski videolar otomatik silinir.",
    )
    yeni_omur = st.number_input(
        "Video saklama süresi (gün)", min_value=1, max_value=365, value=video_omur_gun, step=1,
        help="Bu süreden eski videolar otomatik silinir.",
    )
    if st.button("Kaydet", icon=":material/save:"):
        db.ayar_yaz(conn, "min_kayit_suresi_sn", int(yeni_min))
        db.ayar_yaz(conn, "pomodoro_calisma_sn", int(yeni_pom) * 60)
        db.ayar_yaz(conn, "oturum_zaman_asimi_dk", int(yeni_oturum))
        db.ayar_yaz(conn, "depo_limit_gb", int(yeni_depo))
        db.ayar_yaz(conn, "video_omur_gun", int(yeni_omur))
        st.success("Ayarlar kaydedildi.")

    st.divider()
    st.subheader(":material/storage: Depolama Durumu")
    sinir_byte = int(depo_limit_gb) * 1024 ** 3
    toplam_byte = db.depo_boyutu()
    d1, d2, d3 = st.columns(3)
    d1.metric("Kullanılan Alan", f"{toplam_byte / (1024 ** 3):.2f} GB")
    d2.metric("Limit", f"{depo_limit_gb} GB")
    d3.metric("Doluluk", f"%{int(toplam_byte / sinir_byte * 100) if sinir_byte else 0}")
    uyari = db.depo_uyari_mesaji(sinir_byte)
    if uyari:
        st.warning(uyari)
    else:
        st.caption("Depolama kullanımı limitin altında.")
    if st.button("Şimdi Temizle", icon=":material/cleaning_services:"):
        silinen, byte = db.depo_temizle(sinir_byte, video_omur_gun)
        if silinen:
            st.success(f"{silinen} eski video silindi ({byte / (1024 ** 2):.1f} MB temizlendi).")
        else:
            st.info("Silinecek eski video bulunamadı.")
