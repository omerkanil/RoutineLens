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
    if "acik_klip" not in st.session_state:
        st.session_state.acik_klip = None
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
                    st.session_state.acik_klip = None
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
            for video in sayfa_videolari:
                anahtar = f"{secili_kisi}:{kat}:{video}"
                acik_mi = st.session_state.acik_klip == anahtar
                ok_ikon = ":material/expand_more:" if acik_mi else ":material/chevron_right:"
                if st.button(dost_isim(video), icon=ok_ikon, key=f"dv_{secili_kisi}_{kat}_{video}"):
                    st.session_state.acik_klip = None if acik_mi else anahtar
                    st.rerun()
                if acik_mi:
                    yol = guvenli_video_yolu(secili_kisi, kat, video)
                    if yol is None:
                        st.error("Video okunamadı veya güvenlik denetiminden geçemedi.")
                    else:
                        # Yolu ver; Streamlit dosyayı RAM'e kopyalamadan sunar.
                        st.video(yol, format="video/mp4")
                        kol_dl, kol_sil = st.columns([2, 1])
                        with kol_dl:
                            with open(yol, "rb") as f:
                                st.download_button("İndir", icon=":material/download:", data=f,
                                                   file_name=video, mime="video/mp4", key=f"dl_{secili_kisi}_{kat}_{video}")
                        with kol_sil:
                            if st.button("Sil", icon=":material/delete:", key=f"sil_{secili_kisi}_{kat}_{video}"):
                                yol = guvenli_video_yolu(secili_kisi, kat, video)
                                if yol is None:
                                    st.error("Silme iptal edildi: güvenlik denetimi başarısız.")
                                else:
                                    try:
                                        os.remove(yol)
                                        st.session_state.acik_klip = None
                                        st.rerun()
                                    except Exception:
                                        st.error("Silinemedi.")

            # --- Altta sayfa seçici ---
            if toplam_sayfa > 1:
                st.divider()
                k_onceki, k_orta, k_sonraki = st.columns([1, 2, 1])
                with k_onceki:
                    if st.button("‹ Önceki", disabled=(sayfa <= 1),
                                 key=f"video_onceki_{secili_kisi}_{kat}", width="stretch"):
                        st.session_state[sayfa_anahtari] = sayfa - 1
                        st.rerun()
                with k_orta:
                    st.selectbox(
                        "Sayfa",
                        list(range(1, toplam_sayfa + 1)),
                        key=sayfa_anahtari,
                        label_visibility="collapsed",
                    )
                with k_sonraki:
                    if st.button("Sonraki ›", disabled=(sayfa >= toplam_sayfa),
                                 key=f"video_sonraki_{secili_kisi}_{kat}", width="stretch"):
                        st.session_state[sayfa_anahtari] = sayfa + 1
                        st.rerun()
