# RoutineLens

Yapay zeka (YOLOv8) tabanlı odak ve verimlilik takip sistemi. RoutineLens kamera görüntüsünden kişinin ne yaptığını tespit eder (çalışıyor, telefonda, dinleniyor, odak kaybı, masada yok), her durumun ne kadar sürdüğünü kaydeder ve her şeyi sade bir web paneli üzerinden raporlar.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white) ![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-7c3aed) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

## Özellikler

### Yapay zeka / görüntü işleme (ajan)

- **Çift YOLOv8 modeli** — iskelet/postür tespiti + telefon (nesne) tespiti.
- **5 durum tespiti:** Çalışıyor, Telefonda, Dinleniyor / Uyukluyor, Odak Kaybı (arkası dönük), Masada Yok.
- **Postür analizi** (kambur / dik) + gerçek zamanlı masaüstü uyarıları.
- **Pomodoro** zamanlayıcısı (25 dk çalışma / 5 dk mola) + bildirimler.(Admin tarafından ayarlanabilir.)
- **Duruma göre video kaydı** (H.264) + otomatik depolama yönetimi (boyut limiti + FIFO temizliği).

### Çalışan paneli

- Günlük **odak skoru** (0–100) + ilerleme çubuğu ve geri bildirim.
- **Özet metrikler**: toplam çalışma, dinlenme, odak kaybı ve telefon süresi.
- **Grafikler** ve günlük zaman dağılımı (oranlar).
- Günün **zaman çizelgesi** + takvim tarih seçici.

### Yönetici paneli

- **Canlı monitör** — şu an kim aktif, hangi durumda.
- **Liderlik tablosu** — kişi başı toplam odaklanma süresi.
- **Video kanıt merkezi** — kaydedilen klipleri inceleme.
- **Kullanıcı yönetimi** — kullanıcı ekle/sil, şifre sıfırla, erişimi aç/kapat.
- **Takım analitiği** — dışa aktarılabilir raporlar (Excel / CSV).
- **Sistem ayarları** — kayıt, Pomodoro, oturum ve depolama limitleri.

### Gizlilik & mimari

- **Video cihazdan asla çıkmaz** — sunucuya yalnızca JSON meta verisi gönderilir.
- YOLO **uçta** (her çalışanın kendi makinesinde) çalışır.
- Rol tabanlı erişim (yönetici / çalışan), oturum yönetimi ve tuzlu şifre özeti (SHA-256).

## Nasıl çalışır

Sistem iki parçadan oluşur:

1. **Sunucu (Docker)** — FastAPI + Streamlit paneli + SQLite. Ofisteki tek bir makinede çalışır ve ajanlardan yalnızca JSON alır.
2. **Ajan (native)** — her çalışanın bilgisayarında çalışır, kamerayı açar, YOLO'yu yerelde çalıştırır ve sunucuya JSON gönderir.

**Giriş / roller:** Panel, tarayıcıdan (`http://<sunucu-ip>:8501`) açılan bir web
uygulamasıdır. Herkes **aynı adrese** giriş yapar; `admin` rolüne sahip kullanıcılar
**yönetici panelini**, diğerleri **çalışan panelini** görür. Ajan (`main.py` +
`ajan/` betikleri) ise yalnızca **kamerayı** çalıştırır — paneli açmaz.

```
[Çalışan 1 PC] main.py (YOLO, native) ─┐
[Çalışan 2 PC] main.py (YOLO, native) ─┼─ JSON (HTTP) ─▶ [SUNUCU — Docker]
[Çalışan N PC] main.py (YOLO, native) ─┘                 ├─ api (FastAPI)         :8000
                                                          ├─ dashboard (Streamlit) :8501
                                                          └─ SQLite (kalıcı hacim)
```

> **Kamera neden Docker'da değil?** Docker (Windows/Docker Desktop) konteynerlere webcam erişimi, ekran (`cv2.imshow`) ve GPU veremez. Bu yüzden görüntü işleme her çalışanın makinesinde native çalışır; Docker yalnızca sunucu tarafını paketler.

## Hızlı başlangıç

### 1) Sunucuyu çalıştır (Docker)

Gereksinim: [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) veya Docker Engine + Compose (Linux).

```bash
# Örnek ortam dosyasını kopyalayıp düzenleyin
copy .env.example .env   # Windows
# cp .env.example .env    # Linux / Mac

docker compose up -d
```

İlk çalıştırmada imajlar otomatik derlenir.

- **Panel:** http://localhost:8501 — varsayılan kullanıcı `admin`; şifre `.env` içindeki `ROUTINELENS_ADMIN_SIFRE` değeridir (`.env.example`'ı kopyalayıp düzenleyin).
- **API:** http://localhost:8000 (dokümantasyon http://localhost:8000/docs)

### 2) Yönetici: tarayıcıdan giriş yap ve kullanıcıları oluştur

