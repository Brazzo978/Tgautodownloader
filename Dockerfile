FROM python:3.11-slim

WORKDIR /app

# 👉 installiamo ffmpeg nel container
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# se usi /downloads come DOWNLOAD_DIR nel config, tiene buona questa riga
RUN mkdir -p /downloads

# se nel config hai WEB_APP_PORT = 12000, meglio esporre quella
EXPOSE 12000

CMD ["python", "-m", "app.main"]
