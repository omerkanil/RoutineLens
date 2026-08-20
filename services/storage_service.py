# -*- coding: utf-8 -*-
"""Depolama limit kontrolü ve bildirim."""
import db
from database.settings import ayar_oku
from core.notifications import uyari_gonder_thread
def depo_kontrol(conn):
    """Video kaydedildikten sonra disk limitini kontrol eder.

    Limit dolmaya yakınsa kullanıcıya bildirim gönderir; limit aşılırsa
    en eski videoları FIFO mantığıyla otomatik siler.
    """
    try:
        sinir_gb = ayar_oku(conn, "depo_limit_gb", db.DEPO_LIMIT_GB_VARSAYILAN)
        omur_gun = ayar_oku(conn, "video_omur_gun", db.VIDEO_OMUR_GUN_VARSAYILAN)
        sinir_byte = int(sinir_gb) * 1024 * 1024 * 1024
        uyari = db.depo_uyari_mesaji(sinir_byte)
        if uyari:
            uyari_gonder_thread("Depolama Uyarısı", uyari)
        silinen, temizlenen = db.depo_temizle(sinir_byte, omur_gun)
        if silinen:
            print(f"[TEMIZLIK] {silinen} eski video silindi ({temizlenen / (1024 * 1024):.1f} MB).")
    except Exception:
        pass
