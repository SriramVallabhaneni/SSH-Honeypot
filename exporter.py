import time
from database import query_total_attempts, query_unique_ips, query_total_credentials, query_attempts_by_location 
from prometheus_client import start_http_server, Gauge

# Define metrics
total_attempts = Gauge('honeypot_total_attempts', 'Total number of connection attempts')
unique_ips = Gauge('honeypot_unique_ips', 'Number of unique attacker IPs')
total_credentials = Gauge('honeypot_total_credentials', 'Total number of credential attempts')
attempts_by_location = Gauge(
    'honeypot_attempts_by_location',
    'Attempts by location',
    ['ip', 'country', 'city', 'lat', 'lon']
)

def update_metrics():
    total_attempts.set(query_total_attempts())
    unique_ips.set(query_unique_ips())
    total_credentials.set(query_total_credentials())
    
    for row in query_attempts_by_location():
        attempts_by_location.labels(
            ip=row['ip'],
            country=row['country'],
            city=row['city'],
            lat=str(row['lat']),
            lon=str(row['lon'])
        ).set(row['attempts'])

if __name__ == "__main__":
    start_http_server(8000)
    print("Exporter running on port 8000")
    while True:
        update_metrics()
        time.sleep(15)