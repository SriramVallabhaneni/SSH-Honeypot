import sqlite3

DB_FILE = "/data/connections.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

def initialize_db():
    conn, cursor = get_connection()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS connections (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   timestamp TEXT,
                   ip TEXT,
                   port INTEGER,
                   country TEXT,
                   city TEXT,
                   lat REAL,
                   lon REAL,
                   client_banner TEXT,
                   auth_attempts INTEGER,
                   duration REAL
                   )
                   ''')
    
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS credentials (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   connection_id INTEGER,
                   username TEXT,
                   password TEXT,
                   FOREIGN KEY (connection_id) REFERENCES connections(id)
                   )
                   ''')
    
    conn.commit()
    conn.close()

def insert_record(record):
    conn, cursor = get_connection()

    cursor.execute('''
                   INSERT INTO connections
                   (timestamp, ip, port, country, city, lat, lon, client_banner, auth_attempts, duration)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (
                       record['timestamp'],
                       record['ip'],
                       record['port'],
                       record['country'],
                       record['city'],
                       record['lat'],
                       record['lon'],
                       record['client_banner'],
                       record['auth_attempts'],
                       record['duration'],
                   ))
    
    connection_id = cursor.lastrowid

    for cred in record.get('credentials', []):
        cursor.execute ('''
                        INSERT INTO credentials
                        (connection_id, username, password)
                        VALUES (?, ?, ?)
                        ''', (connection_id, cred['username'], cred['password']))
    
    conn.commit()
    conn.close()

def query_total_attempts():
    conn, cursor = get_connection()
    
    cursor.execute('SELECT COUNT(*) FROM connections')
    result = cursor.fetchone()[0]
    conn.close()
    return result

def query_unique_ips():
    conn, cursor = get_connection()

    cursor.execute('SELECT COUNT(DISTINCT ip) FROM connections')
    result = cursor.fetchone()[0]
    conn.close()
    return result

def query_total_credentials():
    conn, cursor = get_connection()

    cursor.execute('SELECT COUNT(*) FROM credentials')
    result = cursor.fetchone()[0]
    conn.close()
    return result

def query_attempts_by_location():
    conn, cursor = get_connection()

    cursor.execute('''
                   SELECT ip, country, lat, lon, COUNT(*) as attempts
                   FROM connections
                   WHERE lat != 0 AND lon != 0
                   GROUP BY ip, country, lat, lon
                   ''')
    results = cursor.fetchall()
    conn.close()
    return results




