# RoutineLens

AI-powered focus & productivity tracking. RoutineLens watches a webcam feed, detects what a person is doing (working, on the phone, resting, losing focus, away), records how long each state lasts, and reports everything through a clean web dashboard.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white) ![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-7c3aed) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

## Features

### Vision / AI (edge agent)

- **Dual YOLOv8 models** — skeleton/posture detection + phone (object) detection.
- **5 detected states:** Working, On the phone, Resting / Drowsy, Focus loss (turned away), Away from desk.
- **Posture analysis** (slouched vs. upright) with real-time desktop alerts.
- **Pomodoro timer** (25 min work / 5 min break) with notifications.
- **Per-state video recording** (H.264) with automatic storage management (size limit + FIFO cleanup).

### Employee dashboard

- Daily **focus score** (0–100) with progress bar and feedback.
- **Summary metrics**: total work, rest, focus loss and phone time.
- **Charts** and a daily time-distribution breakdown.
- **Timeline** of the day plus a calendar date picker.

### Admin dashboard

- **Live monitor** — who is active right now and in which state.
- **Leadership table** — total focused time per person.
- **Video evidence center** — review recorded clips.
- **User management** — create/remove users, reset passwords, enable/disable access.
- **Team analytics** — exportable reports (Excel / CSV).
- **System settings** — recording, Pomodoro, session and storage limits.

### Privacy & architecture

- **Video never leaves the device** — only JSON metadata is sent to the server.
- YOLO runs **on the edge** (on each employee's own machine).
- Role-based access (admin / employee), session management and salted password hashing (SHA-256).

## How it works

The system is split into two parts:

1. **Server (Docker)** — FastAPI + Streamlit dashboard + SQLite. Runs on one machine in the office and only receives JSON from the agents.
2. **Agent (native)** — runs on each employee's computer, opens the camera, runs YOLO locally and sends JSON to the server.

**Login / roles:** The dashboard is a web app opened in the browser
(`http://<server-ip>:8501`). Everyone logs in at the **same address**; users with the
`admin` role see the **admin panel**, everyone else sees the **employee panel**. The
agent (`main.py` + `ajan/` scripts) only runs the **camera** — it does not open the
dashboard.

```
[Employee 1 PC] main.py (YOLO, native) ─┐
[Employee 2 PC] main.py (YOLO, native) ─┼─ JSON (HTTP) ─▶ [SERVER — Docker]
[Employee N PC] main.py (YOLO, native) ─┘                 ├─ api (FastAPI)         :8000
                                                           ├─ dashboard (Streamlit) :8501
                                                           └─ SQLite (persistent volume)
```

> **Why isn't the camera in Docker?** Docker (Windows/Docker Desktop) cannot give containers access to the webcam, a display (`cv2.imshow`), or the GPU. That's why the vision part runs natively on each employee's machine, while Docker packages only the server.

## Quick start

### 1) Run the server (Docker)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine + Compose (Linux).

**Easiest (Windows):** double-click `baslat.bat` — it starts Docker, brings up the
containers and opens the browser at `http://localhost:8501`.

**Manual:**

```bash
docker compose up -d
```

Images are built automatically on the first run (this may take a few minutes).

- **Dashboard:** http://localhost:8501 — default user `admin`, password `admin123`. This default applies unless you create a `.env` (`.env` is only needed to change the password).
- **API:** http://localhost:8000 (docs at http://localhost:8000/docs)

> On the machine running the server, open `http://localhost:8501`; on other machines
> on the same network, open `http://<server-ip>:8501`.

> ⚠️ Do **not** run the dashboard manually (`streamlit run dashboard.py`); only run it
> via Docker (`baslat.bat` or `docker compose up -d`). Running it manually causes a
> port 8501 conflict and points login (admin password) at the wrong database.

### 2) Admin: log in from the browser and create users

1. Open `http://<server-ip>:8501` in a browser.
2. Log in as `admin` (the password is the `ROUTINELENS_ADMIN_SIFRE` value from `.env`).
3. Open **User Management** and create one account per employee (e.g. `omer`, `ayse`). Give the username and password to each employee.

### 3) Employee: log in from the browser

The employee opens `http://<server-ip>:8501` in a browser on their own computer and
logs in with the username/password given by the admin. The **employee panel** shows
their focus score, summary metrics, charts and timeline.

### 4) Employee: install the agent and start the camera (native)

> The agent only runs the **camera** and sends data to the server; it does **not** open
> the dashboard. The dashboard is opened separately in the browser (step 3).

Requires **Python 3.11** (the most reliable version for torch/ultralytics).

1. Double-click `ajan\kur.bat` — installs dependencies and downloads the YOLO models (first run takes a few minutes).
2. Open `ajan_ayarlar.txt` and set `SUNUCU` and `KULLANICI` (the username must match the one created in the dashboard).
3. Double-click `ajan\RoutineLensAjan.bat` — the camera window opens. (Click the window and press `q` to quit.)

`ajan_ayarlar.txt` example:

```
SUNUCU=http://192.168.1.10:8000
KULLANICI=omer
```

> `SUNUCU` must be the LAN IP of the machine running the server (not `localhost`).

## Environment variables (.env)

Secrets (such as the admin password) are not hardcoded — they are read from a
`.env` file in the project root. The `.env` file is protected by `.gitignore` and
`.dockerignore` and is **never committed to GitHub**.

```bash
copy .env.example .env      # Windows
# cp .env.example .env       # Linux / Mac
```

| Variable | Required | Description |
|---|---|---|
| `ROUTINELENS_ADMIN_SIFRE` | Yes (production) | Password of the `admin` account created on first run. |
| `ROUTINELENS_SUNUCU` | No | Central server address the agent sends data to (default `http://127.0.0.1:8000`). |
| `ROUTINELENS_DB` | No | SQLite file path (default `routinelens.db`). |
| `ROUTINELENS_KAYIT` | No | Video recordings folder (default `kayitlar`). |

> ⚠️ If you don't create a `.env`, the system starts with the development default
> `admin` / `admin123`. **For public/production use, always create a `.env` and set
> a strong password.**

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/status` | Live state (heartbeat) |
| POST | `/api/logs` | Completed state segment |
| POST | `/api/offline` | Agent shut down |

## Project structure

```
RoutineLens/
├── core/          # Constants, media, notifications, remote client
├── database/      # SQLite layer (auth, crud, logs, settings, storage)
├── vision/        # YOLO engine + video recorder (agent side)
├── services/      # Business logic (analytics, storage, process control)
├── ui/            # Streamlit pages (dashboard)
├── server/        # FastAPI REST API (server)
├── ajan/          # Agent setup + launcher scripts
├── main.py        # Agent entry point (camera + YOLO)
├── dashboard.py   # Dashboard entry point (Streamlit)
├── docker-compose.yml
└── requirements.txt / agent_requirements.txt
```

## Technologies

| Technology | Used for |
|---|---|
| Python 3.11 | Core language |
| YOLOv8 (Ultralytics) / PyTorch | Pose & object detection |
| OpenCV | Camera capture and rendering |
| Streamlit | Web dashboard |
| FastAPI | REST API |
| SQLite | Storage |
| Docker / Docker Compose | Server packaging |
| Pandas, Plotly | Analytics and charts |

## Notes / limitations (MVP)

- The web UI is currently in **Turkish**.
- Recorded videos stay on each employee's machine; the central "Video Evidence Center" does not yet pull them to the server.
- The agent is currently **Windows-only** (it uses Windows-specific camera, notification and process-management components).
