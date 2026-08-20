# RoutineLens — merkezi panel imajı (Streamlit; kamera/YOLO içermez)
FROM python:3.11-slim

WORKDIR /app

# Panel bağımlılıkları (ağır ML bağımlılıkları yok)
RUN pip install --no-cache-dir \
    "streamlit>=1.39.0" \
    "pandas>=2.0.0" \
    "plotly>=5.0.0" \
    "openpyxl>=3.1.0" \
    "python-dotenv>=1.0.0"

COPY . /app

ENV ROUTINELENS_DB=/data/routinelens.db \
    ROUTINELENS_KAYIT=/data/kayitlar \
    PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
