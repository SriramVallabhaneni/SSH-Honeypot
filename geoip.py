import requests
import time

# cache to store already looked up IPs
# Format: {ip: {country, city, lat, lon, timestamp}}
cache = {}
CACHE_TIMEOUT = 86400 # 24 hours in seconds

def get_location(ip):

    if ip in cache:
        if time.time() - cache[ip]['timestamp'] < CACHE_TIMEOUT:
            return cache[ip]

    # ingores local or private IPs    
    if ip.startswith(('127.', '10.', '192.168.', '172.')):
        return None
    
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=3)
        data = response.json()
        
        if data['status'] == 'success':
            result = {
                'country': data.get('country', 'Unkown'),
                'city': data.get('city', 'Uknown'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'timestamp': time.time()
            }
            cache[ip] = result
            return result
        
        return None

    except Exception:
        return None
