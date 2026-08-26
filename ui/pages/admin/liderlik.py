# -*- coding: utf-8 -*-
"""Liderlik tablosu sayfası."""
import streamlit as st
from datetime import datetime, timedelta

import db
from services.analytics import liderlik_df, format_sure, kullanici_adi_goster
from ui.security import admin_gerekli, guvenli_metin
from ui.components.grafikler import liderlik_grafigi, liderlik_pasta_grafigi, liderlik_cizgi_grafigi


@st.cache_data(ttl=60, show_spinner=False)
def _liderlik_df_oku(bas):
    conn = db.baglan()
    try:
        return liderlik_df(conn, bas)
    finally:
        conn.close()


@admin_gerekli
def liderlik(conn):
    st.subheader(":material/emoji_events: Pozitif Liderlik Tablosu")
    st.caption("Sadece toplam çalışılan süreye göre sıralanır. Rekabet değil, pozitif teşvik.")
    aralik = st.radio("Aralık", ["Bugün", "Bu Hafta"], horizontal=True)
    if aralik == "Bugün":
        bas = datetime.now().strftime("%Y-%m-%d")
    else:
        bas = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    df = _liderlik_df_oku(bas)
    if df.empty:
        st.info("Bu aralıkta henüz çalışma kaydı yok.")
        return
    madalya = {0: "1.", 1: "2.", 2: "3."}
    max_calisma = int(df["calisma_sn"].max()) or 1
    for i, row in df.iterrows():
        isim = kullanici_adi_goster(row["kullanici"])
        amblem = madalya.get(i, f"{i + 1}.")
        st.write(f"{amblem} **{guvenli_metin(isim)}** — {format_sure(int(row['calisma_sn']))}")
        st.progress(min(int(row["calisma_sn"]) / max_calisma, 1.0))
    st.divider()
    grafik_turu = st.radio("Grafik türü", ["Bar", "Pie", "Çizgi"], horizontal=True)
    if grafik_turu == "Pie":
        fig = liderlik_pasta_grafigi(df)
    elif grafik_turu == "Çizgi":
        fig = liderlik_cizgi_grafigi(df)
    else:
        fig = liderlik_grafigi(df)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
