"""
/main.py

Project: Fridrich-Server
Created: 24.05.2023
Author: Lukas Krahbichler
"""

import time
import socket
from sklearn.datasets import load_iris

data = load_iris()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 2432))

server.listen()

while True:
    client, add = server.accept()
    print("CONNECTION", add)
    client.send("Your are connected".encode("UTF-8"))
    client.send(f"{data['data'][:, 0]}\n".encode())
    time.sleep(2)
    client.send("Your are being disconnected".encode())
    client.close()
