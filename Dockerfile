FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m honeypot

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY honeypot.py .
COPY exporter.py .
COPY geoip.py .
COPY database.py .
COPY migrate.py .

RUN mkdir /data && chown -R honeypot:honeypot /data

USER honeypot

EXPOSE 22

CMD ["python", "honeypot.py"]
