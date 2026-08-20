# -*- coding: utf-8 -*-
"""Analitik ve veri sorguları."""
import os

import pandas as pd

import db
from core.config import KATEGORI_ANAHTARLARI
def format_sure(saniye):
    if saniye < 60:
        return f"{int(saniye)} sn"
    elif saniye < 3600:
        dakika = saniye // 60
        kalan = saniye % 60
        return f"{dakika} dk {kalan} sn" if kalan else f"{dakika} dk"
    else:
        saat = saniye // 3600
        dakika = (saniye % 3600) // 60
        return f"{saat} saat {dakika} dk" if dakika else f"{saat} saat"


def verimlilik_skoru(calisma_sn, dinlenme_sn, telefon_sn):
    toplam = calisma_sn + dinlenme_sn + telefon_sn
    if toplam <= 0:
        return 0
    return int(round((calisma_sn / toplam) * 100))


def dost_isim(dosya_adi):
    ad = os.path.splitext(dosya_adi)[0]
    parcalar = ad.split("_")
    if len(parcalar) >= 2:
        tarih, saat = parcalar[0], parcalar[1]
        if len(tarih) == 8 and len(saat) == 6:
            return f"{tarih[6:8]}.{tarih[4:6]}.{tarih[0:4]}---{saat[0:2]}.{saat[2:4]}.{saat[4:6]}"
    return dosya_adi


def kullanici_adi_goster(k):
    return k


def video_envanteri():
    envanter = {}
    if not os.path.isdir(db.KAYIT_KLASORU):
        return envanter
    for girdi in sorted(os.listdir(db.KAYIT_KLASORU)):
        yol = os.path.join(db.KAYIT_KLASORU, girdi)
        if not os.path.isdir(yol) or girdi.startswith("_"):
            continue
        # Eski "genel" kayıtlar doğrudan kategori klasörlerindeydi; onları yok say.
        if girdi in KATEGORI_ANAHTARLARI:
            continue
        for kat in KATEGORI_ANAHTARLARI:
            kat_yolu = os.path.join(yol, kat)
            if os.path.isdir(kat_yolu):
                videolar = sorted(f for f in os.listdir(kat_yolu) if f.endswith(".mp4"))
                if videolar:
                    envanter.setdefault(girdi, {})[kat] = videolar
    return envanter


def kullanici_gunluk_ozet(conn, kullanici_adi, tarih_str):
    satir = conn.execute("""
        SELECT
            SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS calisma,
            SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS dinlenme,
            SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS telefon,
            SUM(CASE WHEN durum IN (?, ?) THEN gecirilen_sure_sn ELSE 0 END) AS odak_kaybi,
            COUNT(*) AS olay_sayisi
        FROM rutin_loglari
        WHERE kullanici_adi = ? AND tarih = ?
    """, (db.DURUM_CALISMA, db.DURUM_DINLENME, db.DURUM_TELEFON,
          *db.ODAK_KAYBI_DURUMLAR, kullanici_adi, tarih_str)).fetchone()
    return {
        "calisma": satir["calisma"] or 0,
        "dinlenme": satir["dinlenme"] or 0,
        "telefon": satir["telefon"] or 0,
        "odak_kaybi": satir["odak_kaybi"] or 0,
        "olay_sayisi": satir["olay_sayisi"] or 0,
    }


def liderlik_df(conn, baslangic_tarih):
    return pd.read_sql_query("""
        SELECT kullanici_adi AS kullanici,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS calisma_sn,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS telefon_sn,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) AS dinlenme_sn
        FROM rutin_loglari
        WHERE tarih >= ? AND kullanici_adi IS NOT NULL AND kullanici_adi != 'genel'
        GROUP BY kullanici_adi
        ORDER BY calisma_sn DESC
    """, conn, params=(db.DURUM_CALISMA, db.DURUM_TELEFON, db.DURUM_DINLENME, baslangic_tarih))


def saatlik_df(conn, tarih):
    return pd.read_sql_query("""
        SELECT CAST(substr(saat, 1, 2) AS INTEGER) AS saat_dilimi,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) / 60.0 AS calisma_dk,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) / 60.0 AS telefon_dk
        FROM rutin_loglari
        WHERE tarih = ? AND kullanici_adi IS NOT NULL AND kullanici_adi != 'genel'
        GROUP BY saat_dilimi
        ORDER BY saat_dilimi
    """, conn, params=(db.DURUM_CALISMA, db.DURUM_TELEFON, tarih))


def gunluk_trend_df(conn):
    return pd.read_sql_query("""
        SELECT tarih, kullanici_adi AS kullanici,
               SUM(CASE WHEN durum = ? THEN gecirilen_sure_sn ELSE 0 END) / 60.0 AS calisma_dk
        FROM rutin_loglari
        WHERE kullanici_adi IS NOT NULL AND kullanici_adi != 'genel'
        GROUP BY tarih, kullanici_adi
        ORDER BY tarih
    """, conn, params=(db.DURUM_CALISMA,))
