import sqlite3

DATABASE = "coaching.db"


# ================= DATABASE CONNECTION =================

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn



# ================= DATABASE CREATION =================

def init_db():

    conn = get_connection()

    cursor = conn.cursor()


    # Users Table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT

    )
    """)

    cursor.execute("""
    SELECT * FROM users
    WHERE username='Anuradha'
    """)

    user = cursor.fetchone()

    if not user:
        cursor.execute("""
        INSERT INTO users(username,password)
        VALUES(?,?)
        """,
        ("Anuradha","anuradha123"))


        # Students Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE,
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



    # Teachers Table

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



    # Fees Table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fees(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        total_fee INTEGER,
        paid_fee INTEGER,
        date TEXT

    )
    """)


    # Attendance Table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT

    )
    """)


    conn.commit()
    conn.close()