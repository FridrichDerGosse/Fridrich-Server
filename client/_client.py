"""
client/_client.py

Project: Fridrich-Server
Created: 11.05.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from socket import socket, AF_INET, SOCK_STREAM


##################################################
#                     Code                       #
##################################################

class Client(socket):

    def __init__(self, ip: str, port: int) -> None:
        super().__init__(AF_INET, SOCK_STREAM)

        self.connect((ip, port))
