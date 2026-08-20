# -*- coding: utf-8 -*-
"""Kullanıcı CRUD işlemleri."""
from datetime import datetime

from database.auth import sifre_hashle
def kullanici_ekle(conn, kullanici_adi, ad_soyad, sifre, rol="calisan"):
    kullanici_adi = (kullanici_adi or "").strip()
    if not kullanici_adi:
        return False, "Kullanıcı adı boş olamaz."
    if not sifre:
        return False, "Başlangıç şifresi boş olamaz."
    var = conn.execute(
        "SELECT id FROM kullanicilar WHERE kullanici_adi = ?", (kullanici_adi,)
    ).fetchone()
    if var is not None:
        return False, f"'{kullanici_adi}' zaten kayıtlı."
    conn.execute(
        "INSERT INTO kullanicilar (kullanici_adi, ad_soyad, sifre_hash, rol, aktif, olusturma_tarihi) "
        "VALUES (?, ?, ?, ?, 1, ?)",
        (kullanici_adi, ad_soyad, sifre_hashle(sifre), rol, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    return True, f"'{kullanici_adi}' eklendi."


def kullanici_sifre_guncelle(conn, kullanici_id, yeni_sifre):
    conn.execute(
        "UPDATE kullanicilar SET sifre_hash = ? WHERE id = ?",
        (sifre_hashle(yeni_sifre), kullanici_id),
    )
    conn.commit()


def kullanici_aktiflik_guncelle(conn, kullanici_id, aktif):
    conn.execute("UPDATE kullanicilar SET aktif = ? WHERE id = ?", (1 if aktif else 0, kullanici_id))
    conn.commit()


def kullanici_sil(conn, kullanici_id):
    conn.execute("DELETE FROM kullanicilar WHERE id = ?", (kullanici_id,))
    conn.commit()


def kullanici_listele(conn):
    return conn.execute(
        "SELECT id, kullanici_adi, ad_soyad, rol, aktif, olusturma_tarihi "
        "FROM kullanicilar ORDER BY id"
    ).fetchall()
