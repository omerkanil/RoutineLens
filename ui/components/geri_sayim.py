# -*- coding: utf-8 -*-
"""Oturum geri sayım bileşeni (sidebar)."""
import time

import streamlit as st

import db


def _format_sure(saniye):
    saat, kalan = divmod(saniye, 3600)
    dakika, sn = divmod(kalan, 60)
    if saat > 0:
        return f"{saat:02d}:{dakika:02d}:{sn:02d}"
    return f"{dakika:02d}:{sn:02d}"


def oturum_bitis_hesapla(conn, token):
    """Oturumun bitiş zamanını (epoch saniye) ve süreyi (dk) döndürür.

    Süre girişten itibaren sabittir; işlem yaptıkça yenilenmez.
    """
    sure_dk = db.ayar_oku(conn, "oturum_zaman_asimi_dk", 15)
    if sure_dk <= 0:
        return None, sure_dk
    son = db.oturum_baslangic(conn, token) if token else None
    if son is None:
        return None, sure_dk
    return son.timestamp() + sure_dk * 60, sure_dk


@st.fragment(run_every=1)
def geri_sayim(bitis_timestamp, sure_dk):
    """Sidebar'da kalan süreyi canlı gösterir (DB erişimi yapmaz)."""
    kalan = int(bitis_timestamp - time.time())
    kalan = max(0, kalan)

    oran = kalan / (sure_dk * 60)
    if oran > 0.3:
        renk = "#34d399"   # yeşil
    elif oran > 0.15:
        renk = "#f97316"   # turuncu
    else:
        renk = "#ef4444"   # kırmızı

    st.markdown(
        f"<div style='text-align:center; padding:0.3rem 0 0.55rem;'>"
        f"<div style='font-size:0.66rem; letter-spacing:0.06em; text-transform:uppercase; "
        f"color:#94a3b8;'>Oturum Süresi</div>"
        f"<div style='font-size:1.5rem; font-weight:800; color:{renk}; "
        f"letter-spacing:0.04em; font-variant-numeric:tabular-nums; line-height:1.2;'>"
        f"{_format_sure(kalan)}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
