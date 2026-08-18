from flask import Flask, render_template, request, redirect, flash, url_for,session
from datetime import date
import sqlite3

from functools import wraps
from flask import session

from db import get_connection, init_db
from groq import Groq
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "bright_future_secret_key"

# ================= GROQ AI CONFIGURATION =================

from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



#====== student login ======

def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first!", "warning")
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view
# ================= HOME =================

@app.route("/")
def home():
    return render_template("home.html")




#=======notes========
@app.route('/subject/<subject_name>')
def subject_notes(subject_name):
    return render_template(
        'subject_notes.html',
        subject_name=subject_name
    )
# ================= AI DATABASE ANALYSIS =================
def ask_ai(question):
    conn = get_connection()

    # ================= STUDENTS DATA =================
    students = conn.execute("""
        SELECT id, roll_no, name, course, batch, status
        FROM students
        ORDER BY roll_no
    """).fetchall()

    # ================= TEACHERS DATA =================
    teachers = conn.execute("""
        SELECT name, subject, mobile, timing, experience
        FROM teachers
        ORDER BY name
    """).fetchall()


    # ================= FEES DATA =================
    fees = conn.execute("""
        SELECT students.name, students.roll_no, fees.total_fee, fees.paid_fee,
            (fees.total_fee - fees.paid_fee) AS pending_fee,
            fees.date
        FROM fees
        INNER JOIN students
        ON fees.student_id = students.id
        ORDER BY students.name
    """).fetchall()


    # ================= ATTENDANCE DATA =================
    attendance = conn.execute("""
        SELECT  students.name, students.roll_no, attendance.date, attendance.status
        FROM attendance
        INNER JOIN students
        ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    """).fetchall()


    # ================= PERFORMANCE DATA =================
    performance = conn.execute("""
        SELECT students.name, students.roll_no, performance.marks, performance.remark
        FROM performance
        INNER JOIN students
        ON performance.student_id = students.id
        ORDER BY performance.marks DESC
    """).fetchall()


    conn.close()


    # ================= PREPARE DATABASE CONTEXT =================

    student_data = "\n".join(
        f"Roll No: {s['roll_no']}, "
        f"Name: {s['name']}, "
        f"Course: {s['course']}, "
        f"Batch: {s['batch']}, "
        f"Status: {s['status']}"
        for s in students
    )

    teacher_data = "\n".join(
    f"Teacher: {t['name']}, "
    f"Subject: {t['subject']}, "
    f"Mobile: {t['mobile']}, "
    f"Timing: {t['timing']}, "
    f"Experience: {t['experience']} years"
    for t in teachers
    )


    fee_data = "\n".join(
        f"Student: {f['name']}, "
        f"Roll No: {f['roll_no']}, "
        f"Total Fee: ₹{f['total_fee']}, "
        f"Paid: ₹{f['paid_fee']}, "
        f"Pending: ₹{f['pending_fee']}, "
        f"Date: {f['date']}"
        for f in fees
    )


    attendance_data = "\n".join(
        f"Student: {a['name']}, "
        f"Roll No: {a['roll_no']}, "
        f"Date: {a['date']}, "
        f"Status: {a['status']}"
        for a in attendance
    )


    performance_data = "\n".join(
        f"Student: {p['name']}, "
        f"Roll No: {p['roll_no']}, "
        f"Marks: {p['marks']}, "
        f"Remark: {p['remark']}"
        for p in performance
    )

    # ================= AI PROMPT =================

    database_context = f"""
STUDENT DATA:
{student_data if student_data else "No student records found."}

FEE DATA:
{fee_data if fee_data else "No fee records found."}

ATTENDANCE DATA:
{attendance_data if attendance_data else "No attendance records found."}

PERFORMANCE DATA:
{performance_data if performance_data else "No performance records found."}

TEACHER DATA:
{teacher_data if teacher_data else "No teacher records found."}
"""


    # ================= GROQ AI =================
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[

            {
                "role": "system",
                "content": """
You are the AI Assistant of Bright Future Coaching Classes.

You are connected to the coaching class management database.

IMPORTANT RULES:
1. Answer questions using ONLY the database information provided by the application.
2. Do NOT invent student names, fees, attendance, marks or any other information.
3. Keep the answer short and concise.
4. Answer in maximum 4-5 sentences.
5. If the requested information is not available in the database, clearly say:
   "This information is not available in the database."
6. For pending fee use:
   Pending Fee = Total Fee - Paid Fee
7. Give clear, simple and professional answers.
8. If useful, show calculations.
9. If a Course exists in the database, explain it using general knowledge.
If a Course is not in the database, say: "This Course is not available in Bright Future Coaching Classes."
10. You can provide suggestions for coaching management, but clearly separate suggestions from actual database information.
If the question is about a course in our database, answer it normally using your knowledge. 
Don't say the information is unavailable.
11. If student marks are available in the database, provide simple and practical tips to improve their marks based on their performance.
12. Do not invent marks or performance details. Use only the marks provided by the application.
"""
            },

            {
                "role": "user",
                "content": f"""
DATABASE INFORMATION:

{database_context}

USER QUESTION:

{question}
"""
            }

        ],

        temperature=0.2
    )
    return response.choices[0].message.content
