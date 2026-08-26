# -*- coding: utf-8 -*-
"""Personel paneli."""
import streamlit as st
import pandas as pd
from datetime import datetime

import db
from services.analytics import kullanici_gunluk_ozet, verimlilik_skoru, format_sure
from services.tracking import takip_aktif_mi, takip_baslat, takip_durdur
from ui.components.takvim import takvim_widget
from ui.security import guvenli_metin
from ui.session import cikis
from ui.styles import personel_stil
from ui.components.grafikler import kisisel_grafik, kisisel_pasta_grafigi, kisisel_cizgi_grafigi
from ui.components.marka import marka_basligi


def calisan_paneli(conn, kullanici):
    ad = kullanici.get("ad_soyad") or kullanici["kullanici_adi"]
    personel_stil()

    metin = "#f1f5f9"
    ikincil = "#94a3b8"
    vurgu = "#f8fafc"
    soluk = "#64748b"

    # --- MARKA BAŞLIĞI (büyük, kutulu) ---
    marka_basligi()
    st.sidebar.divider()

    # --- KULLANICI PROFİLİ ---
    bas_harfler = guvenli_metin("".join([p[0] for p in ad.split() if p][:2]).upper() or "RL")
    st.sidebar.markdown(
        f"<div style='display:flex; align-items:center; gap:0.8rem; padding:0.4rem 0 0.5rem;'>"
        f"<div style='width:46px; height:46px; min-width:46px; border-radius:50%; "
        f"background:linear-gradient(135deg,#8b5cf6,#6366f1); display:flex; align-items:center; "
        f"justify-content:center; color:#fff; font-weight:800; font-size:1.05rem; "
        f"box-shadow:0 0 16px rgba(139,92,246,0.45);'>{bas_harfler}</div>"
        f"<div style='overflow:hidden;'>"
        f"<div style='font-weight:700; color:{metin}; white-space:nowrap; overflow:hidden; "
        f"text-overflow:ellipsis;'>{guvenli_metin(ad)}</div>"
        f"<div style='color:{ikincil}; font-size:0.78rem;'>Personel</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

    bugun = datetime.now().date()
    mevcut = [r["tarih"] for r in conn.execute(
        "SELECT DISTINCT tarih FROM rutin_loglari WHERE kullanici_adi = ? ORDER BY tarih DESC",
        (kullanici["kullanici_adi"],),
    ).fetchall()]

    # Takvim her zaman bugünden başlasın; gün geçtikçe otomatik olarak ilerler.
    st.sidebar.header(":material/calendar_month: Tarih")
    tarih_str = takvim_widget(mevcut, bugun, bugun)

    st.sidebar.divider()
    if st.sidebar.button("Çıkış Yap", icon=":material/logout:", width="stretch"):
        cikis(conn)

    # --- ANA İÇERİK ---
    st.title(f"Hoş geldin, {ad}")

    # --- TAKİP KONTROLÜ (kart) ---
    with st.container(border=True):
        st.subheader(":material/videocam: Takip Kontrolü")
        aktif = takip_aktif_mi(conn, kullanici["kullanici_adi"])
        if aktif:
            durum_satiri = conn.execute(
                "SELECT durum FROM canli_durum WHERE kullanici_adi = ?", (kullanici["kullanici_adi"],)
            ).fetchone()
            durum_etiket = db.DURUM_GORSEL.get(durum_satiri["durum"], ("aktif", "success"))[0] if durum_satiri else "aktif"
            st.success(f"Takip aktif — şu an: {durum_etiket}")
        else:
            st.info("Takip şu an kapalı.")

        if db.DB_PATH.startswith("/"):
            # Docker / LAN modu: kamera çalışanın kendi bilgisayarında çalışır.
            st.caption(
                "Kamera bu panelde değil, kendi bilgisayarınızda çalışır. "
                "Başlatmak için bilgisayarınızda `ajan\\kur.bat` (bir kez) ve "
                "`ajan\\RoutineLensAjan.bat` çalıştırın (`ajan_ayarlar.txt` içine SUNUCU ve KULLANICI yazın)."
            )
        else:
            baslat_kol, bitir_kol = st.columns(2)
            with baslat_kol:
                if st.button("Takibi Başlat", icon=":material/play_arrow:", type="primary", width="stretch", disabled=aktif):
                    pid = takip_baslat(conn, kullanici["kullanici_adi"])
                    st.success(f"Takip başlatıldı (PID {pid}). Kamera penceresi açılacak.")
                    st.rerun()
            with bitir_kol:
                if st.button("Takibi Bitir", icon=":material/stop:", width="stretch", disabled=not aktif):
                    takip_durdur(conn, kullanici["kullanici_adi"])
                    st.success("Takip durduruldu.")
                    st.rerun()

    ozet = kullanici_gunluk_ozet(conn, kullanici["kullanici_adi"], tarih_str)

    if ozet["olay_sayisi"] == 0:
        st.info(f"'{tarih_str}' için henüz sana ait kayıt yok. "
                f"'main.py --kullanici {kullanici['kullanici_adi']}' çalıştığında veriler burada görünür.")
        return

    skor = verimlilik_skoru(ozet["calisma"], ozet["dinlenme"], ozet["telefon"])

    # --- ODAK SKORU (kart) ---
    with st.container(border=True):
        st.subheader(":material/track_changes: Günlük Odak Skoru")
        st.markdown(
            f"<div style='text-align:center; font-size:4.2rem; font-weight:800; line-height:1.05; "
            f"letter-spacing:-0.03em;'>"
            f"<span style='color:{vurgu};'>{skor}</span>"
            f"<span style='color:{soluk}; font-size:1.6rem; font-weight:600;'>/100</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.progress(skor / 100)
        if skor >= 70:
            st.success("Mükemmel odak! Harika gidiyorsun.")
        elif skor >= 40:
            st.warning("İyi seviyede. Telefon veya dinlenme süreni biraz azaltabilirsin.")
        else:
            st.error("Odak seviyen düşük görünüyor. Daha fazla çalışmaya odaklan.")

    # --- ÖZET METRİKLERİ (kart) ---
    with st.container(border=True):
        st.subheader(":material/analytics: Kişisel Özet Metrikleri")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Çalışma", format_sure(ozet["calisma"]))
        m2.metric("Dinlenme", format_sure(ozet["dinlenme"]))
        m3.metric("Odak Kaybı", format_sure(ozet["odak_kaybi"]))
        m4.metric("Telefon", format_sure(ozet["telefon"]))

    # --- GRAFİKLER (kart) ---
    with st.container(border=True):
        st.subheader(":material/bar_chart: Kişisel Grafikler")
        grafik_turu = st.radio("Grafik türü", ["Bar", "Pie", "Çizgi"], horizontal=True)
        grafik_df = pd.DataFrame({
            "Kategori": ["Çalışma", "Dinlenme", "Odak Kaybı", "Telefon"],
            "Süre (dk)": [
                ozet["calisma"] / 60, ozet["dinlenme"] / 60,
                ozet["odak_kaybi"] / 60, ozet["telefon"] / 60,
            ],
        }).set_index("Kategori")
        if grafik_turu == "Pie":
            fig = kisisel_pasta_grafigi(grafik_df)
        elif grafik_turu == "Çizgi":
            fig = kisisel_cizgi_grafigi(grafik_df)
        else:
            fig = kisisel_grafik(grafik_df)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        toplam = ozet["calisma"] + ozet["dinlenme"] + ozet["odak_kaybi"] + ozet["telefon"]
        if toplam > 0:
            st.caption("Günün Dağılımı (oranlar)")
            for etiket, deger in [
                ("Çalışma", ozet["calisma"]), ("Dinlenme", ozet["dinlenme"]),
                ("Odak Kaybı", ozet["odak_kaybi"]), ("Telefon", ozet["telefon"]),
            ]:
                oran = deger / toplam
                st.write(f"{etiket}: {format_sure(deger)} (%{round(oran * 100)})")
                st.progress(oran)

    # --- ZAMAN ÇİZELGESİ (kart) ---
    with st.container(border=True):
        st.subheader(":material/schedule: Zaman Çizelgesi")
        df = pd.read_sql_query(
            "SELECT tarih, saat, durum, gecirilen_sure_sn FROM rutin_loglari "
            "WHERE kullanici_adi = ? AND tarih = ? ORDER BY saat",
            conn, params=(kullanici["kullanici_adi"], tarih_str),
        )
        df_display = df.copy()
        df_display["gecirilen_sure_sn"] = df_display["gecirilen_sure_sn"].apply(format_sure)
        df_display["tarih_saat"] = df_display["tarih"] + " " + df_display["saat"]
        st.dataframe(
            df_display[["tarih_saat", "durum", "gecirilen_sure_sn"]].rename(columns={
                "tarih_saat": "Tarih / Saat", "durum": "Durum", "gecirilen_sure_sn": "Süre",
            }),
            width="stretch",
        )
