"""
postgres/_setup.py

Project: Fridrich-Server
Created: 11.05.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from typing import TYPE_CHECKING
import mysql.connector

from database._secrets import DB_PASSWORD

if TYPE_CHECKING:
    import mysql.connector.connection


##################################################
#                     Code                       #
##################################################

class DataBaseSetup:
    """
    MySQL Database setup management
    """

    conn: mysql.connector.MySQLConnection | None
    cursor: mysql.connector.connection.MySQLCursor | None

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
        """
        Connect to the database
        :param host: hostname for db login
        :param user: user for db login
        :param password: pw for db login
        """
        print("Connecting to MySQL Server...")

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
        :param db_name: Name of the database
        """
        self.cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        if db_name in self.cursor.fetchone():
            confirm = input("\n!!! - WARNING - !!!\n\n"
                            "Database already exists!\n"
                            "Type CONFIRM if you want to delete it to create a new one!\n"
                            "ATTENTION: All data will be LOST\n\n"
                            "-> ")
            if confirm != "CONFIRM":
                return

            print("Deleting old database...")

            self.cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")

        print("Creating new database...")
        self.cursor.execute(f"CREATE DATABASE {db_name}")
        self.cursor.execute(f"USE {db_name}")

        print("")

        # Create independent tables
        self.__create_user()
        self.__create_pattern()

        # Create dependent tables
        self.__create_permissions()
        self.__create_connection()
        self.__create_voting()
        self.__create_voting_codex()
        self.__create_chat()
        self.__create_calender()

    def __create_user(self) -> None:
        """
        Create user and options table
        """
        print("Creating user tables...")

        self.cursor.execute("""
        CREATE TABLE users (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            label VARCHAR(256) NOT NULL,
            password VARCHAR(1024) NOT NULL,
            options_id INT UNSIGNED NOT NULL,
            double_votes SMALLINT UNSIGNED NOT NULL DEFAULT 0,
            permissionlevel_id INT UNSIGNED NOT NULL DEFAULT 0,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE useroptions (
            user_id INT UNSIGNED NOT NULL,
            displayname VARCHAR(256),
            status VARCHAR(64),
            description VARCHAR(1024),
            telephone VARCHAR(64),
            email VARCHAR(64),
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
            PRIMARY KEY (user_id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE pronoun (
            id INT UNSIGNED NOT NULL,
            label VARCHAR(64) NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        # Relationships
        self.cursor.execute("""
        CREATE TABLE useroptions_pronoun (
            user_id INT UNSIGNED NOT NULL,
            pronoun_id INT UNSIGNED NOT NULL,
            FOREIGN KEY (user_id) REFERENCES useroptions(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (pronoun_id) REFERENCES pronoun(id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT id PRIMARY KEY (user_id, pronoun_id)
        ) ENGINE=InnoDB
        """)

    def __create_pattern(self) -> None:
        """
        Create pattern table
        """
        print("Creating pattern table...")

        self.cursor.execute("""
        CREATE TABLE pattern (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            patterntype VARCHAR(64) NOT NULL,
            patterndetails VARCHAR(256) NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

    def __create_permissions(self) -> None:
        """
        Create permission tables with references
        """
        print("Creating permission tables...")

        self.cursor.execute("""
        CREATE TABLE permission (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            label VARCHAR(64) NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB;
        """)

        self.cursor.execute("""
        CREATE TABLE permissionlevel (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            label VARCHAR(64) NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        # Relationships
        self.cursor.execute("""
        CREATE TABLE permissionlevel_permission (
            permissionlevel_id INT UNSIGNED NOT NULL,
            permission_id INT UNSIGNED NOT NULL,
            FOREIGN KEY (permissionlevel_id) REFERENCES permissionlevel(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permission(id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT id PRIMARY KEY (permissionlevel_id, permission_id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE user_permission(
            user_id INT UNSIGNED NOT NULL,
            permission_id INT UNSIGNED NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES Permission(id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT id PRIMARY KEY (user_id, permission_id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        ALTER TABLE users 
        ADD FOREIGN KEY (permissionlevel_id) REFERENCES Permissionlevel(id) ON UPDATE CASCADE ON DELETE SET DEFAULT
        """)

    def __create_voting(self) -> None:
        """
        Create voting tables
        """
        print("Creating voting tables...")

        self.cursor.execute("""
        CREATE TABLE voting (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            label VARCHAR(64) NOT NULL,
            is_normal BOOLEAN DEFAULT 1,
            user_id INT UNSIGNED,
            pattern_id INT UNSIGNED,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
            FOREIGN KEY (pattern_id) REFERENCES pattern(id) ON UPDATE CASCADE ON DELETE SET NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE votingslave (
            voting_id INT UNSIGNED NOT NULL,
            votingslave_id INT UNSIGNED NOT NULL,
            start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_id INT UNSIGNED,
            INDEX (end_time),
            FOREIGN KEY (voting_id) REFERENCES voting(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
            CONSTRAINT id PRIMARY KEY (votingslave_id, voting_id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE votingoption (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            label VARCHAR(64) NOT NULL,
            is_user_id INT UNSIGNED,
            created_user_id INT UNSIGNED,
            FOREIGN KEY (is_user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
            FOREIGN KEY (created_user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE vote (
            voting_id INT UNSIGNED NOT NULL,
            votingslave_id INT UNSIGNED NOT NULL,
            vote_id INT UNSIGNED NOT NULL,
            timepoint TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            voting_option_id INT UNSIGNED NOT NULL,
            user_id INT UNSIGNED,
            FOREIGN KEY (voting_id) REFERENCES votingslave(voting_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (votingslave_id) REFERENCES votingslave(votingslave_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (voting_option_id) REFERENCES votingoption(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
            CONSTRAINT id PRIMARY KEY (voting_id, votingslave_id, vote_id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE votingresult (
            voting_id INT UNSIGNED NOT NULL,
            votingslave_id INT UNSIGNED NOT NULL,
            votingoption_id INT UNSIGNED NOT NULL,
            votes INT UNSIGNED DEFAULT 0,
            FOREIGN KEY (voting_id) REFERENCES votingslave(voting_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (votingslave_id) REFERENCES votingslave(votingslave_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (votingoption_id) REFERENCES votingoption(id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT id PRIMARY KEY (voting_id, votingslave_id, votingoption_id)
        ) ENGINE=InnoDB
        """)

        # Relationships
        self.cursor.execute("""
        CREATE TABLE votingslave_votingoption (
            voting_id INT UNSIGNED NOT NULL,
            votingslave_id INT UNSIGNED NOT NULL,
            votingoption_id INT UNSIGNED NOT NULL,
            FOREIGN KEY (voting_id) REFERENCES votingslave(voting_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (votingslave_id) REFERENCES votingslave(votingslave_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (votingoption_id) REFERENCES votingoption(id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT id PRIMARY KEY (votingslave_id, votingoption_id)
        ) ENGINE=InnoDB
        """)

    def __create_voting_codex(self) -> None:
        """
        Create codex tables (Voting tables must already exist)
        """
        print("Creating codex tables...")

        self.cursor.execute("""
        CREATE TABLE codex (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            label VARCHAR(64) NOT NULL,
            passthrough TINYINT(100) UNSIGNED NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE paragraph (
            codex_id INT UNSIGNED NOT NULL,
            paragraph_id INT UNSIGNED NOT NULL,
            label VARCHAR(64) NOT NULL,
            INDEX (paragraph_id),
            FOREIGN KEY (codex_id) REFERENCES codex(id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT id PRIMARY KEY (codex_id, paragraph_id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE subparagraph (
            codex_id INT UNSIGNED NOT NULL,
            paragraph_id INT UNSIGNED NOT NULL,
            subparagraph_id INT UNSIGNED NOT NULL,
            text VARCHAR(1024) NOT NULL,
            voting_id INT UNSIGNED,
            FOREIGN KEY (codex_id) REFERENCES paragraph(codex_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (paragraph_id) REFERENCES paragraph(paragraph_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (voting_id) REFERENCES voting(id) ON UPDATE CASCADE ON DELETE SET NULL,
            CONSTRAINT id PRIMARY KEY (codex_id, paragraph_id, subparagraph_id)
        ) ENGINE=InnoDB
        """)

    def __create_chat(self) -> None:
        """
        Create chat and message table
        """
        print("Creating chat tables...")

        self.cursor.execute("""
        CREATE TABLE chat (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            label VARCHAR(64) NOT NULL,
            creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_id INT UNSIGNED,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE message (
            chat_id INT UNSIGNED NOT NULL,
            message_id INT UNSIGNED NOT NULL,
            label VARCHAR(256) NOT NULL,
            send_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_id INT UNSIGNED,
            FOREIGN KEY (chat_id) REFERENCES chat(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
            CONSTRAINT id PRIMARY KEY (chat_id, message_id)
        ) ENGINE=InnoDB
        """)

        # Relationships

        self.cursor.execute("""
        CREATE TABLE users_chat (
            user_id INT UNSIGNED NOT NULL,
            chat_id INT UNSIGNED NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (chat_id) REFERENCES chat(id) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT id PRIMARY KEY (user_id, chat_id)
        ) ENGINE=InnoDB
        """)

    def __create_calender(self) -> None:
        """
        Create calender tables
        """
        print("Creating calender tables...")
        # Work for later

    def __create_connection(self) -> None:
        """
        Create connection tables
        """
        print("Creating connection tables...")

        self.cursor.execute("""
        CREATE TABLE encryption (
            id INT UNSIGNED NOT NULL,
            lease_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            own_public VARCHAR(64) NOT NULL,
            own_private VARCHAR(64) NOT NULL,
            client_public VARCHAR(64) NOT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB
        """)

        self.cursor.execute("""
        CREATE TABLE connection (
            user_id INT UNSIGNED NOT NULL,
            connection_id INT UNSIGNED NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            lease_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            encryption_id INT UNSIGNED,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (encryption_id) REFERENCES encryption(id) ON UPDATE CASCADE ON DELETE SET NULL,
            CONSTRAINT id PRIMARY KEY (user_id, connection_id)
        ) ENGINE=InnoDB
        """)
