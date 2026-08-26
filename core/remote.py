# -*- coding: utf-8 -*-
"""Ajanın merkezi sunucuya JSON verisi göndermesi (arayüzü BLOKE ETMEZ).

Gönderimler arka plan iş parçacığında yapılır; kamera döngüsü ağa asla takılmaz.
Bu sayede sunucu erişilemez veya yavaş olsa bile FPS düşmez.
Yalnızca standart kütüphane kullanır; görüntü/video asla gönderilmez.
"""
import json
import os
import queue
import threading
import urllib.request

# Varsayılan sunucu: ortam değişkeniyle ya da main.py --sunucu ile değiştirilebilir.
SUNUCU = (os.environ.get("ROUTINELENS_SUNUCU") or "http://127.0.0.1:8000").rstrip("/")

# Ağ isteği zaman aşımı (sn). Arka planda olduğu için kamera döngüsünü etkilemez.
_TIMEOUT = 3

# Gönderim kuyruğu: ana döngü yalnızca mesaj bırakır, asla beklemez.
_kuyruk = queue.Queue()
_isci_thread = None
_kilit = threading.Lock()


def _post(yol, payload, timeout=_TIMEOUT):
    """Belirtilen yola JSON POST atar; başarıda True döner."""
    try:
        veri = json.dumps(payload).encode("utf-8")
        istek = urllib.request.Request(
            SUNUCU + yol,
            data=veri,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(istek, timeout=timeout) as yanit:
            return yanit.status == 200
    except Exception:
        return False


def _isci():
    """Kuyruktaki gönderimleri arka planda işler."""
    while True:
        yol, payload = _kuyruk.get()
        if yol is None:  # durdurma sinyali (daemon olduğu için normalde kullanılmaz)
            return
        _post(yol, payload)


def _isciyi_baslat():
    global _isci_thread
    with _kilit:
        if _isci_thread is None or not _isci_thread.is_alive():
            _isci_thread = threading.Thread(target=_isci, daemon=True, name="routine-remote")
            _isci_thread.start()


def _kuyruga_at(yol, payload):
    _isciyi_baslat()
    _kuyruk.put((yol, payload))  # sınırsız kuyruk: asla bloke etmez


def sunucu_hazir():
    """Sunucuya EŞZAMANLI hızlı sağlık kontrolü (yalnızca başlangıçta çağrılır)."""
    try:
        with urllib.request.urlopen(SUNUCU + "/api/health", timeout=2) as yanit:
            return yanit.status == 200
    except Exception:
        return False


def durum_gonder(kullanici, durum):
    """Canlı durumu (heartbeat) arka plana kuyruklar; dönüşü beklemez."""
    _kuyruga_at("/api/status", {"kullanici": kullanici, "durum": durum})
    return True


def log_gonder(kullanici, tarih, saat, durum, sure_sn):
    """Tamamlanan durum segmentini arka plana kuyruklar."""
    _kuyruga_at("/api/logs", {
        "kullanici": kullanici,
        "tarih": tarih,
        "saat": saat,
        "durum": durum,
        "sure": int(sure_sn),
    })
    return True


def cevrimdisi_gonder(kullanici):
    """Ajan kapanırken canlı durumu EŞZAMANLI temizler (döngüde değiliz)."""
    return _post("/api/offline", {"kullanici": kullanici, "durum": ""})
