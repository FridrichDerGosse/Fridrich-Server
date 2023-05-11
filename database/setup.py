"""
postgres/_setup.py

Project: Fridrich-Server
Created: 11.05.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from typing import Any
import mysql.connector

from database._secrets import DB_PASSWORD


##################################################
#                     Code                       #
##################################################

class DataBaseSetup:
    """
    MySQL Database setup management
    """

    conn: mysql.connector.MySQLConnection | None
    cursor: Any | None

    def __init__(self) -> None:
        """
        Create setup manager
        """
        self.conn = None
        self.cursor = None

    def connect(
            self,
            host: str | None = "127.0.0.1",
            user: str | None = "root",
            password: str | None = None
    ) -> None:
        self.conn = mysql.connector.connect(host=host,
                                            user=user,
                                            password=password if password else DB_PASSWORD)
        self.cursor = self.conn.cursor()

    def create(
            self,
            db_name: str | None = "fridrich"
    ) -> None:
        """
        Create database and tables
        """
        self.cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")

        self.cursor.execute(f"CREATE DATABASE {db_name}")
        self.cursor.execute(f"USE {db_name}")

        self.cursor.execute("""
        CREATE TABLE user (
            ID int NOT NULL AUTO_INCREMENT,
            Name varchar(255) NOT NULL,
            Password varchar(255) NOT NULL,
            PRIMARY KEY(ID)
        )
        """)

        self.cursor.execute(f"DESCRIBE user")

        print(self.cursor.fetchall())

        # REMOVE


