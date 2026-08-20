# -*- coding: utf-8 -*-
"""Video format dönüştürme (ffmpeg)."""
import os
import shutil
import subprocess

import numpy as np

from core.config import GECICI_KLASOR


def ffmpeg_exe():
    """Sistemdeki ffmpeg yolunu döndürür; yoksa imageio-ffmpeg'e düşer."""
    yol = shutil.which("ffmpeg")
    if yol:
        return yol
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


class FfmpegVideoYazici:
    """Ham BGR kareleri ffmpeg'e borular, tek geçişte H.264 MP4 üretir.

    cv2.VideoWriter (mp4v) + sonradan h264_cevir iki geçişli akışının yerini
    alır: daha küçük dosya, tek geçiş, doğrudan tarayıcıda oynatılabilir.
    """

    def __init__(self, yol, genislik, yukseklik, fps):
        self.surec = None
        exe = ffmpeg_exe()
        if not exe:
            return
        komut = [
            exe, "-y",
            "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", f"{genislik}x{yukseklik}", "-r", str(fps),
            "-i", "-",
            "-an",
            "-c:v", "libx264", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            yol,
        ]
        try:
            self.surec = subprocess.Popen(
                komut,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            self.surec = None

    def hazir(self):
        return self.surec is not None and self.surec.poll() is None

    def yaz(self, frame):
        if self.hazir():
            try:
                self.surec.stdin.write(np.ascontiguousarray(frame).tobytes())
            except Exception:
                pass

    def kapat(self):
        if self.surec is None:
            return
        try:
            if self.surec.stdin:
                self.surec.stdin.close()
        except Exception:
            pass
        try:
            self.surec.wait(timeout=30)
        except Exception:
            try:
                self.surec.kill()
            except Exception:
                pass
        self.surec = None


def h264_cevir(video_yolu):
    """mp4v ile kaydedilen klibi tarayıcıda oynatılabilir H.264 formatına dönüştürür."""
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return  # imageio-ffmpeg yoksa klip mp4v olarak kalır
    os.makedirs(GECICI_KLASOR, exist_ok=True)
    gecici = os.path.join(GECICI_KLASOR, f"donustur_{os.path.basename(video_yolu)}")
    try:
        komut = [
            ffmpeg, "-y", "-i", video_yolu,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "veryfast", "-movflags", "+faststart",
            gecici,
        ]
        sonuc = subprocess.run(komut, capture_output=True)
        if sonuc.returncode == 0 and os.path.exists(gecici) and os.path.getsize(gecici) > 0:
            os.replace(gecici, video_yolu)
        elif os.path.exists(gecici):
            os.remove(gecici)
    except Exception:
        if os.path.exists(gecici):
            try:
                os.remove(gecici)
            except Exception:
                pass
