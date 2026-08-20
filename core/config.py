# -*- coding: utf-8 -*-
"""RoutineLens — merkezi sabitler ve yapılandırma (tek doğruluk kaynağı)."""
import os

# .env dosyasını yükle (varsa). python-dotenv yüklü değilse sistem ortam
# değişkenleri olduğu gibi kullanılır; bu sayede uygulama dotenv olmadan da çalışır.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Yollar ---
# Ortam değişkeniyle ezilebilir (Docker kurulumunda /data altına yönlendirilir).
DB_PATH = os.getenv("ROUTINELENS_DB", "routinelens.db")
KAYIT_KLASORU = os.getenv("ROUTINELENS_KAYIT", "kayitlar")
GECICI_KLASOR = os.path.join(KAYIT_KLASORU, "_gecici")

# --- Güvenlik ---
# İlk kurulumda oluşturulan varsayılan yönetici (admin) şifresi.
# GÜVENLİK: Varsayılan değer yalnızca geliştirme içindir; .env ile değiştirin.
VARSAYILAN_ADMIN_SIFRE = os.getenv("ROUTINELENS_ADMIN_SIFRE", "admin123")

PROJE_DIZINI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PY = os.path.join(PROJE_DIZINI, "main.py")

# --- Ekran etiketi -> kayıt klasörü anahtarı ---
DURUM_KATEGORI = {
    "Calisiyor (Working)": "calisiyor",
    "Telefonda Vakit Geciriyor": "telefonda",
    "Dinleniyor / Uyukluyor (Resting)": "dinleniyor",
    "Odak Kaybi / Arkasi Donuk": "odak_kaybi",
    "Masada Yok (Away)": "odak_kaybi",
}

# --- Sorgularda kullanılan sabit durum etiketleri ---
DURUM_CALISMA = "Calisiyor (Working)"
DURUM_DINLENME = "Dinleniyor / Uyukluyor (Resting)"
DURUM_TELEFON = "Telefonda Vakit Geciriyor"
ODAK_KAYBI_DURUMLAR = ("Odak Kaybi / Arkasi Donuk", "Masada Yok (Away)")

# --- Canlı monitörde durum için emoji + renk ipucu ---
DURUM_GORSEL = {
    DURUM_CALISMA: ("Çalışıyor", "success"),
    DURUM_TELEFON: ("Telefonda Vakit Geçiriyor", "warning"),
    DURUM_DINLENME: ("Dinleniyor / Uyukluyor", "warning"),
    "Odak Kaybi / Arkasi Donuk": ("Odak Kaybı / Arkası Dönük", "error"),
    "Masada Yok (Away)": ("Masada Yok", "error"),
}

# --- Dashboard kategori etiketleri ---
KATEGORI_ETIKETLERI = {
    "calisiyor": "Çalışıyor",
    "telefonda": "Telefonda Vakit Geçiriyor",
    "dinleniyor": "Dinleniyor",
    "odak_kaybi": "Odak Kaybı",
}
KATEGORI_ANAHTARLARI = set(KATEGORI_ETIKETLERI.keys())

# --- Pomodoro / mola ---
POMODORO_CALISMA_SN = 25 * 60   # Aralıksız çalışma süresi (25 dakika)
MOLA_ONERISI_SN = 5 * 60        # Önerilen mola süresi (5 dakika)

# --- Video kayıt ---
KAYIT_FPS = 20.0
MIN_KAYIT_SURESI_SN = 10  # 10 saniyeden kısa segmentler hiç kaydedilmez

# --- COCO iskelet bağlantıları (sadece ana kişiyi çizmek için) ---
ISKELET_BAGLANTILARI = [
    (0, 1), (0, 2), (1, 3), (2, 4),   # yüz
    (5, 6),                            # omuzlar
    (5, 7), (7, 9),                    # sol kol
    (6, 8), (8, 10),                   # sağ kol
    (5, 11), (6, 12), (11, 12),        # gövde
    (11, 13), (13, 15),                # sol bacak
    (12, 14), (14, 16),                # sağ bacak
]

# --- Eşikler / varsayılanlar ---
CEVRIMDISI_ESIK_SN = 10  # bu süre boyunca güncelleme gelmezse kullanıcı çevrimdışı sayılır
DEPO_LIMIT_GB_VARSAYILAN = 10   # 10 GB
VIDEO_OMUR_GUN_VARSAYILAN = 30  # 30 gün
TEMA_VARSAYILAN = "koyu"
