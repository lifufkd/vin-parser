FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    dos2unix \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libx11-6 \
    libxext6 \
    libxfixes3 \
    libxcb1 \
    libexpat1 \
    libgio-2.0-0 \
    libgobject-2.0-0 \
    libatspi2.0-0 \
    fonts-liberation \
    wget \
    curl \
    gnupg \
    unzip \
    libx11-xcb1 \
    libxcursor1 \
    libgtk-3-0 \
    libgdk-pixbuf-2.0-0 \
    libpangocairo-1.0-0 \
    libcairo-gobject2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
COPY requirements.txt .
COPY entrypoint.sh .

# Приводим к UNIX-формату и даём права на исполнение
RUN dos2unix ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

RUN pip install --upgrade pip && pip install -r requirements.txt
RUN playwright install

ENTRYPOINT ["./entrypoint.sh"]
