# -*- coding: utf-8 -*-
"""Ajan kontrolcüsü: sunucudaki komutlara göre kamerayı başlatır/durdurur.

Dashboard'daki "Takibi Başlat / Takibi Bitir" butonları komutu sunucuya yazar;
bu kontrolcü komutu okuyup kamerayı (main.py) açar/kapatır.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

SUNUCU = (os.environ.get("ROUTINELENS_SUNUCU") or "http://localhost:8000").rstrip("/")

_proc = None


def _komutlari_al():
    try:
        with urllib.request.urlopen(SUNUCU + "/api/komutlar", timeout=5) as r:
            return json.loads(r.read().decode("utf-8")).get("komutlar", [])
    except Exception:
        return []


def _kamera_baslat(kullanici):
    global _proc
    if _proc is not None and _proc.poll() is None:
        return
    os.makedirs("logs", exist_ok=True)
    logf = open(f"logs/takip_{kullanici}.log", "a", encoding="utf-8")
    _proc = subprocess.Popen(
        [sys.executable, "main.py", "--kullanici", kullanici, "--sunucu", SUNUCU],
        stdout=logf, stderr=logf,
    )
    print(f"[KONTROL] Kamera baslatildi: {kullanici}")


def _kamera_durdur():
    global _proc
    if _proc is not None and _proc.poll() is None:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(_proc.pid)], capture_output=True)
        print("[KONTROL] Kamera durduruldu")
    _proc = None


def main():
    print(f"[KONTROL] Ajan kontrolcusu calisiyor - sunucu: {SUNUCU}")
    print("[KONTROL] Kamerayi acmak icin panelde 'Takibi Baslat' butonuna basin.")
    while True:
        try:
            for k in _komutlari_al():
                komut = k.get("komut")
                kullanici = k.get("kullanici", "genel")
                if komut == "baslat":
                    _kamera_baslat(kullanici)
                elif komut == "durdur":
                    _kamera_durdur()
        except Exception:
            pass
        time.sleep(3)


if __name__ == "__main__":
    main()
