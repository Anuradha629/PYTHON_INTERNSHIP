import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "coaching.db")
print("Database Path:", DATABASE)


# ================= DATABASE CONNECTION =================

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    # Enable Foreign Key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON")

    return conn



# ================= DATABASE CREATION =================

def init_db():

    conn = get_connection()

    cursor = conn.cursor()



    # ================= STUDENTS TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no INTEGER UNIQUE,
        name TEXT,
        father_name TEXT,
        surname TEXT,
        mobile TEXT,
        course TEXT,
        batch TEXT,
        address TEXT,
        admission_date TEXT,
        status TEXT

    )
    """)

        
    try:
       cursor.execute("ALTER TABLE students ADD COLUMN photo TEXT DEFAULT 'default.png'")
    except Exception:
        # Column already exists
        pass




    # ================= TEACHERS TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        subject TEXT,
        mobile TEXT,
        timing TEXT,
        experience TEXT

    )
    """)



    # ================= FEES TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fees(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_no TEXT UNIQUE,
        student_id INTEGER NOT NULL,
        total_fee INTEGER NOT NULL,
        paid_fee INTEGER NOT NULL,
        date TEXT NOT NULL,

        FOREIGN KEY(student_id)
        REFERENCES students(id)
        ON DELETE CASCADE

    )
    """)



    # ================= ATTENDANCE TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT,
        status TEXT,

        FOREIGN KEY(student_id)
        REFERENCES students(id)
        ON DELETE CASCADE

    )
    """)



    # ================= USERS TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        role TEXT DEFAULT 'student'

    )
    """)



    # ================= PERFORMANCE TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        marks INTEGER,
        remark TEXT,

        FOREIGN KEY(student_id)
        REFERENCES students(id)
        ON DELETE CASCADE

    )
    """)



    conn.commit()

    conn.close()