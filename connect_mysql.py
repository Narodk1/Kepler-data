# connexion_basedonne.py
import mysql.connector

def connect_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="kepler_projet"
    )
