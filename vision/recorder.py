# -*- coding: utf-8 -*-
"""VideoRecorder: durum değişimlerine göre segment kaydı."""
import os
import threading
import time
from datetime import datetime

import cv2

from core.config import GECICI_KLASOR, KAYIT_FPS
from core.media import FfmpegVideoYazici
from services.storage_service import depo_kontrol


class _Cv2Yazici:
    """ffmpeg bulunamazsa cv2.VideoWriter (mp4v) geri dönüşü."""

    def __init__(self, yol, genislik, yukseklik):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(yol, fourcc, KAYIT_FPS, (genislik, yukseklik))

    def hazir(self):
        return self.writer is not None and self.writer.isOpened()

    def yaz(self, frame):
        if self.writer is not None:
            self.writer.write(frame)

    def kapat(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None


def _yazici_olustur(yol, genislik, yukseklik):
    """FFmpeg varsa tek geçişli H.264 yazıcı, yoksa cv2.VideoWriter geri dönüşü."""
    yazici = FfmpegVideoYazici(yol, genislik, yukseklik, KAYIT_FPS)
    if yazici.hazir():
        return yazici
    return _Cv2Yazici(yol, genislik, yukseklik)


class VideoRecorder:
    """Segment yaşam döngüsünü yönetir; ffmpeg ile tek geçişte H.264 yazar.

    Geçici dosyaya yazar; kategori değiştiğinde veya çıkışta segmenti kapatır,
    yeterince uzunsa kalıcı klasöre taşır (depo kontrolü dahil).
    """

    def __init__(self, kullanici_klasoru, conn):
        self.kullanici_klasoru = kullanici_klasoru
        self.conn = conn
        self.writer = None
        self.kategori = None
        self.sayac = 0
        self.baslangic = time.time()
        self.baslangic_str = None
        self.gecici_yol = None
        self.bekleyen_kare = 0.0
        self._depo_bekliyor = False

    def _kapat_segment(self, min_kayit_sn, senkron=False):
        if self.writer is None:
            return
        writer = self.writer
        self.writer = None
        kayit_suresi = time.time() - self.baslangic
        gecici_yol = self.gecici_yol
        kategori = self.kategori
        baslangic_str = self.baslangic_str
        sayac = self.sayac

        def finalize():
            writer.kapat()
            if kayit_suresi >= min_kayit_sn:
                final_yol = os.path.join(
                    self.kullanici_klasoru, kategori,
                    f"{baslangic_str}_{sayac:03d}.mp4",
                )
                try:
                    os.replace(gecici_yol, final_yol)
                    print(f"[KAYIT] {kategori} -> {os.path.basename(final_yol)} ({kayit_suresi:.1f} sn)")
                    self._depo_bekliyor = True
                except Exception:
                    pass
            else:
                try:
                    os.remove(gecici_yol)
                    print(f"[KAYIT] Kısa segment kaydedilmedi ({kayit_suresi:.1f} sn < {min_kayit_sn} sn)")
                except Exception:
                    pass

        if senkron:
            finalize()
        else:
            threading.Thread(target=finalize, daemon=True).start()

    def _depo_kontrolu_yap(self):
        """Ertelenen depo kontrolünü ana iş parçacığında çalıştırır (thread güvenli)."""
        if self._depo_bekliyor:
            self._depo_bekliyor = False
            depo_kontrol(self.conn)

    def kategori_degistir(self, yeni_kategori, frame, min_kayit_sn):
        """Kategori değiştiyse önceki segmenti kapatıp yenisini başlatır."""
        if yeni_kategori == self.kategori:
            return
        self._kapat_segment(min_kayit_sn)
        self.sayac += 1
        self.baslangic = time.time()
        self.baslangic_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.gecici_yol = os.path.join(GECICI_KLASOR, f"gecici_{self.sayac:03d}.mp4")
        yukseklik, genislik = frame.shape[:2]
        self.writer = _yazici_olustur(self.gecici_yol, genislik, yukseklik)
        self.kategori = yeni_kategori
        self.bekleyen_kare = 0.0

    def kare_yaz(self, frame, delta):
        """Gerçek geçen süreye göre kare yazar (kare tekrarı)."""
        self._depo_kontrolu_yap()
        if self.writer is not None:
            self.bekleyen_kare += delta * KAYIT_FPS
            while self.bekleyen_kare >= 1.0:
                self.writer.yaz(frame)
                self.bekleyen_kare -= 1.0

    def kapat(self, min_kayit_sn):
        """Çıkışta son segmenti senkron kapatır."""
        self._kapat_segment(min_kayit_sn, senkron=True)
        self._depo_kontrolu_yap()
