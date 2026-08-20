# RoutineLens — merkezi API imajı (kamera/YOLO içermez)
FROM python:3.11-slim

WORKDIR /app

COPY server/requirements.txt /app/server/requirements.txt
RUN pip install --no-cache-dir -r /app/server/requirements.txt

# Uygulama kodu (.dockerignore ağır dosyaları hariç tutar)
COPY . /app

ENV ROUTINELENS_DB=/data/routinelens.db \
    ROUTINELENS_KAYIT=/data/kayitlar \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
