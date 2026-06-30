import sqlite3

DB = "coaching.db"

def get_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def close_connection(conn):
    if conn:
        conn.close()