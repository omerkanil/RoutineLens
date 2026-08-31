# -*- coding: utf-8 -*-
"""Video kanıt merkezi sayfası."""
import math
import os
import streamlit as st

from core.config import KATEGORI_ETIKETLERI
from services.analytics import video_envanteri, dost_isim, kullanici_adi_goster
from ui.security import admin_gerekli, guvenli_video_yolu

# Bir sayfada gösterilecek kayıt sayısı (liste uzamasın diye sayfalanır).
SAYFA_BOYUTU = 10


@st.cache_data(ttl=30, show_spinner=False)
def _envanter_getir():
    """Klasör taramasını önbelleğe al (kayıtlar sık değişmez)."""
    return video_envanteri()


@st.dialog("Video Kaydı", width="large")
def video_dialog(yol, video, secili_kisi, kat):
    """Karta tıklanınca açılan ayrı pencere (modal) — video burada oynatılır."""
    st.video(yol, format="video/mp4")
    kol_dl, kol_sil = st.columns([2, 1])
    with kol_dl:
        with open(yol, "rb") as f:
            st.download_button(
                "İndir", icon=":material/download:", data=f,
                file_name=video, mime="video/mp4",
                key=f"dl_{secili_kisi}_{kat}_{video}",
            )
    with kol_sil:
        if st.button("Sil", icon=":material/delete:", key=f"sil_{secili_kisi}_{kat}_{video}", width="stretch"):
            try:
                os.remove(yol)
                _envanter_getir.clear()
                st.session_state["video_mesaji"] = "Video silindi."
                st.rerun()
            except Exception:
                st.error("Silinemedi.")


@admin_gerekli
def video_merkezi(conn):
    st.subheader(":material/video_library: Video Kanıt Merkezi (Smart DVR)")
    st.caption("Çalışanların durum klasörlerindeki kayıtlı video kanıtlarını kişi ve saat bazlı izleyin/indirin.")
    if "video_mesaji" in st.session_state:
        st.success(st.session_state.pop("video_mesaji"))
    envanter = _envanter_getir()
    if not envanter:
        st.info("Henüz video kaydı yok. 'main.py' çalışırken kayıtlar burada birikir.")
        return
    kisiler = sorted(envanter.keys())
    secili_kisi = st.selectbox("Kişi Seç", kisiler, format_func=kullanici_adi_goster)
    kategoriler = envanter.get(secili_kisi)
    if not kategoriler:
        st.info("Bu kişi için video kaydı yok.")
        return
    sekmeler = st.tabs([KATEGORI_ETIKETLERI[k] for k in kategoriler])
    for i, kat in enumerate(kategoriler):
        with sekmeler[i]:
            videolar = kategoriler[kat]
            st.caption(f"{len(videolar)} kayıt")
            with st.popover("Tümünü Sil", icon=":material/delete:"):
                st.warning("Bu kişinin bu kategorideki TÜM kayıtları kalıcı olarak silinecek.")
                if st.button("Evet, Tümünü Sil", type="primary", width="stretch",
                             key=f"tumunu_sil_{secili_kisi}_{kat}"):
                    silinen = 0
                    for video in videolar:
                        yol = guvenli_video_yolu(secili_kisi, kat, video)
                        if yol is not None:
                            try:
                                os.remove(yol)
                                silinen += 1
                            except Exception:
                                pass
                    _envanter_getir.clear()
                    st.session_state["video_mesaji"] = f"{silinen} video silindi."
                    st.rerun()
            toplam_sayfa = max(1, math.ceil(len(videolar) / SAYFA_BOYUTU))
            sayfa_anahtari = f"video_sayfa_{secili_kisi}_{kat}"
            sayfa = st.session_state.get(sayfa_anahtari, 1)
            if sayfa > toplam_sayfa:
                sayfa = toplam_sayfa
                st.session_state[sayfa_anahtari] = sayfa
            bas = (sayfa - 1) * SAYFA_BOYUTU
            sayfa_videolari = videolar[bas:bas + SAYFA_BOYUTU]
            KART_SUTUN = 5
            for satir_basi in range(0, len(sayfa_videolari), KART_SUTUN):
                satir = sayfa_videolari[satir_basi:satir_basi + KART_SUTUN]
                kolonlar = st.columns(KART_SUTUN)
                for idx, video in enumerate(satir):
                    with kolonlar[idx]:
                        if st.button(
                            dost_isim(video),
                            icon=":material/play_circle:",
                            key=f"izle_{secili_kisi}_{kat}_{video}",
                            width="stretch",
                        ):
                            yol = guvenli_video_yolu(secili_kisi, kat, video)
                            if yol is None:
                                st.error("Video okunamadı veya güvenlik denetiminden geçemedi.")
                            else:
                                video_dialog(yol, video, secili_kisi, kat)

            # --- Altta sayfa seçici (Google tarzı) ---
            if toplam_sayfa > 1:
                st.divider()
                GORUNEN = 7
                if toplam_sayfa <= GORUNEN:
                    gosterilecek = list(range(1, toplam_sayfa + 1))
                else:
                    gosterilecek = [1]
                    bas = max(2, sayfa - 2)
                    son = min(toplam_sayfa - 1, sayfa + 2)
                    if bas > 2:
                        gosterilecek.append("...")
                    gosterilecek += list(range(bas, son + 1))
                    if son < toplam_sayfa - 1:
                        gosterilecek.append("...")
                    gosterilecek.append(toplam_sayfa)

                kolonlar = st.columns([1.5] + [1] * len(gosterilecek) + [1.5])
                with kolonlar[0]:
                    if st.button("‹ Önceki", disabled=(sayfa <= 1),
                                 key=f"video_onceki_{secili_kisi}_{kat}", width="stretch"):
                        st.session_state[sayfa_anahtari] = sayfa - 1
                        st.rerun()
                for i, p in enumerate(gosterilecek):
                    with kolonlar[i + 1]:
                        if p == "...":
                            st.markdown("<div style='text-align:center; padding-top:0.5rem;'>…</div>", unsafe_allow_html=True)
                        else:
                            if st.button(str(p), key=f"video_sayfa_{secili_kisi}_{kat}_{p}",
                                         disabled=(p == sayfa), width="stretch"):
                                st.session_state[sayfa_anahtari] = p
                                st.rerun()
                with kolonlar[-1]:
                    if st.button("Sonraki ›", disabled=(sayfa >= toplam_sayfa),
                                 key=f"video_sonraki_{secili_kisi}_{kat}", width="stretch"):
                        st.session_state[sayfa_anahtari] = sayfa + 1
                        st.rerun()
