from flask import Flask, render_template, request, redirect, flash
from datetime import date
import sqlite3

from db import get_connection, init_db


app = Flask(__name__)

app.secret_key = "bright_future_secret_key"


# ================= HOME =================

@app.route("/")
def home():
    return render_template("home.html")



# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    conn = get_connection()


    students = conn.execute("""
    SELECT COUNT(*)
    FROM students
    """).fetchone()[0]


    teachers = conn.execute("""
    SELECT COUNT(*)
    FROM teachers
    """).fetchone()[0]


    paid_fee = conn.execute("""
    SELECT IFNULL(SUM(paid_fee),0)
    FROM fees
    """).fetchone()[0]


    total_fee = conn.execute("""
    SELECT IFNULL(SUM(total_fee),0)
    FROM fees
    """).fetchone()[0]


    pending_fee = total_fee - paid_fee


    attendance = conn.execute("""
    SELECT COUNT(*)
    FROM attendance
    """).fetchone()[0]


    conn.close()


    return render_template(
        "dashboard.html",
        students=students,
        teachers=teachers,
        paid_fee=paid_fee,
        total_fee=total_fee,
        pending_fee=pending_fee,
        attendance=attendance,
        today=date.today()
    )



# ================= STUDENT LIST =================

@app.route("/students")
def students():

    search = request.args.get("search")


    conn = get_connection()


    if search:

        students = conn.execute("""
        SELECT *
        FROM students
        WHERE name LIKE ?
        OR mobile LIKE ?
        OR course LIKE ?
        ORDER BY id ASC
        """,
        (
            "%"+search+"%",
            "%"+search+"%",
            "%"+search+"%"
        )).fetchall()


    else:

        students = conn.execute("""
        SELECT *
        FROM students
        ORDER BY id ASC
        """).fetchall()



    conn.close()


    return render_template(
        "students.html",
        students=students
    )



# ================= ADD STUDENT =================

@app.route("/add_student", methods=["GET","POST"])
def add_student():


    if request.method == "POST":

        roll_no = request.form["roll_no"]
        name = request.form["name"]
        father_name = request.form["father_name"]
        surname = request.form["surname"]
        mobile = request.form["mobile"]
        course = request.form["course"]
        batch = request.form["batch"]
        address = request.form["address"]
        admission_date = request.form["admission_date"]
        status = request.form["status"]


        conn = get_connection()


        try:

            conn.execute("""
            INSERT INTO students
            (
            roll_no,
            name,
            father_name,
            surname,
            mobile,
            course,
            batch,
            address,
            admission_date,
            status
            )

            VALUES(?,?,?,?,?,?,?,?,?,?)

            """,
            (
            roll_no,
            name,
            father_name,
            surname,
            mobile,
            course,
            batch,
            address,
            admission_date,
            status
            ))


            conn.commit()
            conn.close()


            flash(
                "Student Added Successfully",
                "success"
            )


            return redirect("/students")


        except sqlite3.IntegrityError:


            conn.close()


            flash(
                "Roll Number Already Exists",
                "danger"
            )


            return redirect("/add_student")



    return render_template("add_student.html")



# ================= VIEW STUDENT =================

@app.route("/view_student/<int:id>")
def view_student(id):

    conn = get_connection()


    student = conn.execute("""
    SELECT *
    FROM students
    WHERE id=?
    """,
    (id,)).fetchone()


    conn.close()


    return render_template(
        "view_student.html",
        s=student
    )



# ================= EDIT STUDENT =================

@app.route("/edit_student/<int:id>", methods=["GET","POST"])
def edit_student(id):


    conn = get_connection()


    student = conn.execute("""
    SELECT *
    FROM students
    WHERE id=?
    """,
    (id,)).fetchone()



    if request.method=="POST":


        conn.execute("""
        UPDATE students SET

        roll_no=?,
        name=?,
        father_name=?,
        surname=?,
        mobile=?,
        course=?,
        batch=?,
        address=?,
        admission_date=?,
        status=?

        WHERE id=?

        """,
        (
        request.form["roll_no"],
        request.form["name"],
        request.form["father_name"],
        request.form["surname"],
        request.form["mobile"],
        request.form["course"],
        request.form["batch"],
        request.form["address"],
        request.form["admission_date"],
        request.form["status"],
        id
        ))


        conn.commit()
        conn.close()


        flash(
            "Student Updated Successfully",
            "success"
        )


        return redirect("/students")



    conn.close()


    return render_template(
        "edit_student.html",
        s=student
    )



# ================= DELETE STUDENT =================

