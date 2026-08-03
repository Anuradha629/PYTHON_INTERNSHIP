from flask import Flask, render_template, request, redirect, flash, url_for,session
from datetime import date
import sqlite3

from db import get_connection, init_db
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "bright_future_secret_key"


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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



    # ===== Today Attendance Count =====

    today_date = date.today()


    today_present = conn.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE date=?
    AND status='Present'
    """,
    (today_date,)
    ).fetchone()[0]



    today_absent = conn.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE date=?
    AND status='Absent'
    """,
    (today_date,)
    ).fetchone()[0]

     
    # ===== Top 5 Students =====

    top_students = conn.execute("""
    SELECT
        students.name,
        students.course,
        performance.marks,
        performance.remark

    FROM performance

    INNER JOIN students
    ON performance.student_id = students.id

    ORDER BY performance.marks DESC

    LIMIT 5
    """).fetchall()

    conn.close()


    return render_template(
        "dashboard.html",
        students=students,
        teachers=teachers,
        paid_fee=paid_fee,
        total_fee=total_fee,
        pending_fee=pending_fee,
        attendance=attendance,
        top_students=top_students,  
        today_present=today_present,
        today_absent=today_absent,
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

    if session.get("role") != "admin":
            flash("Admins only! You do not have permission.", "danger")
            return redirect("/students")

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
        photo = request.files.get("photo")

        photo_filename = "default.png"

        if photo and photo.filename:

            if allowed_file(photo.filename):

                photo_filename = secure_filename(photo.filename)

                photo.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        photo_filename
                    )
                )

            else:

                flash(
                    "Only JPG, JPEG and PNG images are allowed.",
                    "danger"
                )

                return redirect("/add_student")


        conn = get_connection()

        try:

            conn.execute("""
                INSERT INTO students
                (
                    roll_no,name,father_name,surname,mobile,course,batch,address,admission_date,status,photo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                roll_no, name, father_name, surname, mobile, course, batch, address, admission_date, status, photo_filename
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
    cursor = conn.cursor()

    # Student Details
    cursor.execute("SELECT * FROM students  WHERE id=?", (id,))
    s = cursor.fetchone()

    # Student Performance
   
    cursor.execute("SELECT * FROM performance WHERE student_id=?", (id,))
    performance = cursor.fetchall()
    conn.close()


    return render_template(
        "view_student.html",
        s=s,
        performance=performance
    )

# ================= EDIT STUDENT =================
@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/students")

    conn = get_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        # ================= STUDENT PHOTO =================

        photo = request.files.get("photo")
        # By default, keep the existing photo
        photo_filename = student["photo"] or "default.png"

        if photo and photo.filename:

            if allowed_file(photo.filename):

                photo_filename = secure_filename(photo.filename)

                photo.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        photo_filename
                    )
                )

            else:

                conn.close()

                flash(
                    "Only JPG, JPEG and PNG images are allowed.",
                    "danger"
                )

                return redirect(f"/edit_student/{id}")

        # ================= UPDATE STUDENT =================

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
                status=?,
                photo=?
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
            photo_filename,
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
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/students")

    conn = get_connection()
    conn.execute(" DELETE FROM students WHERE id=?", (id,))
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

    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/teachers")

    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        mobile = request.form["mobile"]
        timing = request.form["timing"]
        experience = request.form["experience"]
        conn = get_connection()

        conn.execute("""
        INSERT INTO teachers
        (name,subject,mobile,timing,experience)VALUES(?,?,?,?,?)""",( name,subject,mobile,timing,experience ))
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
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/teachers")

    conn = get_connection()
    teacher = conn.execute("""
    SELECT *
    FROM teachers
    WHERE id=?
    """,
    (id,)).fetchone()

    if request.method=="POST":
        conn.execute("""
        UPDATE teachers SET name=?, subject=?, mobile=?,  timing=?, experience=?  WHERE id=? """,
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
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/teachers")

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

@app.route("/fees")
def fees():
    conn = get_connection()
    fees = conn.execute("""
    SELECT
    fees.id,
    fees.receipt_no,
    students.roll_no,
    students.name,
    fees.total_fee,
    fees.paid_fee,
    fees.date

    FROM fees
    INNER JOIN students
    ON fees.student_id = students.id
    ORDER BY fees.id ASC

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
        pending_fee=pending_fee,
       
    )

