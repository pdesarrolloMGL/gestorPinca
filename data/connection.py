import sqlite3
import os

_conn = None

def get_connection():
    global _conn
    if _conn is None:
        ruta_db = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'pinca.db')
        )
        _conn = sqlite3.connect(ruta_db)
    return _conn