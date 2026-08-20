# -*- coding: utf-8 -*-
"""RoutineLens — merkezi REST API (FastAPI).

Ajanlar (main.py) görüntü GÖNDERMEZ; yalnızca JSON durum/log verisi yollar.
Bu servis gelen veriyi sunucudaki SQLite'a yazar. Dashboard aynı dosyayı okur.
"""
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from database.manager import db_manager
from database.logs import canli_durum_guncelle, canli_durum_sil

app = FastAPI(title="RoutineLens API", version="1.0.0")


class DurumMesaji(BaseModel):
    kullanici: str
    durum: str = ""


class LogMesaji(BaseModel):
    kullanici: str
    tarih: str
    saat: str
    durum: str
    sure: int


# Şemayı bir kez kur (idempotent). Dosya yoksa oluşturur.
db_manager.schema_kur()


@app.get("/api/health")
def saglik():
    return {"ok": True, "zaman": datetime.now().isoformat()}


@app.post("/api/status")
def durum_guncelle(m: DurumMesaji):
    conn = db_manager.baglan()
    try:
        canli_durum_guncelle(conn, m.kullanici, m.durum)
        return {"ok": True}
    finally:
        conn.close()


@app.post("/api/logs")
def log_yaz(m: LogMesaji):
    conn = db_manager.baglan()
    try:
        conn.execute(
            "INSERT INTO rutin_loglari (tarih, saat, durum, gecirilen_sure_sn, kullanici_adi) "
            "VALUES (?, ?, ?, ?, ?)",
            (m.tarih, m.saat, m.durum, m.sure, m.kullanici),
        )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@app.post("/api/offline")
def cevrimdisi(m: DurumMesaji):
    conn = db_manager.baglan()
    try:
        canli_durum_sil(conn, m.kullanici)
        return {"ok": True}
    finally:
        conn.close()
