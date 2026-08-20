# -*- coding: utf-8 -*-
"""Ajanın merkezi sunucuya JSON verisi göndermesi.

Yalnızca standart kütüphane kullanır (ek bağımlılık gerektirmez).
Görüntü/video asla gönderilmez; yalnızca durum ve süre bilgisi (JSON) gider.
"""
import json
import os
import urllib.request

# Varsayılan sunucu: ortam değişkeniyle ya da main.py --sunucu ile değiştirilebilir.
SUNUCU = (os.environ.get("ROUTINELENS_SUNUCU") or "http://127.0.0.1:8000").rstrip("/")


def _post(path, payload, timeout=5):
    """Belirtilen yola JSON POST atar; başarıda True, aksi halde False döner."""
    try:
        veri = json.dumps(payload).encode("utf-8")
        istek = urllib.request.Request(
            SUNUCU + path,
            data=veri,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(istek, timeout=timeout) as yanit:
            return yanit.status == 200
    except Exception:
        return False


def durum_gonder(kullanici, durum):
    """Canlı durumu (heartbeat) merkezi sunucuya yazar."""
    return _post("/api/status", {"kullanici": kullanici, "durum": durum})


def log_gonder(kullanici, tarih, saat, durum, sure_sn):
    """Tamamlanan bir durum segmentini merkezi sunucuya yazar."""
    return _post("/api/logs", {
        "kullanici": kullanici,
        "tarih": tarih,
        "saat": saat,
        "durum": durum,
        "sure": int(sure_sn),
    })


def cevrimdisi_gonder(kullanici):
    """Ajan kapanırken canlı durumu merkezi sunucudan temizler."""
    return _post("/api/offline", {"kullanici": kullanici, "durum": ""})
