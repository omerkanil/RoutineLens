# -*- coding: utf-8 -*-
"""Kullanıcı yönetimi sayfası."""
import pandas as pd
import streamlit as st

import db
from ui.security import admin_gerekli, guvenli_metin
@admin_gerekli
def kullanici_yonetimi(conn):
    st.subheader(":material/group: Kullanıcı Yönetimi")
    kullanicilar = db.kullanici_listele(conn)
    if kullanicilar:
        df = pd.DataFrame([dict(k) for k in kullanicilar])
        df = df.rename(columns={
            "id": "ID", "kullanici_adi": "Kullanıcı Adı", "ad_soyad": "Ad Soyad",
            "rol": "Rol", "aktif": "Durum", "olusturma_tarihi": "Oluşturma",
        })
        df["Rol"] = df["Rol"].map({"admin": "Yönetici", "calisan": "Personel"})
        df["Durum"] = df["Durum"].map({1: "Aktif", 0: "Kapalı"})
        st.dataframe(df, width="stretch")
    else:
        st.info("Kayıtlı kullanıcı yok.")

    st.divider()

    with st.expander("Yeni Kullanıcı Ekle", icon=":material/person_add:"):
        with st.form("yeni_kullanici_formu"):
            yk_ad = st.text_input("Kullanıcı Adı")
            yk_soyad = st.text_input("Ad Soyad")
            yk_sifre = st.text_input("Başlangıç Şifresi", type="password")
            yk_rol = st.selectbox("Rol", ["calisan", "admin"],
                                  format_func=lambda r: "Yönetici" if r == "admin" else "Personel")
            yk_ekle = st.form_submit_button("Ekle")
        if yk_ekle:
            ok, mesaj = db.kullanici_ekle(conn, yk_ad, yk_soyad, yk_sifre, yk_rol)
            if ok:
                st.success(mesaj)
                st.rerun()
            else:
                st.error(mesaj)

    if kullanicilar:
        with st.expander("Mevcut Kullanıcıyı Yönet", icon=":material/manage_accounts:"):
            secim_id = st.selectbox(
                "Kullanıcı", [k["id"] for k in kullanicilar],
                format_func=lambda i: next((k["kullanici_adi"] for k in kullanicilar if k["id"] == i), i),
            )
            hedef = next(k for k in kullanicilar if k["id"] == secim_id)
            st.write(f"Seçili: **{guvenli_metin(hedef['kullanici_adi'])}** ({guvenli_metin(hedef['rol'])})")

            if hedef["rol"] != "admin":
                if hedef["aktif"]:
                    if st.button("Girişi Kapat", icon=":material/block:"):
                        db.kullanici_aktiflik_guncelle(conn, secim_id, 0)
                        st.rerun()
                else:
                    if st.button("Girişi Aç", icon=":material/check:"):
                        db.kullanici_aktiflik_guncelle(conn, secim_id, 1)
                        st.rerun()
            else:
                st.caption("Yönetici hesabının girişi kapatılamaz.")

            yeni_sifre = st.text_input("Yeni Şifre (sıfırlamak için)", type="password")
            if st.button("Şifreyi Sıfırla", icon=":material/key:"):
                if yeni_sifre:
                    db.kullanici_sifre_guncelle(conn, secim_id, yeni_sifre)
                    st.success("Şifre güncellendi.")
                    st.rerun()
                else:
                    st.error("Yeni şifre boş olamaz.")

            if hedef["rol"] != "admin":
                if st.button("Kullanıcıyı Sil", icon=":material/delete:"):
                    db.kullanici_sil(conn, secim_id)
                    st.success("Kullanıcı silindi.")
                    st.rerun()
            else:
                st.caption("Yönetici hesabı silinemez.")
