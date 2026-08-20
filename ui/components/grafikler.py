# -*- coding: utf-8 -*-
"""Plotly grafik üreticileri (Professional SaaS Dashboard stili)."""
import plotly.express as px
import plotly.graph_objects as go

# --- Renk paleti ---
YESIL = "#22c55e"      # Çalışma
TURUNCU = "#f97316"    # Telefonda / Telefon
INDIGO = "#6366f1"     # Günlük trend
CAMGOBEGI = "#38bdf8"  # Dinlenme
AMBER = "#f59e0b"      # Odak kaybı


def _stil(fig, barmode=None):
    """Ortak stil: transparan arka plan, grid'siz, dar kenar boşlukları."""
    if barmode:
        fig.update_layout(barmode=barmode)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(family="Inter, 'Segoe UI', sans-serif", size=14, color="#e2e8f0"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=13),
        ),
        hoverlabel=dict(bgcolor="rgba(17,24,39,0.9)", font_color="#ffffff"),
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        showline=True, linecolor="#64748b", linewidth=1,
        title_font=dict(size=15, family="Inter, 'Segoe UI', sans-serif"),
        tickfont=dict(size=13, family="Inter, 'Segoe UI', sans-serif"),
    )
    fig.update_yaxes(
        showgrid=False, zeroline=False,
        showline=True, linecolor="#64748b", linewidth=1,
        title_font=dict(size=15, family="Inter, 'Segoe UI', sans-serif"),
        tickfont=dict(size=13, family="Inter, 'Segoe UI', sans-serif"),
    )
    return fig


def saatlik_verim_grafigi(saat_df):
    """Yığılmış sütun grafiği: saatlere göre Çalışma (yeşil) + Telefonda (turuncu)."""
    saat_etiketleri = [f"{int(h):02d}:00" for h in saat_df["saat_dilimi"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=saat_etiketleri,
        y=saat_df["calisma_dk"],
        name="Çalışma",
        marker_color=YESIL,
        hovertemplate="%{y:.0f} dk<extra>Çalışma</extra>",
    ))
    fig.add_trace(go.Bar(
        x=saat_etiketleri,
        y=saat_df["telefon_dk"],
        name="Telefonda",
        marker_color=TURUNCU,
        hovertemplate="%{y:.0f} dk<extra>Telefonda</extra>",
    ))
    fig.update_xaxes(title="Saat", tickangle=0)
    fig.update_yaxes(title="Dakika")
    return _stil(fig, barmode="stack")


def gunluk_trend_grafigi(pivot):
    """Sütun grafiği: tarih bazında toplam çalışma (dk), değerler sütun üstünde."""
    toplam = pivot.sum(axis=1).reset_index()
    toplam.columns = ["tarih", "calisma_dk"]

    fig = px.bar(
        toplam,
        x="tarih",
        y="calisma_dk",
        text_auto=True,
        color_discrete_sequence=[INDIGO],
        labels={"tarih": "Tarih", "calisma_dk": "Çalışma (dk)"},
    )
    fig.update_traces(marker_line_width=0, textposition="outside")
    fig.update_xaxes(title="Tarih")
    fig.update_yaxes(title="Çalışma (dk)")
    return _stil(fig)


def kisisel_grafik(grafik_df):
    """Personel kategorik dağılım grafiği (semantik renkler)."""
    renk_haritasi = {
        "Çalışma": YESIL,
        "Dinlenme": CAMGOBEGI,
        "Odak Kaybı": AMBER,
        "Telefon": TURUNCU,
    }
    kategoriler = list(grafik_df.index)
    degerler = list(grafik_df.iloc[:, 0])
    renkler = [renk_haritasi.get(k, INDIGO) for k in kategoriler]

    fig = go.Figure(go.Bar(
        x=kategoriler,
        y=degerler,
        marker_color=renkler,
        text=[f"{v:.1f}" for v in degerler],
        textposition="outside",
        hovertemplate="%{y:.1f} dk<extra>%{x}</extra>",
    ))
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Süre (dk)")
    return _stil(fig)


def liderlik_grafigi(df):
    """Liderlik tablosu: kişiye göre çalışma (dk) sütun grafiği."""
    veri = df[["kullanici", "calisma_sn"]].copy()
    veri["calisma_dk"] = veri["calisma_sn"] / 60.0

    fig = go.Figure(go.Bar(
        x=veri["kullanici"],
        y=veri["calisma_dk"],
        marker_color=CAMGOBEGI,
        text=[f"{v:.0f}" for v in veri["calisma_dk"]],
        textposition="outside",
        hovertemplate="%{y:.0f} dk<extra>%{x}</extra>",
    ))
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Çalışma (dk)")
    return _stil(fig)
