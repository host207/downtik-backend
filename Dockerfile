FROM python:3.11-slim

# تثبيت yt-dlp و ffmpeg
RUN apt-get update && \
    apt-get install -y wget ffmpeg && \
    wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp && \
    apt-get clean

# مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY instagram_backend_server.py .

# تشغيل
CMD ["python", "instagram_backend_server.py"]