# ================= AI ASSISTANT =================
@app.route("/ai-assistant", methods=["GET", "POST"])
def ai_assistant():
    answer = None
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            try:
                answer = ask_ai(question)
            except Exception as e:

                print("Groq Error:", e)

                answer = "AI service is currently unavailable. Please try again."

    return render_template(
        "ai_assistant.html",
        answer=answer
    )

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

    # ===== Fee Progress Percentage =====
    paid_percentage = 0
    pending_percentage = 0

    if total_fee > 0:
        paid_percentage = round((paid_fee / total_fee) * 100, 1)
        pending_percentage = round((pending_fee / total_fee) * 100, 1)
  
    attendance = conn.execute("""
    SELECT COUNT(*)
    FROM attendance
    """).fetchone()[0]

    # ===== Today Attendance Count =====
    today_date = date.today().isoformat()
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
        paid_percentage=paid_percentage,
        pending_percentage=pending_percentage,
        attendance=attendance,
        top_students=top_students,  
        today_present=today_present,
        today_absent=today_absent,
        today=date.today()
    )



# ================= STUDENT LIST =================
@app.route("/students")
def students():
    search = request.args.get("search", "")
    course = request.args.get("course", "")
    batch = request.args.get("batch", "")
    status = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    per_page = 7
    offset = (page - 1) * per_page
    conn = get_connection()

    # ================= BASE QUERY =================
    query = """
        SELECT *
        FROM students
        WHERE 1=1
    """

    count_query = """
        SELECT COUNT(*)
        FROM students
        WHERE 1=1
    """
    params = []

    # ================= SEARCH =================
    if search:
        query += """
            AND name LIKE ?
        """
        count_query += """
            AND name LIKE ?
        """
        params.append("%" + search + "%")

    # ================= COURSE FILTER =================
    if course:
        query += """
            AND course = ?
        """
        count_query += """
            AND course = ?
        """
        params.append(course)

    # ================= BATCH FILTER =================
    if batch:
        query += """
            AND batch = ?
        """
        count_query += """
            AND batch = ?
        """
        params.append(batch)

    # ================= STATUS FILTER =================
    if status:
        query += """
            AND status = ?
        """
        count_query += """
            AND status = ?
        """
        params.append(status)

    # ================= TOTAL STUDENTS =================
    total = conn.execute(
        count_query,
        params
    ).fetchone()[0]
    # ================= PAGINATION =================
    query += """
        ORDER BY id ASC
        LIMIT ? OFFSET ?
    """
    students = conn.execute(
        query,
        params + [per_page, offset]
    ).fetchall()

    # ================= UNIQUE COURSES =================

    courses = conn.execute("""
        SELECT DISTINCT course
        FROM students
        WHERE course IS NOT NULL
        AND course != ''
        ORDER BY course
    """).fetchall()

    # ================= UNIQUE BATCHES =================

    batches = conn.execute("""
        SELECT DISTINCT batch
        FROM students
        WHERE batch IS NOT NULL
        AND batch != ''
        ORDER BY batch
    """).fetchall()

    conn.close()

    # ================= TOTAL PAGES =================

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "students.html",
        students=students,
        courses=courses,
        batches=batches,
        search=search,
        course=course,
        batch=batch,
        status=status,
        page=page,
        total_pages=total_pages
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
@login_required 
 
