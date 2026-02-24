# SSH Honeypot

A cloud-deployed SSH honeypot that captures real-world brute force attempts from internet-facing attackers and visualizes attack data through a live observability stack.

## Overview

This project simulates an SSH server to attract and log automated attack attempts from across the internet. Rather than using an existing honeypot tool, the SSH server is programmed from scratch using Paramiko, giving full control over what gets captured and logged. Attack data is enriched with geolocation information and fed into a Prometheus + Grafana monitoring stack for real-time visualization.

## Screenshots
![Grafana Dashboard](SSH-Honeypot-Grafana-Dashboard.png)

## Architecture

```
Internet Traffic
      │
      ▼
┌─────────────┐     writes      ┌──────────────────┐
│  Honeypot   │ ─────────────▶  │ connections.jsonl │
│ (Port 22)   │                 └──────────────────┘
└─────────────┘                          │
                                         │ reads
                                         ▼
                                 ┌──────────────┐
                                 │   Exporter   │
                                 │  (Port 8000) │
                                 └──────────────┘
                                         │
                                         │ scrapes
                                         ▼
                                 ┌──────────────┐
                                 │  Prometheus  │
                                 │  (Port 9090) │
                                 └──────────────┘
                                         │
                                         │ queries
                                         ▼
                                 ┌──────────────┐
                                 │   Grafana    │
                                 │  (Port 3000) │
                                 └──────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| `honeypot.py` | Custom SSH server built with Paramiko. Accepts connections, captures credentials, enriches with geolocation, and logs to JSON |
| `geoip.py` | Geolocation module that queries ip-api.com to resolve attacker IPs to country, city, and coordinates. Includes in-memory caching to respect API rate limits |
| `exporter.py` | Prometheus metrics exporter that parses the JSON log file and exposes attack metrics on port 8000 |
| Prometheus | Scrapes the exporter every 15 seconds and stores time series metrics |
| Grafana | Visualizes metrics in real-time dashboards including time series graphs and a world map of attack origins |

## Features

- Custom multi-threaded SSH server with semaphore-based concurrency (up to 50 simultaneous sessions)
- Captures attacker IP, credentials attempted, SSH client banner, connection duration, and geolocation
- Real-time Grafana dashboards showing total attempts, unique attacker IPs, credential patterns, and attack origins on a world map
- Rotating file logging with structured JSON output for easy parsing
- Fully containerized with Docker Compose for portable, reproducible deployment
- Persistent storage for logs and Prometheus data across container restarts

## Tech Stack

- **Python** — Honeypot server, geolocation module, metrics exporter
- **Paramiko** — SSH protocol implementation
- **Docker / Docker Compose** — Containerization and service orchestration
- **Prometheus** — Metrics collection and storage
- **Grafana** — Data visualization
- **AWS EC2** — Cloud deployment

## Prerequisites

- Docker and Docker Compose
- AWS EC2 instance (or any Linux server with a public IP)
- Port 22 open to the internet on your server's firewall (Make sure actual SSH port is configured to something else, such as 2222, to which only you have access)

## Deployment

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/SSH-Honeypot.git
cd SSH-Honeypot
```

**2. Create the data directory**
```bash
mkdir -p Honeypot-Data
sudo chmod 777 Honeypot-Data
```

**3. Start all services**
```bash
docker-compose up -d
```

**4. Verify all containers are running**
```bash
docker-compose ps
```

**5. Access Grafana**

Navigate to `http://<your-server-ip>:3000` and log in with the default credentials (`admin` / `admin`). Add Prometheus as a data source using `http://prometheus:9090` and build your dashboards.

## Metrics Exposed

| Metric | Description |
|--------|-------------|
| `honeypot_total_attempts` | Total number of connection attempts logged |
| `honeypot_unique_ips` | Number of unique attacker IP addresses |
| `honeypot_total_credentials` | Total number of credential pairs attempted |
| `honeypot_attempts_by_location` | Attempts broken down by IP, country, city, and coordinates |

```

## Security Notes

- The honeypot always returns `AUTH_FAILED` — no attacker can gain access (May be updated to simulate real shell)
- The application runs as a non-root user inside the container
- Real SSH access to the server is on a non-standard port, restricted to trusted IPs only
- Prometheus and Grafana ports should be restricted to trusted IPs in your firewall rules
