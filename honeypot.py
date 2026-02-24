import socket
import paramiko
import threading
import logging
from logging.handlers import RotatingFileHandler
import os
import json
import time
from geoip import get_location

# rotating logs with 3 backups
logger = logging.getLogger("honeypot")
logger.setLevel(level=logging.INFO)
handler = RotatingFileHandler("/data/test.log", maxBytes=1024*5, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

KEY_FILE = "/data/server.key"

JSON_FILE = "/data/connections.jsonl"

semaphore = threading.Semaphore(50)

class SSH_Server(paramiko.ServerInterface):
    def __init__(self, client_addr):
        self.client_addr = client_addr
        self.auth_attempts = []

    def check_auth_password(self, username, password):
        self.auth_attempts.append({"username": username, "password": password})
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_FAILED

# keeps same server key, generates server key if not already created
def key_handling():
    if not os.path.exists(KEY_FILE):
        server_key = paramiko.RSAKey.generate(2048)
        server_key.write_private_key_file(KEY_FILE)
        logger.info("Generated new SSH host key")
    else:
        server_key = paramiko.RSAKey(filename=KEY_FILE)
        logger.info("Loaded existing SSH host key")
    return server_key

# handles recording attempt to json file
def write_json_record(record):
    with open(JSON_FILE, "a") as file:
        file.write(json.dumps(record) + "\n")
        file.flush()


# limits to 50 connections
def handle_connection(client_sock, server_key, client_addr):
    with semaphore:
        start_time = time.time()
        ssh = None
        client_banner = None
        transport = None

        try:
            transport = paramiko.Transport(client_sock)
            transport.local_version = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"
            transport.add_server_key(server_key)
            ssh = SSH_Server(client_addr)
            transport.start_server(server=ssh)
            client_banner=transport.remote_version
            transport.accept(5)

        except Exception as e:
            logger.warning(f"{client_addr[0]}:{client_addr[1]} - {e}")

        finally:
            duration = round(time.time() - start_time, 2)
            location = get_location(client_addr[0])

            record = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "ip": client_addr[0],
                "port": client_addr[1],
                "country": location['country'] if location else "Unknown",
                "city": location['city'] if location else "Unknown",
                "lat": location['lat'] if location else 0,
                "lon": location['lon'] if location else 0,
                "client_banner": client_banner,
                "auth_attempts": len(ssh.auth_attempts) if ssh else 0,
                "credentials": ssh.auth_attempts if ssh else [],
                "duration": duration
            }

            write_json_record(record)

            if transport:
                try:
                    transport.close()
                except:
                    pass

            client_sock.close()


def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', 22)) # make sure to change default ssh port to something else
    server_sock.listen(100)

    server_key = key_handling()

    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            logger.info(f"Connection: {client_addr[0]}:{client_addr[1]}")
            t = threading.Thread(target=handle_connection, args = (client_sock, server_key, client_addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        logger.info("Honeypot shutting down")
    finally:
        server_sock.close()


if __name__ == "__main__":
    main()