# -*- coding: utf-8 -*-
"""Uygulama ayarları."""
def ayar_oku(conn, anahtar, varsayilan):
    try:
        satir = conn.execute("SELECT deger FROM ayarlar WHERE anahtar = ?", (anahtar,)).fetchone()
        if satir is not None:
            return int(satir["deger"])
    except (ValueError, TypeError):
        pass
    return varsayilan


def ayar_yaz(conn, anahtar, deger):
    conn.execute("INSERT OR REPLACE INTO ayarlar (anahtar, deger) VALUES (?, ?)", (anahtar, str(deger)))
    conn.commit()