# -------- COLLECT FEE --------
@app.route("/collect_fee", methods=["GET","POST"])
def collect_fee():
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/fees")

    conn = get_connection()
    students = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    if request.method=="POST":
        student_id = request.form["student_id"]
        total_fee = request.form["total_fee"]
        paid_fee = request.form["paid_fee"]
        payment_date = request.form["date"]
        
       #Generate unique receipt number
        last_id = conn.execute("SELECT IFNULL(MAX(id), 0) FROM fees").fetchone()[0]

        receipt_no = f"BFCC-2026-{last_id+1:04d}"
        conn.execute("""
        INSERT INTO fees ( receipt_no, student_id, total_fee, paid_fee, date )
        VALUES(?,?,?,?,?)
        """,
        (
        receipt_no,
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


@app.route("/edit_fee/<int:id>", methods=["GET", "POST"])
def edit_fee(id):
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/fees")
    conn = get_connection()
    fee = conn.execute("SELECT * FROM fees WHERE id=?", (id,)).fetchone()
    if request.method == "POST":
        conn.execute("""
        UPDATE fees
        SET
            total_fee=?,
            paid_fee=?,
            date=?
        WHERE id=?
        """,
        (
            request.form["total_fee"],
            request.form["paid_fee"],
            request.form["date"],
            id
        ))

        conn.commit()
        conn.close()

        flash("Fee Updated Successfully", "success")
        return redirect("/fees")

    conn.close()
    return render_template("edit_fee.html", fee=fee)


# -------- FEE RECEIPT --------

@app.route("/fee_receipt/<int:id>")
def fee_receipt(id):
    conn = get_connection()

    receipt = conn.execute("""
    SELECT
    fees.id,
    fees.receipt_no,
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




# -------- ATTENDANCE LIST + ADD --------
@app.route("/attendance", methods=["GET","POST"])
def attendance():
    conn = get_connection()
    # All Students
    students = conn.execute(" SELECT * FROM students  ORDER BY roll_no ").fetchall()
    if request.method == "POST":
        
        # Only Admin can save attendance
        if session.get("role") != "admin":
            flash(
                "Admins only! You do not have permission.",
                "danger"
            )
            conn.close()
            return redirect("/attendance")
        
        attendance_date = request.form["date"]
        for student in students:
            student_id = student["id"]
            status = request.form.get(
                f"status_{student_id}"
            )


            # Check duplicate attendance

            existing = conn.execute("  SELECT *  FROM attendance  WHERE student_id=?  AND date=? ",
            (student_id,attendance_date)).fetchone()

            if existing:
                # Update existing attendance

                conn.execute("UPDATE attendance SET status=? WHERE student_id=?  AND date=?",
                (status, student_id, attendance_date  ))
            else:
                # Insert new attendance

                conn.execute("""
                    INSERT INTO attendance
                    (student_id,date,status
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
            "Attendance Saved Successfully", "success" )
        return redirect("/attendance")


    # Attendance Records

    attendance = conn.execute("""
        SELECT
        attendance.id,
        students.roll_no,
        students.name,
        students.course,
        attendance.date,
        attendance.status
        FROM attendance
        INNER JOIN students
        ON attendance.student_id = students.id
        ORDER BY attendance.date DESC,
        students.roll_no ASC

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
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/attendance")
    conn = get_connection()
    record = conn.execute("SELECT * FROM attendance WHERE id=? ", (id,)).fetchone()

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
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/attendance")
    conn = get_connection()
    conn.execute(" DELETE FROM attendance  WHERE id=?",(id,))
    conn.commit()
    conn.close()
    flash(
        "Attendance Deleted Successfully",
        "success"
    )


    return redirect("/attendance")

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        # Check existing user
        cursor.execute("""
            SELECT * FROM users 
            WHERE username=? OR email=?
        """, (username, email))

        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or Email already exists. Please use another one.", "danger")
            conn.close()
            return redirect("/register")


        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users(username,email,password)
            VALUES(?,?,?)
        """, (username, email, hashed_password))

        conn.commit()
        conn.close()

        flash("Registration successful. Please login.", "success")
        return redirect("/login")

    return render_template("register.html")


#=========Login route==========
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute(
        "SELECT * FROM users WHERE username=? OR email=?",
        (username,username)
        )
        user=cursor.fetchone()
        conn.close()


        if user and check_password_hash(user["password"],password):

            session["user_id"]=user["id"]
            session["username"]=user["username"]
            session["role"]=user["role"]

            flash(f"Welcome {user['username']}! Login successful.", "success")
            return redirect("/")
        else:

            flash("Invalid username or password. Please try again.", "danger")

    return render_template("login.html")

#==========Logout route==========
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out .", "danger")
    return redirect("/login")


#==========Performance=======
@app.route("/performance")
def performance():

    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
    SELECT 
    performance.*,
    students.name,
    students.course
    FROM performance
    JOIN students
    ON performance.student_id = students.id
    """)
    data=cursor.fetchall()
    conn.close()
    return render_template(
        "performance.html",
        performance=data
    )

#======marks according Performance=======

@app.route("/add_performance", methods=["GET","POST"])
def add_performance():
    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/performance")

    conn = get_connection()
    cursor = conn.cursor()


    if request.method == "POST":

        student_id = request.form["student_id"]

        marks = int(request.form["marks"])


        if marks >= 90:
            remark = "Excellent"

        elif marks >= 75:
            remark = "Very Good"

        elif marks >= 60:
            remark = "Good"

        else:
            remark = "Needs Improvement"



        cursor.execute(" INSERT INTO performance (student_id, marks, remark) VALUES (?,?,?) ",
        ( student_id, marks, remark ))
        conn.commit()
        conn.close()
        return redirect(url_for("performance"))

    cursor.execute("SELECT id,name,course FROM students")

    students = cursor.fetchall()
    conn.close()
    return render_template(
        "add_performance.html",
        students=students
    )

# ================= START APPLICATION =================
init_db()
if __name__=="__main__":

    app.run(debug=True)