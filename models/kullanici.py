# -*- coding: utf-8 -*-
"""Kullanici veri modeli."""
from dataclasses import dataclass


@dataclass
class Kullanici:
    id: int = None
    kullanici_adi: str = ""
    ad_soyad: str = ""
    sifre_hash: str = ""
    rol: str = "calisan"
    aktif: int = 1
    olusturma_tarihi: str = ""

    @classmethod
    def from_row(cls, satir):
        return cls(**{k: satir[k] for k in satir.keys()})
