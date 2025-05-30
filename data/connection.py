import sqlite3
import os

def get_connection():
    ruta_db = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'pinca.db')
    )
    conn = sqlite3.connect(ruta_db)
    return conn