@app.route("/delete_student/<int:id>")
def delete_student(id):


    conn = get_connection()


    conn.execute("""
    DELETE FROM students
    WHERE id=?
    """,
    (id,))


    conn.commit()
    conn.close()


    flash(
        "Student Deleted Successfully",
        "success"
    )


    return redirect("/students")



# ================= STUDENT ID CARD =================

@app.route("/student_id_card/<int:id>")
def student_id_card(id):


    conn = get_connection()


    student = conn.execute("""
    SELECT *
    FROM students
    WHERE id=?
    """,
    (id,)).fetchone()


    conn.close()


    return render_template(
        "student_id_card.html",
        s=student
    )
# ================= TEACHER MODULE =================


# -------- TEACHER LIST --------

@app.route("/teachers")
def teachers():

    conn = get_connection()


    teachers = conn.execute("""
    SELECT *
    FROM teachers
    ORDER BY id ASC
    """).fetchall()


    conn.close()


    return render_template(
        "teachers.html",
        teachers=teachers
    )



# -------- ADD TEACHER --------

@app.route("/add_teacher", methods=["GET","POST"])
def add_teacher():


    if request.method == "POST":


        name = request.form["name"]
        subject = request.form["subject"]
        mobile = request.form["mobile"]
        timing = request.form["timing"]
        experience = request.form["experience"]


        conn = get_connection()


        conn.execute("""
        INSERT INTO teachers
        (
        name,
        subject,
        mobile,
        timing,
        experience
        )

        VALUES(?,?,?,?,?)

        """,
        (
        name,
        subject,
        mobile,
        timing,
        experience
        ))


        conn.commit()
        conn.close()


        flash(
            "Teacher Added Successfully",
            "success"
        )


        return redirect("/teachers")



    return render_template(
        "add_teacher.html"
    )



# -------- EDIT TEACHER --------

@app.route("/edit_teacher/<int:id>", methods=["GET","POST"])
def edit_teacher(id):


    conn = get_connection()


    teacher = conn.execute("""
    SELECT *
    FROM teachers
    WHERE id=?
    """,
    (id,)).fetchone()



    if request.method=="POST":


        conn.execute("""
        UPDATE teachers SET

        name=?,
        subject=?,
        mobile=?,
        timing=?,
        experience=?

        WHERE id=?

        """,
        (
        request.form["name"],
        request.form["subject"],
        request.form["mobile"],
        request.form["timing"],
        request.form["experience"],
        id
        ))


        conn.commit()
        conn.close()


        flash(
            "Teacher Updated Successfully",
            "success"
        )


        return redirect("/teachers")



    conn.close()


    return render_template(
        "edit_teacher.html",
        t=teacher
    )



# -------- DELETE TEACHER --------

@app.route("/delete_teacher/<int:id>")
def delete_teacher(id):


    conn = get_connection()


    conn.execute("""
    DELETE FROM teachers
    WHERE id=?
    """,
    (id,))


    conn.commit()
    conn.close()


    flash(
        "Teacher Deleted Successfully",
        "success"
    )


    return redirect("/teachers")





# ================= FEES MODULE =================



# -------- FEES LIST --------

@app.route("/fees")
def fees():
    conn = get_connection()
    fees = conn.execute("""
    SELECT
    fees.id,
    students.roll_no,
    students.name,
    fees.total_fee,
    fees.paid_fee,
    fees.date

    FROM fees
    INNER JOIN students
    ON fees.student_id = students.id
    ORDER BY fees.id DESC

    """).fetchall()



    total_collection = conn.execute("""
    SELECT IFNULL(SUM(paid_fee),0)
    FROM fees
    """).fetchone()[0]



    total_students = conn.execute("""
    SELECT COUNT(*)
    FROM students
    """).fetchone()[0]



    pending_fee = conn.execute("""
    SELECT IFNULL(SUM(total_fee-paid_fee),0)
    FROM fees
    """).fetchone()[0]



    conn.close()



    return render_template(
        "fees.html",
        fees=fees,
        total_collection=total_collection,
        total_students=total_students,
        pending_fee=pending_fee
    )





# -------- COLLECT FEE --------

@app.route("/collect_fee", methods=["GET","POST"])
def collect_fee():


    conn = get_connection()



    students = conn.execute("""
    SELECT *
    FROM students
    ORDER BY name
    """).fetchall()



    if request.method=="POST":


        student_id = request.form["student_id"]

        total_fee = request.form["total_fee"]

        paid_fee = request.form["paid_fee"]

        payment_date = request.form["date"]



        conn.execute("""
        INSERT INTO fees

        (
        student_id,
        total_fee,
        paid_fee,
        date
        )

        VALUES(?,?,?,?)

        """,
        (
        student_id,
        total_fee,
        paid_fee,
        payment_date
        ))



        conn.commit()
        conn.close()



        flash(
            "Fee Collected Successfully",
            "success"
        )


        return redirect("/fees")



    conn.close()



    return render_template(
        "collect_fee.html",
        students=students
    )





