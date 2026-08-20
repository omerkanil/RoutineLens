# -*- coding: utf-8 -*-
"""Canlı durum ve süreç yönetimi."""
from datetime import datetime
def canli_durum_guncelle(conn, kullanici_adi, durum):
    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO canli_durum (kullanici_adi, durum, baslangic, son_guncelleme)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(kullanici_adi) DO UPDATE SET
            durum = excluded.durum,
            baslangic = CASE
                WHEN canli_durum.durum = excluded.durum THEN canli_durum.baslangic
                ELSE excluded.baslangic
            END,
            son_guncelleme = excluded.son_guncelleme
    """, (kullanici_adi, durum, su_an, su_an))
    conn.commit()


def canli_durum_sil(conn, kullanici_adi):
    conn.execute("DELETE FROM canli_durum WHERE kullanici_adi = ?", (kullanici_adi,))
    conn.commit()


def surec_kaydet(conn, kullanici_adi, pid):
    conn.execute(
        "INSERT OR REPLACE INTO surecler (kullanici_adi, pid) VALUES (?, ?)",
        (kullanici_adi, int(pid)),
    )
    conn.commit()


def surec_oku(conn, kullanici_adi):
    satir = conn.execute("SELECT pid FROM surecler WHERE kullanici_adi = ?", (kullanici_adi,)).fetchone()
    return satir["pid"] if satir else None


def surec_sil(conn, kullanici_adi):
    conn.execute("DELETE FROM surecler WHERE kullanici_adi = ?", (kullanici_adi,))
    conn.commit()
