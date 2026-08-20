# -*- coding: utf-8 -*-
"""Rutin kaydı veri modeli."""
from dataclasses import dataclass


@dataclass
class RutinKaydi:
    id: int = None
    tarih: str = ""
    saat: str = ""
    durum: str = ""
    gecirilen_sure_sn: int = 0
    kullanici_adi: str = ""

    @classmethod
    def from_row(cls, satir):
        return cls(**{k: satir[k] for k in satir.keys()})
