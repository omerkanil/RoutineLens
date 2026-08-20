# -*- coding: utf-8 -*-
"""Kimlik doğrulama ve oturum yönetimi."""
import hashlib
import secrets
from datetime import datetime
def sifre_hashle(sifre, tuz=None):
    if tuz is None:
        tuz = secrets.token_hex(8)
    ozet = hashlib.sha256((tuz + sifre).encode("utf-8")).hexdigest()
    return f"{tuz}:{ozet}"


def sifre_dogrula(sifre, sifre_hash):
    try:
        tuz, ozet = sifre_hash.split(":", 1)
    except (ValueError, AttributeError):
        return False
    return hashlib.sha256((tuz + sifre).encode("utf-8")).hexdigest() == ozet


def kullanici_dogrula(conn, kullanici_adi, sifre):
    satir = conn.execute(
        "SELECT * FROM kullanicilar WHERE kullanici_adi = ?", (kullanici_adi.strip(),)
    ).fetchone()
    if satir is None or satir["aktif"] != 1:
        return None
    if not sifre_dogrula(sifre, satir["sifre_hash"]):
        return None
    return dict(satir)


def oturum_olustur(conn, kullanici_adi):
    token = secrets.token_hex(24)
    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT OR REPLACE INTO oturumlar (token, kullanici_adi, olusturma_tarihi, son_aktivite) "
        "VALUES (?, ?, ?, ?)",
        (token, kullanici_adi, su_an, su_an),
    )
    conn.commit()
    return token


def oturum_dogrula(conn, token):
    satir = conn.execute(
        "SELECT k.* FROM oturumlar o JOIN kullanicilar k ON k.kullanici_adi = o.kullanici_adi "
        "WHERE o.token = ?",
        (token,),
    ).fetchone()
    if satir is None or satir["aktif"] != 1:
        return None
    return dict(satir)


def oturum_sil(conn, token):
    conn.execute("DELETE FROM oturumlar WHERE token = ?", (token,))
    conn.commit()


def oturum_baslangic(conn, token):
    """Oturumun başlangıç (giriş) zamanını datetime olarak döndürür; yoksa None.

    Oturum süresi girişten itibaren sabittir; işlem yaptıkça yenilenmez.
    """
    satir = conn.execute(
        "SELECT olusturma_tarihi FROM oturumlar WHERE token = ?", (token,)
    ).fetchone()
    if satir is None or satir["olusturma_tarihi"] is None:
        return None
    try:
        return datetime.strptime(satir["olusturma_tarihi"], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None
