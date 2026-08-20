# -*- coding: utf-8 -*-
"""Takım analitiği sayfası."""
import io
import pandas as pd
import streamlit as st
from datetime import datetime

import db
from services.analytics import format_sure, verimlilik_skoru, kullanici_adi_goster, saatlik_df, gunluk_trend_df
from ui.security import admin_gerekli
from ui.components.grafikler import saatlik_verim_grafigi, gunluk_trend_grafigi


@st.cache_data(ttl=60, show_spinner=False)
def _saatlik_df_oku(tarih):
    conn = db.baglan()
    try:
        return saatlik_df(conn, tarih)
    finally:
        conn.close()


@st.cache_data(ttl=60, show_spinner=False)
def _gunluk_trend_oku():
    conn = db.baglan()
    try:
        return gunluk_trend_df(conn)
    finally:
        conn.close()


@st.cache_data(ttl=60, show_spinner=False)
def _df_all_oku():
    conn = db.baglan()
    try:
        return pd.read_sql_query(
            "SELECT id, tarih, saat, durum, gecirilen_sure_sn, kullanici_adi FROM rutin_loglari "
            "WHERE kullanici_adi IS NOT NULL AND kullanici_adi != 'genel' ORDER BY id", conn)
    finally:
        conn.close()


@st.cache_data(show_spinner=False)
def _excel_uret(df):
    b = io.BytesIO()
    with pd.ExcelWriter(b, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="RutinLoglari")
    return b.getvalue()


@admin_gerekli
def takim_analitigi(conn):
    st.subheader(":material/analytics: Takım Analitiği")
    st.caption("Tüm şirketin/sınıfın genel odak ortalamaları ve verimin düştüğü saatler.")

    bugun = datetime.now().strftime("%Y-%m-%d")
    genel = conn.execute("""
        SELECT
            SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS calisma,
            SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS telefon,
            SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS dinlenme,
            SUM(CASE WHEN durum IN (?, ?) THEN gecirilen_sure_sn ELSE 0 END) AS odak_kaybi
        FROM rutin_loglari
        WHERE tarih = ? AND kullanici_adi IS NOT NULL AND kullanici_adi != 'genel'
    """, (db.DURUM_CALISMA, db.DURUM_TELEFON, db.DURUM_DINLENME,
          *db.ODAK_KAYBI_DURUMLAR, bugun)).fetchone()

    calisma = genel["calisma"] or 0
    telefon = genel["telefon"] or 0
    dinlenme = genel["dinlenme"] or 0
    odak = genel["odak_kaybi"] or 0
    skor = verimlilik_skoru(calisma, dinlenme, telefon)

    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("Takım Odak Skoru", f"{skor}/100")
    g2.metric("Toplam Çalışma", format_sure(calisma))
    g3.metric("Toplam Telefon", format_sure(telefon))
    g4.metric("Toplam Dinlenme", format_sure(dinlenme))
    g5.metric("Odak Kaybı", format_sure(odak))

    st.divider()
    st.subheader(":material/group: Kişi Bazlı Özet (Bugün)")
    kisi_df = conn.execute("""
        SELECT kullanici_adi AS kullanici,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS calisma,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS telefon,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS dinlenme,
               SUM(CASE WHEN durum IN (?, ?) THEN gecirilen_sure_sn ELSE 0 END) AS odak_kaybi
        FROM rutin_loglari
        WHERE tarih = ? AND kullanici_adi IS NOT NULL AND kullanici_adi != 'genel'
        GROUP BY kullanici_adi ORDER BY calisma DESC
    """, (db.DURUM_CALISMA, db.DURUM_TELEFON, db.DURUM_DINLENME,
          *db.ODAK_KAYBI_DURUMLAR, bugun)).fetchall()
    if kisi_df:
        df = pd.DataFrame([dict(r) for r in kisi_df])
        df = df.rename(columns={
            "kullanici": "Kişi", "calisma": "Çalışma", "telefon": "Telefon",
            "dinlenme": "Dinlenme", "odak_kaybi": "Odak Kaybı",
        })
        df["Kişi"] = df["Kişi"].apply(kullanici_adi_goster)
        for col in ["Çalışma", "Telefon", "Dinlenme", "Odak Kaybı"]:
            df[col] = df[col].apply(format_sure)
        st.dataframe(df, width="stretch")
    else:
        st.info("Bugüne ait veri yok.")

    st.divider()
    st.subheader(":material/schedule: Saatlik Verim Analizi (Bugün)")
    saat_df = _saatlik_df_oku(bugun)
    if not saat_df.empty:
        st.plotly_chart(saatlik_verim_grafigi(saat_df), use_container_width=True)
        st.caption("Yeşil: çalışma (dk) · Turuncu: telefon (dk). Bugün hangi saatlerde verimin düştüğünü gösterir.")
    else:
        st.info("Bugüne ait saatlik veri yok.")

    st.divider()
    st.subheader(":material/bar_chart: Günlük Çalışma Trendi (Toplam, dakika)")
    trend_df = _gunluk_trend_oku()
    if not trend_df.empty:
        pivot = trend_df.pivot(index="tarih", columns="kullanici", values="calisma_dk").fillna(0)
        pivot.columns = [kullanici_adi_goster(c) for c in pivot.columns]
        st.plotly_chart(gunluk_trend_grafigi(pivot), use_container_width=True)
    else:
        st.info("Trend verisi yok.")

    st.divider()
    st.subheader(":material/download: Raporu İndir")
    df_all = _df_all_oku()
    if not df_all.empty:
        df_all = df_all.rename(columns={
            "id": "ID", "tarih": "Tarih", "saat": "Saat", "durum": "Durum",
            "gecirilen_sure_sn": "Süre (sn)", "kullanici_adi": "Kullanıcı",
        })
        df_all["Süre (okunabilir)"] = df_all["Süre (sn)"].apply(format_sure)
        excel_verisi = None
        try:
            excel_verisi = _excel_uret(df_all)
        except Exception:
            pass
        c1, c2 = st.columns(2)
        with c1:
            if excel_verisi:
                st.download_button("Excel İndir", icon=":material/table_chart:", data=excel_verisi,
                                   file_name=f"takim_rapor_{bugun}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("Excel için 'openpyxl' gerekli.")
        with c2:
            st.download_button("CSV İndir", icon=":material/download:", data=df_all.to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"takim_rapor_{bugun}.csv", mime="text/csv")
    else:
        st.info("Dışa aktarılacak kayıt yok.")
