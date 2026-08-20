# -*- coding: utf-8 -*-
"""Takvim bileşeni."""
from datetime import datetime

import streamlit as st
def takvim_widget(mevcut_tarihler, varsayilan, bugun):
    """Sol panelde her zaman açık tam takvim. Seçili günü 'YYYY-MM-DD' metni olarak döndürür."""
    import calendar as cal

    mevcut_set = set(mevcut_tarihler)
    aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    gunler = ["Pt", "Sa", "Ça", "Pe", "Cu", "Ct", "Pz"]

    if "tk_yil" not in st.session_state:
        st.session_state.tk_yil = varsayilan.year
        st.session_state.tk_ay = varsayilan.month
        st.session_state.tk_gun = varsayilan.strftime("%Y-%m-%d")

    yil = st.session_state.tk_yil
    ay = st.session_state.tk_ay

    with st.sidebar:
        n1, n2, n3 = st.columns([1, 2, 1])
        with n1:
            if st.button("", icon=":material/chevron_left:", key="tk_onceki"):
                ay -= 1
                if ay == 0:
                    ay, yil = 12, yil - 1
                st.session_state.tk_ay, st.session_state.tk_yil = ay, yil
                st.rerun()
        with n2:
            st.markdown(f"<div style='text-align:center;font-weight:700;'>{aylar[ay - 1]} {yil}</div>",
                        unsafe_allow_html=True)
        with n3:
            if st.button("", icon=":material/chevron_right:", key="tk_sonraki"):
                ay += 1
                if ay == 13:
                    ay, yil = 1, yil + 1
                st.session_state.tk_ay, st.session_state.tk_yil = ay, yil
                st.rerun()

        hk = st.columns(7)
        for i, g in enumerate(gunler):
            hk[i].markdown(f"<div style='text-align:center;color:#94a3b8;font-size:0.7rem;'>{g}</div>",
                           unsafe_allow_html=True)

        ilk_gun, gun_sayisi = cal.monthrange(yil, ay)

        gun_no = 1
        for hafta in range(6):
            if gun_no > gun_sayisi:
                break
            kol = st.columns(7)
            for i in range(7):
                if hafta == 0 and i < ilk_gun:
                    kol[i].markdown("")
                    continue
                if gun_no > gun_sayisi:
                    break
                tarih_str = f"{yil:04d}-{ay:02d}-{gun_no:02d}"
                secili = tarih_str == st.session_state.tk_gun
                veri_var = tarih_str in mevcut_set
                gelecek = datetime(yil, ay, gun_no).date() > bugun
                etiket = f"{gun_no}" + (" •" if veri_var else "")
                if gelecek:
                    kol[i].button(etiket, key=f"tk_d_{tarih_str}", disabled=True, width="stretch")
                elif kol[i].button(etiket, key=f"tk_d_{tarih_str}",
                                   type="primary" if secili else "secondary", width="stretch"):
                    st.session_state.tk_gun = tarih_str
                    st.rerun()
                gun_no += 1

    return st.session_state.tk_gun
