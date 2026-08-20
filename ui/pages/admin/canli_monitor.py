# -*- coding: utf-8 -*-
"""Canlı monitör sayfası."""
import streamlit as st
from datetime import datetime

import db
from core.config import CEVRIMDISI_ESIK_SN
from services.analytics import format_sure
from ui.security import admin_gerekli, guvenli_metin


@admin_gerekli
def canli_monitor(conn):
    st.subheader(":material/sensors: Canlı Monitör")
    st.caption("O an sistemde aktif olan kişilerin durumu")
    _canli_monitor_icerik()


@st.fragment(run_every=5)
def _canli_monitor_icerik():
    conn = db.baglan()
    try:
        satirlar = conn.execute(
            "SELECT kullanici_adi, durum, baslangic, son_guncelleme FROM canli_durum ORDER BY kullanici_adi"
        ).fetchall()
        simdi = datetime.now()

        cevrimici_listesi = []
        cevrimdisi_listesi = []
        for s in satirlar:
            try:
                son = datetime.strptime(s["son_guncelleme"], "%Y-%m-%d %H:%M:%S")
                cevrimici = (simdi - son).total_seconds() < CEVRIMDISI_ESIK_SN
            except Exception:
                cevrimici = False
            if cevrimici:
                cevrimici_listesi.append(s)
            else:
                cevrimdisi_listesi.append(s)

        # Durum bildirim kutusu (iç gölgeli, pürüzsüz)
        if cevrimici_listesi:
            durum_renk = "#34d399"
            durum_metin = f"{len(cevrimici_listesi)} kişi çevrimiçi"
        else:
            durum_renk = "#64748b"
            durum_metin = "Tümü çevrimdışı" if satirlar else "Aktif izleme yok"
        kutu_arka = "rgba(255,255,255,0.04)"
        kutu_kenar = "rgba(255,255,255,0.10)"
        kutu_golge = "inset 0 2px 6px rgba(0,0,0,0.35)"
        kutu_metin = "#e2e8f0"
        st.markdown(
            f"<div style='background:{kutu_arka}; border:1px solid {kutu_kenar}; "
            f"border-radius:14px; padding:0.9rem 1.1rem; box-shadow:{kutu_golge}; "
            f"display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;'>"
            f"<span style='width:12px; height:12px; border-radius:50%; background:{durum_renk}; "
            f"box-shadow:0 0 10px {durum_renk};'></span>"
            f"<span style='color:{kutu_metin}; font-weight:600;'>{durum_metin}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if not satirlar:
            st.info("Şu an izlenen kimse yok")
            return

        for s in cevrimdisi_listesi:
            st.caption(f"{guvenli_metin(s['kullanici_adi'])} — Çevrimdışı (son: {s['son_guncelleme']})")

        for s in cevrimici_listesi:
            etiket, tip = db.DURUM_GORSEL.get(s["durum"], (s["durum"], "info"))
            try:
                bas = datetime.strptime(s["baslangic"], "%Y-%m-%d %H:%M:%S")
                gecen = format_sure(int((simdi - bas).total_seconds()))
            except Exception:
                gecen = "-"
            mesaj = f"**{guvenli_metin(s['kullanici_adi'])}**: {etiket}  ·  {gecen}dir"
            if tip == "success":
                st.success(mesaj)
            elif tip == "warning":
                st.warning(mesaj)
            else:
                st.error(mesaj)
    finally:
        conn.close()
