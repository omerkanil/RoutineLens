# -*- coding: utf-8 -*-
"""Disk/depolama yönetimi (DoS koruması)."""
import os
import time

from core.config import KAYIT_KLASORU, DEPO_LIMIT_GB_VARSAYILAN, VIDEO_OMUR_GUN_VARSAYILAN
def depo_boyutu(kok=None):
    """kayitlar klasörünün toplam video boyutunu (byte) döndürür."""
    kok = kok or KAYIT_KLASORU
    toplam = 0
    if not os.path.isdir(kok):
        return 0
    for dizin, _, dosyalar in os.walk(kok):
        if "_gecici" in dizin.split(os.sep):
            continue
        for ad in dosyalar:
            if not ad.lower().endswith(".mp4"):
                continue
            try:
                toplam += os.path.getsize(os.path.join(dizin, ad))
            except OSError:
                continue
    return toplam


def depo_temizle(max_byte=None, omur_gun=None):
    """FIFO mantığıyla en eski videoları otomatik siler.

    - omur_gun gününden eski dosyalar silinir.
    - Toplam boyut max_byte'ı aşarsa, en eskiden başlayarak limitin
      altına inene kadar silinir.
    Döndürür: (silinen_dosya_sayisi, temizlenen_byte)
    """
    if max_byte is None:
        max_byte = DEPO_LIMIT_GB_VARSAYILAN * 1024 * 1024 * 1024
    if omur_gun is None:
        omur_gun = VIDEO_OMUR_GUN_VARSAYILAN

    kok = os.path.abspath(KAYIT_KLASORU)
    if not os.path.isdir(kok):
        return 0, 0

    simdi = time.time()
    omur_sn = int(omur_gun) * 24 * 3600

    dosyalar = []
    for dizin, _, dosya_listesi in os.walk(kok):
        if "_gecici" in dizin.split(os.sep):
            continue
        for ad in dosya_listesi:
            if not ad.lower().endswith(".mp4"):
                continue
            yol = os.path.join(dizin, ad)
            try:
                boyut = os.path.getsize(yol)
                mtime = os.path.getmtime(yol)
            except OSError:
                continue
            dosyalar.append((yol, boyut, mtime))

    dosyalar.sort(key=lambda x: x[2])  # en eskiden en yeniye (FIFO)

    toplam = sum(b for _, b, _ in dosyalar)
    silinen_sayisi = 0
    temizlenen_byte = 0

    for yol, boyut, mtime in dosyalar:
        eskimi = (simdi - mtime) > omur_sn
        tasma = toplam > max_byte
        if not eskimi and not tasma:
            break
        try:
            os.remove(yol)
            silinen_sayisi += 1
            temizlenen_byte += boyut
            toplam -= boyut
        except OSError:
            continue

    return silinen_sayisi, temizlenen_byte


def depo_uyari_mesaji(max_byte=None, esik_oran=0.9):
    """Depolama limit dolmaya yakınsa uyarı mesajı döndürür; değilse None."""
    if max_byte is None:
        max_byte = DEPO_LIMIT_GB_VARSAYILAN * 1024 * 1024 * 1024
    toplam = depo_boyutu()
    if max_byte <= 0:
        return None
    oran = toplam / max_byte
    if oran >= esik_oran:
        return (
            f"Depolama uyarısı: video klasörü %{int(oran * 100)} dolu "
            f"({toplam / (1024 ** 3):.2f} GB / {max_byte / (1024 ** 3):.2f} GB)."
        )
    return None
