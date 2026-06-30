from flask import Flask, render_template, request, redirect
from db import get_connection, close_connection

app = Flask(__name__)


# ---------------- INIT DATABASE ----------------
def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        course TEXT,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS fees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        amount INTEGER,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    close_connection(conn)


init_db()


# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    conn = get_connection()

    students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    fees = conn.execute("SELECT COUNT(*) FROM fees").fetchone()[0]
    attendance = conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]

    close_connection(conn)

    return render_template("dashboard.html",
                           students=students,
                           fees=fees,
                           attendance=attendance)


# ---------------- STUDENTS ----------------
@app.route("/students")
def students():
    conn = get_connection()
    data = conn.execute("SELECT * FROM students").fetchall()
    close_connection(conn)
    return render_template("students.html", students=data)


@app.route("/add_student", methods=["POST"])
def add_student():
    conn = get_connection()

    conn.execute(
        "INSERT INTO students(name,course,status) VALUES(?,?,?)",
        (request.form["name"], request.form["course"], request.form["status"])
    )

    conn.commit()
    close_connection(conn)

    return redirect("/students")


@app.route("/view_student/<int:id>")
def view_student(id):
    conn = get_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    close_connection(conn)

    return render_template("view_student.html", s=student)


@app.route("/edit_student/<int:id>", methods=["GET","POST"])
def edit_student(id):
    conn = get_connection()

    if request.method == "POST":
        conn.execute("""
        UPDATE students
        SET name=?, course=?, status=?
        WHERE id=?
        """, (
            request.form["name"],
            request.form["course"],
            request.form["status"],
            id
        ))

        conn.commit()
        close_connection(conn)
        return redirect("/students")

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    close_connection(conn)

    return render_template("edit_student.html", s=student)


@app.route("/delete_student/<int:id>")
def delete_student(id):
    conn = get_connection()

    conn.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    close_connection(conn)

    return redirect("/students")


# ---------------- FEES ----------------

@app.route("/fees")
def fees():
    conn = get_connection()

    # all fee records
    data = conn.execute("SELECT * FROM fees").fetchall()

    # total paid per student (SUM)
    paid_data = conn.execute("""
        SELECT student_name, SUM(amount) as paid
        FROM fees
        GROUP BY student_name
    """).fetchall()

    close_connection(conn)

    # convert to dictionary
    paid_dict = {row["student_name"]: row["paid"] for row in paid_data}

    # fixed total fees per student
    TOTAL_FEE = 10000

    return render_template(
        "fees.html",
        fees=data,
        paid=paid_dict,
        total=TOTAL_FEE
    )

@app.route("/add_fee", methods=["POST"])
def add_fee():
    conn = get_connection()

    student_name = request.form["student_name"]
    amount = request.form["amount"]
    status = request.form["status"]

    conn.execute(
        "INSERT INTO fees(student_name, amount, status) VALUES(?,?,?)",
        (student_name, amount, status)
    )

    conn.commit()
    close_connection(conn)

    return redirect("/fees")


# ---------------- ATTENDANCE ----------------

@app.route("/attendance", methods=["GET","POST"])
def attendance():
    conn = get_connection()
    students = conn.execute( "SELECT * FROM students" ).fetchall()


    if request.method == "POST":

        conn.execute(
            "INSERT INTO attendance(student_name,date,status) VALUES(?,?,?)",
            (
                request.form["student_name"],
                request.form["date"],
                request.form["status"]
            )
        )

        conn.commit()

    records = conn.execute("SELECT * FROM attendance ORDER BY id ASC").fetchall()


    close_connection(conn)


    return render_template(
        "attendance.html",
        students=students,
        records=records
    )

# -------- DELETE ATTENDANCE --------

@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):
    conn = get_connection()

    conn.execute("DELETE FROM attendance WHERE id=?", (id,))

    conn.commit()
    close_connection(conn)

    return redirect("/attendance")


# -------- EDIT ATTENDANCE --------

@app.route("/edit_attendance/<int:id>", methods=["GET","POST"])
def edit_attendance(id):

    conn = get_connection()


    record = conn.execute(
        "SELECT * FROM attendance WHERE id=?",
        (id,)
    ).fetchone()


    if request.method == "POST":

        conn.execute("""
            UPDATE attendance
            SET student_name=?, date=?, status=?
            WHERE id=?
        """,
        (
            request.form["student_name"],
            request.form["date"],
            request.form["status"],
            id
        ))

        conn.commit()
        close_connection(conn)

        return redirect("/attendance")


    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()


    close_connection(conn)


    return render_template(
        "edit_attendance.html",
        record=record,
        students=students
    )
init_db()
if __name__ == "__main__":
    app.run(debug=True)