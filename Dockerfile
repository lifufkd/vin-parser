FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    dos2unix \
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