# -------- FEE RECEIPT --------

@app.route("/fee_receipt/<int:id>")
def fee_receipt(id):
    conn = get_connection()


    receipt = conn.execute("""
    SELECT

    fees.id,

    students.roll_no,

    students.name,

    students.course,

    fees.total_fee,

    fees.paid_fee,

    (fees.total_fee - fees.paid_fee) AS pending_fee,

    fees.date


    FROM fees


    INNER JOIN students


    ON fees.student_id = students.id


    WHERE fees.id=?

    """,
    (id,)).fetchone()



    conn.close()



    return render_template(
        "fee_receipt.html",
        receipt=receipt
    )
# ================= ATTENDANCE MODULE =================


# -------- ATTENDANCE LIST + ADD --------

@app.route("/attendance", methods=["GET","POST"])
def attendance():


    conn = get_connection()


    students = conn.execute("""
    SELECT *
    FROM students
    ORDER BY name
    """).fetchall()



    if request.method=="POST":


        student_id = request.form["student_id"]

        attendance_date = request.form["date"]

        status = request.form["status"]



        conn.execute("""
        INSERT INTO attendance

        (
        student_id,
        date,
        status
        )

        VALUES(?,?,?)

        """,
        (
        student_id,
        attendance_date,
        status
        ))


        conn.commit()
        conn.close()


        flash(
            "Attendance Added Successfully",
            "success"
        )


        return redirect("/attendance")




    attendance = conn.execute("""
    SELECT

    attendance.id,

    students.name,

    students.roll_no,

    attendance.date,

    attendance.status


    FROM attendance


    INNER JOIN students


    ON attendance.student_id = students.id


    ORDER BY attendance.id DESC


    """).fetchall()



    conn.close()



    return render_template(
        "attendance.html",
        students=students,
        attendance=attendance
    )





# -------- EDIT ATTENDANCE --------

@app.route("/edit_attendance/<int:id>", methods=["GET","POST"])
def edit_attendance(id):


    conn = get_connection()



    record = conn.execute("""
    SELECT *
    FROM attendance
    WHERE id=?
    """,
    (id,)).fetchone()



    if request.method=="POST":


        conn.execute("""
        UPDATE attendance SET

        date=?,
        status=?

        WHERE id=?

        """,
        (
        request.form["date"],
        request.form["status"],
        id
        ))


        conn.commit()
        conn.close()



        flash(
            "Attendance Updated Successfully",
            "success"
        )


        return redirect("/attendance")



    conn.close()



    return render_template(
        "edit_attendance.html",
        record=record
    )





# -------- DELETE ATTENDANCE --------

@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):


    conn = get_connection()


    conn.execute("""
    DELETE FROM attendance
    WHERE id=?
    """,
    (id,))


    conn.commit()
    conn.close()



    flash(
        "Attendance Deleted Successfully",
        "success"
    )


    return redirect("/attendance")







# ================= REPORTS MODULE =================


@app.route("/reports")
def reports():


    conn = get_connection()



    # Student Count

    total_students = conn.execute("""
    SELECT COUNT(*)
    FROM students
    """).fetchone()[0]




    # Fees Report

    total_fee = conn.execute("""
    SELECT IFNULL(SUM(total_fee),0)
    FROM fees
    """).fetchone()[0]



    paid_fee = conn.execute("""
    SELECT IFNULL(SUM(paid_fee),0)
    FROM fees
    """).fetchone()[0]



    pending_fee = total_fee - paid_fee





    # Attendance Report


    total_attendance = conn.execute("""
    SELECT COUNT(*)
    FROM attendance
    """).fetchone()[0]



    present = conn.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE status='Present'
    """).fetchone()[0]



    absent = conn.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE status='Absent'
    """).fetchone()[0]




    if total_attendance > 0:


        attendance_percentage = round(
            (present / total_attendance) * 100,
            2
        )


    else:

        attendance_percentage = 0





    # Course Wise Report


    courses = conn.execute("""
    SELECT

    course,

    COUNT(*) as count


    FROM students


    GROUP BY course

    """).fetchall()



    conn.close()



    return render_template(
        "reports.html",

        total_students=total_students,

        total_fee=total_fee,

        paid_fee=paid_fee,

        pending_fee=pending_fee,

        total_attendance=total_attendance,

        present=present,

        absent=absent,

        attendance_percentage=attendance_percentage,

        courses=courses
    )






# ================= START APPLICATION =================


init_db()



if __name__=="__main__":

    app.run(debug=True)