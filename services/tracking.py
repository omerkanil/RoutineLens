# -*- coding: utf-8 -*-
"""Takip süreç yönetimi (main.py başlat/durdur)."""
import os
import subprocess
import sys
import signal
from datetime import datetime

import db
from core.config import CEVRIMDISI_ESIK_SN, MAIN_PY, PROJE_DIZINI
def takip_aktif_mi(conn, kullanici_adi):
    satir = conn.execute(
        "SELECT son_guncelleme FROM canli_durum WHERE kullanici_adi = ?", (kullanici_adi,)
    ).fetchone()
    if satir is None:
        return False
    try:
        son = datetime.strptime(satir["son_guncelleme"], "%Y-%m-%d %H:%M:%S")
        return (datetime.now() - son).total_seconds() < CEVRIMDISI_ESIK_SN
    except Exception:
        return False


def surec_sonlandir(pid):
    try:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
        return True
    except Exception:
        pass
    try:
        os.kill(pid, signal.SIGTERM)
        return True
    except Exception:
        return False


def takip_baslat(conn, kullanici_adi):
    os.makedirs("logs", exist_ok=True)
    log_dosyasi = os.path.join("logs", f"takip_{kullanici_adi}.log")
    with open(log_dosyasi, "a", encoding="utf-8") as logf:
        proc = subprocess.Popen(
            [sys.executable, MAIN_PY, "--kullanici", kullanici_adi],
            stdout=logf, stderr=logf, cwd=PROJE_DIZINI,
        )
    db.surec_kaydet(conn, kullanici_adi, proc.pid)
    # Takip başlar başlamaz panelde "aktif" görünsün diye canlı durumu hemen yaz.
    # (main.py modelleri yükleyene kadar canli_durum boş kaldığı için arayüz
    #  "kapalı" gösteriyor ve "Takibi Bitir" butonu aktif olmuyordu.)
    db.canli_durum_guncelle(conn, kullanici_adi, "Başlatılıyor")
    return proc.pid


def takip_durdur(conn, kullanici_adi):
    pid = db.surec_oku(conn, kullanici_adi)
    if pid:
        surec_sonlandir(pid)
    db.surec_sil(conn, kullanici_adi)
    db.canli_durum_sil(conn, kullanici_adi)
