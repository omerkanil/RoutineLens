# -*- coding: utf-8 -*-
"""DatabaseManager: SQLite bağlantı yaşam döngüsü (WAL + timeout)."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from core.config import DB_PATH, VARSAYILAN_ADMIN_SIFRE
from database.auth import sifre_hashle


class DatabaseManager:
    """SQLite bağlantılarını yönetir.

    WAL + busy_timeout + synchronous=NORMAL ile arkada yazan main.py ile
    panelin eşzamanlı erişiminde "database is locked" ve race condition
    hatalarını önler.
    """

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def baglan(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error:
            pass
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("PRAGMA synchronous = NORMAL")
        return conn

    @contextmanager
    def baglam(self):
        """Bağlantıyı otomatik kapatan context manager."""
        conn = self.baglan()
        try:
            yield conn
        finally:
            conn.close()

    def _schema_kur(self, conn):
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS rutin_loglari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT,
                saat TEXT,
                durum TEXT,
                gecirilen_sure_sn INTEGER,
                kullanici_adi TEXT
            )
        ''')

        # Eski tabloya geriye dönük uyum için kullanici_adi sütununu ekle
        mevcut_kolonlar = [satir[1] for satir in c.execute("PRAGMA table_info(rutin_loglari)")]
        if "kullanici_adi" not in mevcut_kolonlar:
            c.execute("ALTER TABLE rutin_loglari ADD COLUMN kullanici_adi TEXT")

        # Sık filtrelenen sütunlara indeks (tam tablo taramasını önler)
        c.execute("CREATE INDEX IF NOT EXISTS idx_rutin_tarih ON rutin_loglari (tarih)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_rutin_kullanici ON rutin_loglari (kullanici_adi)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_rutin_tarih_kullanici ON rutin_loglari (tarih, kullanici_adi)")

        c.execute('''
            CREATE TABLE IF NOT EXISTS ayarlar (
                anahtar TEXT PRIMARY KEY,
                deger TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                ad_soyad TEXT,
                sifre_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'calisan',
                aktif INTEGER NOT NULL DEFAULT 1,
                olusturma_tarihi TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS canli_durum (
                kullanici_adi TEXT PRIMARY KEY,
                durum TEXT,
                baslangic TEXT,
                son_guncelleme TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS oturumlar (
                token TEXT PRIMARY KEY,
                kullanici_adi TEXT NOT NULL,
                olusturma_tarihi TEXT,
                son_aktivite TEXT
            )
        ''')

        # Oturum zaman aşımı için son_aktivite sütununu geriye dönük ekle
        oturum_kolonlar = [satir[1] for satir in c.execute("PRAGMA table_info(oturumlar)")]
        if "son_aktivite" not in oturum_kolonlar:
            c.execute("ALTER TABLE oturumlar ADD COLUMN son_aktivite TEXT")

        c.execute('''
            CREATE TABLE IF NOT EXISTS surecler (
                kullanici_adi TEXT PRIMARY KEY,
                pid INTEGER
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS komutlar (
                kullanici_adi TEXT PRIMARY KEY,
                komut TEXT,
                zaman TEXT
            )
        ''')

        # İlk çalıştırmada varsayılan admin hesabını oluştur
        if c.execute("SELECT COUNT(*) FROM kullanicilar WHERE rol = 'admin'").fetchone()[0] == 0:
            sifre_hash = sifre_hashle(VARSAYILAN_ADMIN_SIFRE)
            c.execute(
                "INSERT INTO kullanicilar (kullanici_adi, ad_soyad, sifre_hash, rol, aktif, olusturma_tarihi) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("admin", "Yönetici", sifre_hash, "admin", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )

        conn.commit()

    def schema_kur(self):
        """Şemayı, migration'ları ve indeksleri kurar (idempotent).

        Uygulama başında bir kez çalıştırılması yeterlidir; her istekte
        tekrar çalıştırmaya gerek yoktur.
        """
        conn = self.baglan()
        try:
            self._schema_kur(conn)
        finally:
            conn.close()

    def init_db(self):
        """Şemayı kurup açık bir bağlantı döndürür (main.py gibi tek seferlik kullanım)."""
        conn = self.baglan()
        self._schema_kur(conn)
        return conn


db_manager = DatabaseManager()
