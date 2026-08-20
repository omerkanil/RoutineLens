# -*- coding: utf-8 -*-
"""RoutineLens — takip istemcisi (ince orkestratör).

Kamera döngüsünü yönetir; tespit -> VisionEngine, kayıt -> VideoRecorder,
veritabanı -> DatabaseManager tarafından yapılır.
"""
import os
import time
import argparse
from datetime import datetime

import cv2

from core.config import (
    KAYIT_KLASORU, GECICI_KLASOR, DURUM_KATEGORI,
    POMODORO_CALISMA_SN, MIN_KAYIT_SURESI_SN, MOLA_ONERISI_SN,
)
from core.notifications import uyari_gonder_thread, mola_uyarisi_thread
from core import remote
from database.manager import db_manager
from database.settings import ayar_oku
from database.logs import canli_durum_guncelle, canli_durum_sil
from vision.engine import VisionEngine
from vision.recorder import VideoRecorder

# Yeni durumun kayda geçmesi için arka arkaya kaç kare sabit kalması gerektiği.
# Titreme kaynaklı FFmpeg segment çakışmasını (FPS düşüşünü) önler.
DURUM_SABITLEME_KARE = 8


def main():
    parser = argparse.ArgumentParser(description="RoutineLens takip istemcisi")
    parser.add_argument("--kullanici", type=str, default="genel",
                        help="Verilerin hangi kullanıcıya yazılacağı (varsayılan: genel)")
    parser.add_argument("--sunucu", type=str, default="",
                        help="Merkezi sunucu adresi (örn: http://192.168.1.10:8000)")
    args = parser.parse_args()
    kullanici_adi = (args.kullanici or "").strip() or "genel"
    if args.sunucu:
        remote.SUNUCU = args.sunucu.rstrip("/")

    os.makedirs("logs", exist_ok=True)
    tarih_str = datetime.now().strftime('%Y-%m-%d')
    log_txt = f"logs/rutin_raporu_{tarih_str}.txt"

    conn = db_manager.init_db()
    cursor = conn.cursor()

    # Modeller yüklenmeden önce canlı durumu yaz; böylece model yükleme süresi
    # boyunca panel takibi "aktif" görür (son_guncelleme taze kalır).
    canli_durum_guncelle(conn, kullanici_adi, "Başlatılıyor")

    # Merkezi sunucuya da bildir (LAN kurulumu). Ulaşılamazsa ajan yerelde çalışmaya devam eder.
    if not remote.durum_gonder(kullanici_adi, "Başlatılıyor"):
        print(f"[UYARI] Merkezi sunucuya ulaşılamadı ({remote.SUNUCU}). Veriler yalnızca yerelde tutulacak.")

    # --- KULLANICI AYARLARINI OKU (dashboard'dan değiştirilebilir) ---
    pomodoro_sn = ayar_oku(conn, "pomodoro_calisma_sn", POMODORO_CALISMA_SN)
    min_kayit_sn = ayar_oku(conn, "min_kayit_suresi_sn", MIN_KAYIT_SURESI_SN)
    son_ayar_okuma_zamani = 0.0

    # --- ÇİFT MOTORLU YAPAY ZEKA MODELLERİ (bir kez yüklenir) ---
    print("[INFO] Yapay zeka modelleri yukleniyor (Pose & Object)...")
    engine = VisionEngine()

    cap = cv2.VideoCapture(0)
    window_name = "RoutineLens - Dual AI & SQLite Edition"

    onceki_durum = "Masada Yok (Away)"
    durum_baslangic_zamani = time.time()

    # --- DURUM SABİTLEME (debounce) değişkenleri ---
    bekleyen_durum = "Masada Yok (Away)"
    bekleyen_sayac = 0

    kambur_araliksiz_sayac = 0
    son_bildirim_zamani = 0

    # --- POMODORO / MOLA YÖNETİMİ DEĞİŞKENLERİ ---
    kesintisiz_calisma_sn = 0.0
    son_kare_zamani = time.time()
    mola_modu_aktif = False

    # --- VİDEO KAYIT KLASÖRLERİNİ OLUŞTUR (kişi bazlı) ---
    os.makedirs(KAYIT_KLASORU, exist_ok=True)
    os.makedirs(GECICI_KLASOR, exist_ok=True)
    kullanici_klasoru = os.path.join(KAYIT_KLASORU, kullanici_adi)
    for kat in set(DURUM_KATEGORI.values()):
        os.makedirs(os.path.join(kullanici_klasoru, kat), exist_ok=True)

    # Önceki çalışmadan kalan geçici dosyaları temizle
    for eski in os.listdir(GECICI_KLASOR):
        try:
            os.remove(os.path.join(GECICI_KLASOR, eski))
        except Exception:
            pass

    recorder = VideoRecorder(kullanici_klasoru, conn)
    son_canli_guncelleme = 0.0

    print("[INFO] RoutineLens baslatildi. Cift motor ve SQLite devrede!")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # --- POMODORO ZAMAN SAYACI ---
        simdiki_zaman = time.time()
        delta = simdiki_zaman - son_kare_zamani
        son_kare_zamani = simdiki_zaman

        # --- KULLANICI AYARLARINI PERİYODİK GÜNCELLE (5 sn'de bir) ---
        if simdiki_zaman - son_ayar_okuma_zamani > 5:
            pomodoro_sn = ayar_oku(conn, "pomodoro_calisma_sn", POMODORO_CALISMA_SN)
            min_kayit_sn = ayar_oku(conn, "min_kayit_suresi_sn", MIN_KAYIT_SURESI_SN)
            son_ayar_okuma_zamani = simdiki_zaman

        sonuc = engine.tespit(frame, kambur_araliksiz_sayac)
        current_state = sonuc.current_state
        text_color = sonuc.text_color
        postur_durumu = sonuc.postur_durumu
        postur_renk = sonuc.postur_renk
        annotated_frame = sonuc.annotated_frame
        kambur_araliksiz_sayac = sonuc.kambur_sayac

        # --- CANLI DURUMU VERİTABANINA YAZ (2 sn'de bir veya durum değişince) ---
        if simdiki_zaman - son_canli_guncelleme > 2 or current_state != onceki_durum:
            canli_durum_guncelle(conn, kullanici_adi, current_state)
            remote.durum_gonder(kullanici_adi, current_state)
            son_canli_guncelleme = simdiki_zaman

        # --- POMODORO / MOLA YÖNETİMİ ---
        if current_state == "Calisiyor (Working)":
            kesintisiz_calisma_sn += delta
            if kesintisiz_calisma_sn >= pomodoro_sn and not mola_modu_aktif:
                mola_uyarisi_thread(
                    "Pomodoro Tamamlandı!",
                    f"{pomodoro_sn // 60} dakika kesintisiz calistin. {MOLA_ONERISI_SN // 60} dakika mola ver ve gozlerini dinlendir."
                )
                mola_modu_aktif = True
                kesintisiz_calisma_sn = 0.0
        else:
            kesintisiz_calisma_sn = 0.0
            mola_modu_aktif = False

        # POSTÜR BİLDİRİMİ
        if kambur_araliksiz_sayac > 100:
            if (time.time() - son_bildirim_zamani) > 60:
                uyari_gonder_thread("Postür Uyarısı!", "Uzun süredir kambur çalışıyorsun. Lütfen dikleş.")
                son_bildirim_zamani = time.time()

        # DURUM DEĞİŞİMİ VE VERİTABANINA YAZMA (debounce: yeni durum N kare sabit kalmalı)
        if current_state != onceki_durum:
            if current_state == bekleyen_durum:
                bekleyen_sayac += 1
            else:
                bekleyen_durum = current_state
                bekleyen_sayac = 1

            if bekleyen_sayac >= DURUM_SABITLEME_KARE:
                gecen_sure = int(time.time() - durum_baslangic_zamani)
                su_an = datetime.now().strftime("%H:%M:%S")

                if gecen_sure > 2:
                    log_metni = f"[{su_an}] {onceki_durum} sona erdi. (Sure: {gecen_sure} sn) -> YENI DURUM: {current_state}\n"
                    print(log_metni.strip())
                    with open(log_txt, "a", encoding="utf-8") as f:
                        f.write(log_metni)

                    cursor.execute('''
                        INSERT INTO rutin_loglari (tarih, saat, durum, gecirilen_sure_sn, kullanici_adi)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (tarih_str, su_an, onceki_durum, gecen_sure, kullanici_adi))
                    conn.commit()
                    remote.log_gonder(kullanici_adi, tarih_str, su_an, onceki_durum, gecen_sure)

                onceki_durum = current_state
                durum_baslangic_zamani = time.time()
                kambur_araliksiz_sayac = 0
                bekleyen_durum = current_state
                bekleyen_sayac = 0
        else:
            # Durum sabit; bekleyen sayacı sıfırla
            bekleyen_durum = current_state
            bekleyen_sayac = 0

        # EKRANA YAZDIRMA
        anlik_gecen_sure = int(time.time() - durum_baslangic_zamani)
        cv2.putText(annotated_frame, f"Durum: {current_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        cv2.putText(annotated_frame, f"Sure: {anlik_gecen_sure} sn", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        if current_state == "Calisiyor (Working)":
            cv2.putText(annotated_frame, f"Postur: {postur_durumu}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, postur_renk, 2)

        # Pomodoro ilerleme göstergesi
        pomodoro_dk = int(kesintisiz_calisma_sn // 60)
        pomodoro_hedef_dk = pomodoro_sn // 60
        cv2.putText(annotated_frame, f"Pomodoro: {pomodoro_dk} dk / {pomodoro_hedef_dk} dk", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        if mola_modu_aktif:
            cv2.rectangle(annotated_frame, (10, 180), (760, 220), (0, 0, 0), -1)
            cv2.putText(annotated_frame, "MOLA MODU AKTIF - Gozlerini Dinlendir!", (20, 208), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # --- VİDEO KAYIT (duruma göre kategoriye yaz, normal hız) ---
        kategori = DURUM_KATEGORI.get(onceki_durum, "odak_kaybi")
        recorder.kategori_degistir(kategori, frame, min_kayit_sn)
        recorder.kare_yaz(frame, delta)

        cv2.imshow(window_name, annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            gecen_sure = int(time.time() - durum_baslangic_zamani)
            su_an = datetime.now().strftime("%H:%M:%S")
            cursor.execute('''
                INSERT INTO rutin_loglari (tarih, saat, durum, gecirilen_sure_sn, kullanici_adi)
                VALUES (?, ?, ?, ?, ?)
            ''', (tarih_str, su_an, onceki_durum, gecen_sure, kullanici_adi))
            conn.commit()
            remote.log_gonder(kullanici_adi, tarih_str, su_an, onceki_durum, gecen_sure)
            break

    recorder.kapat(min_kayit_sn)

    cap.release()
    # Çıkışta canlı durumu temizle (admin monitörde hemen çevrimdışı görünsün)
    try:
        canli_durum_sil(conn, kullanici_adi)
    except Exception:
        pass
    conn.close()
    remote.cevrimdisi_gonder(kullanici_adi)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

