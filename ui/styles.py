# -*- coding: utf-8 -*-
"""Streamlit CSS stilleri."""
import streamlit as st
def genel_stil():
    st.markdown("""
    <style>
        /* --- Tipografi hiyerarşisi --- */
        h1 { font-weight: 800 !important; letter-spacing: -0.03em !important; color: #f8fafc !important; }
        h2 { font-weight: 700 !important; letter-spacing: -0.02em !important; color: #e2e8f0 !important; }
        h3 {
            font-weight: 700 !important;
            color: #ffffff !important;
            font-size: 1.45rem !important;
            letter-spacing: -0.01em !important;
            padding: 0.6rem 1rem !important;
            background: linear-gradient(90deg, rgba(99,102,241,0.28), rgba(139,92,246,0.16)) !important;
            border: 1px solid rgba(99,102,241,0.5) !important;
            border-left: 4px solid #6366f1 !important;
            border-radius: 12px !important;
            margin: 0.2rem 0 1rem !important;
        }
        h4 { font-weight: 600 !important; color: #cbd5e1 !important; }

        /* --- Kartlar: yuvarlak köşe + hafif gölge --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-radius: 16px !important;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35) !important;
            padding: 1rem 1.25rem !important;
        }

        /* --- Metrik kartları --- */
        div[data-testid="stMetric"] {
            background-color: #0f172a !important;
            border: 1px solid #1f2937 !important;
            border-radius: 12px !important;
            padding: 0.75rem 1rem !important;
        }
        div[data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 700 !important; font-size: 1.5rem !important; }
        div[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.78rem !important; }

        /* --- Birincil butonlar: indigo (yumuşak vurgu) --- */
        button[kind="primary"] {
            background-color: #6366f1 !important;
            border-color: #6366f1 !important;
            color: #ffffff !important;
        }
        button[kind="primary"]:hover {
            background-color: #4f46e5 !important;
            border-color: #4f46e5 !important;
            color: #ffffff !important;
        }

        /* --- Kenar çubuğu --- */
        section[data-testid="stSidebar"] {
            background-color: #0b1220 !important;
            border-right: 1px solid #1f2937 !important;
        }

        /* --- Girdi alanları: içeriğe uygun genişlik --- */
        div[data-testid="stTextInput"], div[data-testid="stNumberInput"] {
            max-width: 440px !important;
        }

        /* --- Kenar çubuğu butonlarını kompakt yap (takvim dahil) --- */
        section[data-testid="stSidebar"] button {
            min-height: 1.85rem !important;
            padding: 0.15rem 0.4rem !important;
            font-size: 0.8rem !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)


def personel_stil():
    st.markdown("""
    <style>
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stToolbar"] { background: transparent !important; }

        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(99,102,241,0.42) 0%, transparent 45%),
                radial-gradient(circle at 88% 10%, rgba(168,85,247,0.36) 0%, transparent 50%),
                radial-gradient(circle at 82% 88%, rgba(59,130,246,0.33) 0%, transparent 48%),
                radial-gradient(circle at 15% 92%, rgba(139,92,246,0.32) 0%, transparent 50%),
                #070b18 !important;
        }
        [data-testid="stAppViewContainer"] { background: transparent !important; }

        section[data-testid="stSidebar"] {
            background: rgba(13, 18, 36, 0.55) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-right: 1px solid rgba(255,255,255,0.10) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 20px !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.45) !important;
        }

        button[kind="primary"] {
            background-image: linear-gradient(90deg, #8b5cf6 0%, #6366f1 100%) !important;
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
        }
        button[kind="primary"]:hover {
            background-image: linear-gradient(90deg, #7c3aed 0%, #4f46e5 100%) !important;
            box-shadow: 0 0 28px rgba(139, 92, 246, 0.7) !important;
            color: #ffffff !important;
        }

        div[data-testid="stProgressBar"] > div > div {
            background-image: linear-gradient(90deg, #34d399, #60a5fa) !important;
            background-color: transparent !important;
            box-shadow: 0 0 12px rgba(52, 211, 153, 0.55), 0 0 20px rgba(96, 165, 250, 0.45) !important;
        }
    </style>
    """, unsafe_allow_html=True)


def admin_stil():
    st.markdown("""
    <style>
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stToolbar"] { background: transparent !important; }

        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(99,102,241,0.42) 0%, transparent 45%),
                radial-gradient(circle at 88% 10%, rgba(168,85,247,0.36) 0%, transparent 50%),
                radial-gradient(circle at 82% 88%, rgba(59,130,246,0.33) 0%, transparent 48%),
                radial-gradient(circle at 15% 92%, rgba(139,92,246,0.32) 0%, transparent 50%),
                #070b18 !important;
        }
        [data-testid="stAppViewContainer"] { background: transparent !important; }

        section[data-testid="stSidebar"] {
            background: rgba(13, 18, 36, 0.55) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-right: 1px solid rgba(255,255,255,0.10) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 20px !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.45) !important;
        }

        /* Aktif menü sekmesi: canlı mavi-mor gradyan + neon gölge */
        button[kind="primary"] {
            background-image: linear-gradient(90deg, #3b82f6 0%, #a855f7 100%) !important;
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            box-shadow: 0 0 18px rgba(139, 92, 246, 0.55) !important;
        }
        button[kind="primary"]:hover {
            background-image: linear-gradient(90deg, #2563eb 0%, #9333ea 100%) !important;
            box-shadow: 0 0 26px rgba(139, 92, 246, 0.75) !important;
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)
