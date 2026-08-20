# -*- coding: utf-8 -*-
"""Giriş ekranı."""
import streamlit as st

import db


def login_ekrani(conn):
    # --- Premium karanlık tema: neon ışık huzmeleri + buzlu cam kart ---
    st.markdown("""
    <style>
        /* Header/araç çubuğunu şeffaflaştır (tam ekran arka plan) */
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stToolbar"] { background: transparent !important; }

        /* Zifiri siyah değil, koyu lacivert taban + mor/mavi neon huzmeler */
        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(99,102,241,0.45) 0%, transparent 45%),
                radial-gradient(circle at 88% 10%, rgba(168,85,247,0.38) 0%, transparent 50%),
                radial-gradient(circle at 82% 88%, rgba(59,130,246,0.35) 0%, transparent 48%),
                radial-gradient(circle at 15% 92%, rgba(139,92,246,0.34) 0%, transparent 50%),
                #070b18 !important;
        }
        [data-testid="stAppViewContainer"] { background: transparent !important; }

        /* Buzlu cam (glassmorphism) kart */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,0.06) !important;
            backdrop-filter: blur(18px) !important;
            -webkit-backdrop-filter: blur(18px) !important;
            border: 1px solid rgba(255,255,255,0.14) !important;
            border-radius: 22px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
            padding: 2.5rem 2rem !important;
            max-width: 430px !important;
            margin: 0 auto !important;
        }

        /* Koyu, pürüzsüz girdi kutuları */
        div[data-testid="stTextInput"] input {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 12px !important;
            color: #e2e8f0 !important;
            padding: 0.65rem 0.9rem !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextInput"] input:focus-visible {
            border-color: rgba(255,255,255,0.3) !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Şifre kutusu: yazı göz ikonuyla çakışmasın diye sağ boşluk */
        div[data-testid="stTextInput"] input[type="password"] {
            padding-right: 2.6rem !important;
        }

        /* Giriş butonu: mor-indigo gradyan + neon gölge */
        div[data-testid="stFormSubmitButton"] > button {
            background-image: linear-gradient(90deg, #8b5cf6 0%, #6366f1 100%) !important;
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            padding: 0.7rem 1rem !important;
            box-shadow: 0 0 22px rgba(139, 92, 246, 0.55) !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-image: linear-gradient(90deg, #7c3aed 0%, #4f46e5 100%) !important;
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.75) !important;
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)

    baslik = "#ffffff"
    ikincil = "#94a3b8"

    # Dikeyde ortalamak için üst boşluk
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)

    sol, orta, sag = st.columns([1, 1.1, 1])
    with orta:
        with st.container(border=True):
            st.markdown(
                f"<h2 style='text-align:center; margin-bottom:0.3rem; font-weight:800; font-size:2.3rem; letter-spacing:-0.02em;'>"
                f"<span style='color:{baslik};'>Routine</span>"
                f"<span style='background:linear-gradient(90deg,#60a5fa,#a78bfa); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; color:transparent;'>Lens</span>"
                f"</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='text-align:center; color:{ikincil}; margin-bottom:1.6rem;'>Personel veya yönetici girişi</p>",
                unsafe_allow_html=True,
            )
            with st.form("giris_formu"):
                kullanici_adi = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adı",
                                              label_visibility="collapsed", icon=":material/person:")
                sifre = st.text_input("Şifre", type="password", placeholder="Şifre",
                                      label_visibility="collapsed", icon=":material/lock:")
                giris = st.form_submit_button("Giriş Yap", type="primary", width="stretch")
            if giris:
                kullanici = db.kullanici_dogrula(conn, kullanici_adi, sifre)
                if kullanici:
                    token = db.oturum_olustur(conn, kullanici["kullanici_adi"])
                    st.session_state.giris = kullanici
                    st.query_params["token"] = token
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı ya da hesap kapatılmış.")