1. Tarayıcıdan `http://<sunucu-ip>:8501` adresini aç.
2. `admin` kullanıcısıyla giriş yap (şifre `.env` içindeki `ROUTINELENS_ADMIN_SIFRE` değeridir).
3. **Kullanıcı Yönetimi** sayfasından her çalışan için bir hesap oluştur (örn. `ali`, `ayse`). Oluşturduğun kullanıcı adı ve şifreyi çalışana ilet.

### 3) Çalışan: tarayıcıdan giriş yap

Çalışan, kendi bilgisayarında tarayıcıdan `http://<sunucu-ip>:8501` adresini açar ve
yöneticinin verdiği kullanıcı adı/şifreyle giriş yapar. Açılan **çalışan panelinde**
kendi odak skorunu, özet metriklerini, grafiklerini ve zaman çizelgesini görür.

### 4) Çalışan: ajanı kur ve kamerayı başlat (native)

> Ajan yalnızca **kamerayı** çalıştırır ve veriyi sunucuya gönderir; paneli **açmaz**.
> Panel, 3. adımdaki gibi tarayıcıdan ayrıca açılır.

Gereksinim: **Python 3.11** (torch/ultralytics ile en garanti uyumlu sürüm).

1. `ajan\kur.bat` dosyasına çift tıklayın — bağımlılıkları kurar ve YOLO modellerini indirir (ilk kurulum birkaç dakika sürer).
2. `ajan_ayarlar.txt` dosyasını açıp `SUNUCU` ve `KULLANICI` değerlerini girin (kullanıcı adı, panelde oluşturulan adla aynı olmalı).
3. `ajan\RoutineLensAjan.bat` dosyasına çift tıklayın — kamera penceresi açılır. (Kapatmak için pencereye tıklayıp `q` tuşuna basın.)

`ajan_ayarlar.txt` örneği:

```
SUNUCU=http://192.168.1.10:8000
KULLANICI=omer
```

> `SUNUCU`, sunucunun çalıştığı makinenin LAN IP'si olmalıdır (`localhost` değil).

## Ortam değişkenleri (.env)

Gizli değerler (yönetici şifresi gibi) koda gömülü değildir; kök dizindeki `.env`
dosyasından okunur. `.env` dosyası `.gitignore` ve `.dockerignore` ile korunur ve
**GitHub'a asla gönderilmez**.

```bash
copy .env.example .env      # Windows
# cp .env.example .env       # Linux / Mac
```

| Değişken | Zorunlu | Açıklama |
|---|---|---|
| `ROUTINELENS_ADMIN_SIFRE` | Evet (üretimde) | İlk kurulumda oluşturulan `admin` hesabının şifresi. |
| `ROUTINELENS_SUNUCU` | Hayır | Ajanın veri göndereceği merkezi sunucu adresi (varsayılan `http://127.0.0.1:8000`). |
| `ROUTINELENS_DB` | Hayır | SQLite dosya yolu (varsayılan `routinelens.db`). |
| `ROUTINELENS_KAYIT` | Hayır | Video kayıt klasörü (varsayılan `kayitlar`). |

> ⚠️ `.env` oluşturmazsanız sistem geliştirme amaçlı varsayılan `admin` / `admin123`
> ile başlar. **Public / production kullanımda mutlaka `.env` oluşturup güçlü bir
> şifre belirleyin.**

## API

| Metot | Yol | Açıklama |
|---|---|---|
| GET | `/api/health` | Sağlık kontrolü |
| POST | `/api/status` | Canlı durum (heartbeat) |
| POST | `/api/logs` | Tamamlanan durum segmenti |
| POST | `/api/offline` | Ajan kapandı |

## Proje yapısı

```
RoutineLens/
├── core/          # Sabitler, medya, bildirimler, uzak sunucu istemcisi
├── database/      # SQLite katmanı (auth, crud, logs, settings, storage)
├── vision/        # YOLO motoru + video kaydedici (ajan tarafı)
├── services/      # İş mantığı (analitik, depolama, süreç yönetimi)
├── ui/            # Streamlit sayfaları (panel)
├── server/        # FastAPI REST API (sunucu)
├── ajan/          # Ajan kurulum + başlatma betikleri
├── main.py        # Ajan giriş noktası (kamera + YOLO)
├── dashboard.py   # Panel giriş noktası (Streamlit)
├── docker-compose.yml
└── requirements.txt / agent_requirements.txt
```

## Teknolojiler

| Teknoloji | Kullanım amacı |
|---|---|
| Python 3.11 | Çekirdek dil |
| YOLOv8 (Ultralytics) / PyTorch | Postür ve nesne tespiti |
| OpenCV | Kamera yakalama ve çizim |
| Streamlit | Web paneli |
| FastAPI | REST API |
| SQLite | Veri depolama |
| Docker / Docker Compose | Sunucu paketleme |
| Pandas, Plotly | Analitik ve grafikler |

## Notlar / sınırlamalar (MVP)

- Web arayüzü şu an **Türkçe**dir.
- Video kayıtları her çalışanın kendi makinesinde kalır; merkezi "Video Kanıt Merkezi" henüz videoları sunucuya taşımaz.
- Ajan şu an **Windows'a özgüdür** (kamera, bildirim ve süreç yönetimi için Windows bileşenleri kullanır).
