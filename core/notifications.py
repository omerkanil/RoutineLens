# -*- coding: utf-8 -*-
"""Masaüstü bildirimleri (thread tabanlı)."""
import threading
from plyer import notification


def uyari_gonder_thread(baslik, mesaj):
    def gonder():
        try:
            notification.notify(
                title=baslik,
                message=mesaj,
                app_name="RoutineLens",
                timeout=4
            )
        except Exception:
            pass
    threading.Thread(target=gonder).start()


def mola_uyarisi_thread(baslik, mesaj):
    def gonder():
        try:
            notification.notify(
                title=baslik,
                message=mesaj,
                app_name="RoutineLens",
                timeout=6
            )
        except Exception:
            pass
        try:
            import winsound
            winsound.Beep(880, 250)
            winsound.Beep(660, 250)
        except Exception:
            pass
    threading.Thread(target=gonder).start()
