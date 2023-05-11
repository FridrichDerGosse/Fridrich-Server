"""
/setup.py

Project: Fridrich-Server
Created: 11.05.2023
Author: Lukas Krahbichler
"""

##################################################
#                    Imports                     #
##################################################

from database.setup import DataBaseSetup


##################################################
#                     Code                       #
##################################################

if __name__ == '__main__':
    setup = DataBaseSetup()
    setup.connect()
    setup.create()
