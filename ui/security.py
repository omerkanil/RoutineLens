# -*- coding: utf-8 -*-
"""Güvenlik: yetki kontrolü, XSS, oturum zaman aşımı, path traversal."""
import os
import functools
import html
from datetime import datetime

import streamlit as st

import db
from core.config import KATEGORI_ANAHTARLARI
def aktif_kullanici_admin_mi():
    """Oturumdaki kullanıcının veritabanında GERÇEKTEN admin olup
    olmadığını anlık olarak doğrular. Yalnızca session_state'e güvenmez."""
    giris = st.session_state.get("giris")
    if not isinstance(giris, dict):
        return False
    if giris.get("rol") != "admin":
        return False
    kullanici_adi = giris.get("kullanici_adi")
    if not kullanici_adi:
        return False
    try:
        conn = db.baglan()
        try:
            satir = conn.execute(
                "SELECT rol, aktif FROM kullanicilar WHERE kullanici_adi = ?",
                (kullanici_adi,),
            ).fetchone()
        finally:
            conn.close()
    except Exception:
        return False
    return bool(satir and satir["aktif"] == 1 and satir["rol"] == "admin")


def admin_gerekli(fonksiyon):
    """Admin sayfalarını yetkisiz erişime karşı koruyan dekoratör.

    Her admin sayfasının/fonksiyonunun en tepesinde çalışır; kullanıcının
    veritabanında admin yetkisi yoksa sayfayı durdurur (st.stop).
    """
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        if not aktif_kullanici_admin_mi():
            st.error("Yetkisiz erişim: Bu sayfa yalnızca yöneticilere açıktır.")
            st.stop()
        return fonksiyon(*args, **kwargs)
    return sarmalayici


def guvenli_metin(deger):
    """Veritabanından gelen kullanıcı kaynaklı metni HTML/JS'e karşı kaçışlar.

    Stored XSS koruması: unsafe_allow_html=True ile basılan her kullanıcı
    girdisi bu fonksiyondan geçirilmelidir.
    """
    return html.escape(str(deger or ""))


def oturum_zaman_asimi_kontrol(conn, token):
    """Girişten itibaren geçen süre dolduysa oturumu kapatır ve True döndürür."""
    if st.session_state.get("giris") is None:
        return False
    sure_dk = db.ayar_oku(conn, "oturum_zaman_asimi_dk", 15)
    if sure_dk <= 0:
        return False
    son = db.oturum_baslangic(conn, token) if token else None
    if son is None:
        return False
    if (datetime.now() - son).total_seconds() > sure_dk * 60:
        if token:
            db.oturum_sil(conn, token)
        try:
            st.query_params.pop("token", None)
        except Exception:
            pass
        st.session_state.giris = None
        st.session_state["cikis_mesaji"] = "Oturum süresi doldu. Lütfen tekrar giriş yapın."
        st.rerun()
    return False


@st.fragment(run_every=60)
def oturum_denetim_fragmani():
    """Arka planda 60 sn'de bir çalışır; boşta kalan oturumu kapatır."""
    if st.session_state.get("giris") is None:
        return
    token = st.query_params.get("token")
    conn = db.baglan()
    try:
        oturum_zaman_asimi_kontrol(conn, token)
    finally:
        conn.close()


def guvenli_video_yolu(kullanici, kat, dosya):
    """Path Traversal korumalı dosya yolu doğrulama.

    Kullanıcıdan/URL'den gelen dosya adının yalnızca
    kayitlar/<kullanici>/<kat> klasörü içinde kaldığını
    os.path.abspath + os.path.commonprefix ile garanti eder.
    Geçersiz ise None döndürür.
    """
    # 1) Kategori yalnızca tanımlı kategorilerden biri olabilir.
    if kat not in KATEGORI_ANAHTARLARI:
        return None
    # 2) Dosya adı yalnızca basit bir dosya adı olmalı (yol/.. içermemeli).
    if os.path.basename(dosya) != dosya or not dosya.lower().endswith(".mp4"):
        return None

    kok = os.path.abspath(db.KAYIT_KLASORU)
    hedef_klasor = os.path.abspath(os.path.join(kok, kullanici, kat))
    dosya_yolu = os.path.abspath(os.path.join(hedef_klasor, dosya))

    # 3) Kategori klasörü, kayıt kökünün içinde kalmalı.
    if os.path.commonprefix([kok + os.sep, hedef_klasor + os.sep]) != kok + os.sep:
        return None
    # 4) Dosya, kategori klasörünün içinde kalmalı (symlink dahil realpath).
    if os.path.commonprefix(
        [os.path.realpath(hedef_klasor) + os.sep, os.path.realpath(dosya_yolu)]
    ) != os.path.realpath(hedef_klasor) + os.sep:
        return None
    if not os.path.isfile(dosya_yolu):
        return None
    return dosya_yolu


def guvenli_video_oku(kullanici, kat, dosya):
    """Path Traversal korumalı video okuma; içeriği bytes olarak döndürür."""
    dosya_yolu = guvenli_video_yolu(kullanici, kat, dosya)
    if dosya_yolu is None:
        return None
    try:
        with open(dosya_yolu, "rb") as f:
            return f.read()
    except Exception:
        return None
