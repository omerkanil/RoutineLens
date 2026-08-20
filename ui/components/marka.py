# -*- coding: utf-8 -*-
"""Marka (RoutineLens) başlığı bileşeni."""
import streamlit as st


def marka_basligi():
    """Sidebar'ın sol üstüne büyük, kutulu marka başlığı basar."""
    st.sidebar.markdown(
        "<div style='padding:0.9rem 1rem 1rem; margin-bottom:0.75rem; "
        "background:linear-gradient(135deg, rgba(99,102,241,0.28), rgba(139,92,246,0.16)); "
        "border:1px solid rgba(99,102,241,0.5); border-radius:16px; "
        "text-align:center; box-shadow:0 8px 22px rgba(0,0,0,0.32);'>"
        "<span style='font-weight:800; font-size:2rem; letter-spacing:-0.03em; color:#ffffff;'>Routine</span>"
        "<span style='font-weight:800; font-size:2rem; letter-spacing:-0.03em; "
        "background:linear-gradient(90deg,#60a5fa,#a78bfa); -webkit-background-clip:text; "
        "background-clip:text; -webkit-text-fill-color:transparent; color:transparent;'>Lens</span>"
        "</div>",
        unsafe_allow_html=True,
    )