def fees(): 
    conn = get_connection() 
 
    page = request.args.get("page", 1, type=int) 
    per_page = 5 
    offset = (page - 1) * per_page 
 
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
    LIMIT ? OFFSET ? 
 
    """, (per_page, offset)).fetchall() 
 
 
    total_records = conn.execute(""" 
        SELECT COUNT(*) 
        FROM fees 
    """).fetchone()[0] 
 
    total_pages = (total_records + per_page - 1) // per_page 
 
 
    # =============================== 
    # TOTAL COLLECTION 
    # =============================== 
 
    total_collection = conn.execute(""" 
        SELECT IFNULL(SUM(paid_fee),0) 
        FROM fees 
    """).fetchone()[0] 
 
 
    # =============================== 
    # TOTAL STUDENTS 
    # =============================== 
 
    total_students = conn.execute(""" 
        SELECT COUNT(*) 
        FROM students 
    """).fetchone()[0] 
 
 
    # PENDING FEES 
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
        page=page, 
        total_pages=total_pages 
    )  


# -------- COLLECT FEE --------
@app.route("/collect_fee", methods=["GET", "POST"])
def collect_fee():

    if session.get("role") != "admin":
        flash("Admins only! You do not have permission.", "danger")
        return redirect("/fees")

    conn = get_connection()

    # Only students who do NOT have a fee record yet
    students = conn.execute("""
        SELECT *
        FROM students
        WHERE id NOT IN (
            SELECT student_id
            FROM fees
        )
        ORDER BY name
    """).fetchall()

    if request.method == "POST":

        student_id = request.form["student_id"]
        total_fee = int(request.form["total_fee"])
        paid_fee = int(request.form["paid_fee"])
        payment_date = request.form["date"]

        # Check again before inserting
        existing_fee = conn.execute("""
            SELECT id
            FROM fees
            WHERE student_id = ?
        """, (student_id,)).fetchone()

        if existing_fee:
            conn.close()

            flash(
                "Fee record already exists for this student. Please use Edit Fee for installments.",
                "warning"
            )

            return redirect("/fees")

        # Validate payment
        if paid_fee <= 0:
            conn.close()
            flash("Paid amount must be greater than 0.", "danger")
            return redirect("/collect_fee")

        if paid_fee > total_fee:
            conn.close()
            flash("Paid amount cannot be greater than total fee.", "danger")
            return redirect("/collect_fee")

        # Generate unique receipt number
        last_id = conn.execute(
            "SELECT IFNULL(MAX(id), 0) FROM fees"
        ).fetchone()[0]

        receipt_no = f"BFCC-2026-{last_id + 1:04d}"

        conn.execute("""
            INSERT INTO fees
            (
                receipt_no,
                student_id,
                total_fee,
                paid_fee,
                date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
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

    fee = conn.execute("""
        SELECT
            fees.*,
            students.name,
            students.roll_no,
            students.course
        FROM fees
        INNER JOIN students
        ON fees.student_id = students.id
        WHERE fees.id = ?
    """, (id,)).fetchone()

    if not fee:
        conn.close()
        flash("Fee record not found.", "danger")
        return redirect("/fees")

    if request.method == "POST":

        total_fee = int(request.form["total_fee"])
        paid_fee = int(request.form["paid_fee"])
        payment_date = request.form["date"]

        if paid_fee < 0:
            conn.close()
            flash("Paid amount cannot be negative.", "danger")
            return redirect(f"/edit_fee/{id}")

        if paid_fee > total_fee:
            conn.close()
            flash("Paid amount cannot be greater than total fee.", "danger")
            return redirect(f"/edit_fee/{id}")

        conn.execute("""
            UPDATE fees
            SET
                total_fee = ?,
                paid_fee = ?,
                date = ?
            WHERE id = ?
        """, (
            total_fee,
            paid_fee,
            payment_date,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            "Fee Updated Successfully",
            "success"
        )

        return redirect("/fees")

    conn.close()

    return render_template(
        "edit_fee.html",
        fee=fee
    )


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
@login_required

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


# ================= PERFORMANCE PAGE =================

@app.route("/performance")
def performance():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            performance.*,
            students.name,
            students.course,
            students.roll_no
        FROM performance
        JOIN students
        ON performance.student_id = students.id
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "performance.html",
        performance=data
    )


# ================= ADD PERFORMANCE =================

@app.route("/add_performance", methods=["GET", "POST"])
def add_performance():

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        student_id = request.form.get("student_id")
        marks = request.form.get("marks")

        # Student validation
        if not student_id:

            conn.close()

            flash(
                "Please select a student.",
                "danger"
            )

            return redirect(
                url_for("add_performance")
            )

        # Marks validation
        if not marks:

            conn.close()

            flash(
                "Please enter marks.",
                "danger"
            )

            return redirect(
                url_for("add_performance")
            )

        try:

            marks = float(marks)

        except ValueError:

            conn.close()

            flash(
                "Please enter valid marks.",
                "danger"
            )

            return redirect(
                url_for("add_performance")
            )

        # Marks range validation
        if marks < 0 or marks > 100:

            conn.close()

            flash(
                "Marks must be between 0 and 100.",
                "danger"
            )

            return redirect(
                url_for("add_performance")
            )

        # ================= AUTOMATIC REMARK =================

        if marks >= 90:
            remark = "Excellent!"

        elif marks >= 75:
            remark = "Very Good"

        elif marks >= 60:
            remark = "Good"

        elif marks >= 40:
            remark = "Needs Improvement"

        else:
            remark = " Work harder and improve !"

        # ================= SAVE =================

        cursor.execute("""
            INSERT INTO performance
            (student_id, marks, remark)
            VALUES (?, ?, ?)
        """, (
            student_id,
            marks,
            remark
        ))

        conn.commit()
        conn.close()

        flash(
            "Performance added successfully!",
            "success"
        )

        return redirect(
            url_for("performance")
        )

    # ================= GET =================

    cursor.execute("""
        SELECT
            id,
            name,
            roll_no,
            course
        FROM students
        ORDER BY name
    """)

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