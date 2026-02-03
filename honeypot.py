import socket
import paramiko
import threading
import logging
from logging.handlers import RotatingFileHandler

# rotating logs with 3 backups
logger = logging.getLogger("honeypot")
logger.setLevel(level=logging.INFO)
handler = RotatingFileHandler(filename="test.log", maxBytes=1024*5, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

class SSH_Server(paramiko.ServerInterface):
    def check_auth_password(self, username, password):
        logger.info(f"{username}:{password}")
        return paramiko.AUTH_FAILED


    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_FAILED


def handle_connection(client_sock, server_key):
    transport = paramiko.Transport(client_sock)
    transport.add_server_key(server_key)
    ssh = SSH_Server()
    transport.start_server(server=ssh)


def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', 2222)) # for security reasons default ssh port 22 won't be used for lab purposes
    server_sock.listen(100)


    server_key = paramiko.RSAKey.generate(2048)


    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"Connection: {client_addr[0]}:{client_addr[1]}")
        t = threading.Thread(target=handle_connection, args = (client_sock, server_key))
        t.start()


if __name__ == "__main__":
    main()