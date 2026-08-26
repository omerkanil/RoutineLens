# -*- coding: utf-8 -*-
"""Geriye dönük uyumluluk facadesi: database paketine ve core.config'e yönlendirir.

Eski `import db; db.xxx` çağrılarının çalışmaya devam etmesi için.
"""
from core.config import (
    DB_PATH, KAYIT_KLASORU, GECICI_KLASOR, DURUM_KATEGORI,
    DURUM_CALISMA, DURUM_DINLENME, DURUM_TELEFON, ODAK_KAYBI_DURUMLAR, DURUM_GORSEL,
    KATEGORI_ETIKETLERI, KATEGORI_ANAHTARLARI, POMODORO_CALISMA_SN, MOLA_ONERISI_SN,
    KAYIT_FPS, MIN_KAYIT_SURESI_SN, ISKELET_BAGLANTILARI,
    CEVRIMDISI_ESIK_SN, DEPO_LIMIT_GB_VARSAYILAN, VIDEO_OMUR_GUN_VARSAYILAN,
    TEMA_VARSAYILAN, PROJE_DIZINI, MAIN_PY,
)
from database.manager import DatabaseManager, db_manager
from database.auth import (
    sifre_hashle, sifre_dogrula, kullanici_dogrula,
    oturum_olustur, oturum_dogrula, oturum_sil,
    oturum_baslangic,
)
from database.crud import (
    kullanici_ekle, kullanici_sifre_guncelle, kullanici_aktiflik_guncelle,
    kullanici_sil, kullanici_listele,
)
from database.logs import (
    canli_durum_guncelle, canli_durum_sil, surec_kaydet, surec_oku, surec_sil,
    komut_yaz, komutlari_oku_temizle,
)
from database.settings import ayar_oku, ayar_yaz
from database.storage import depo_boyutu, depo_temizle, depo_uyari_mesaji


def baglan():
    return db_manager.baglan()


def init_db():
    return db_manager.init_db()
