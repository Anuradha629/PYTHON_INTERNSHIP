
from flask import Flask, render_template

app = Flask(__name__)

institute = {
    "name": "Bright Future Classes",
    "location": "Ahilyanagar, Hingoli",
    "Pin code": "431513",
    "contact": "+91 85******96",
    "email": "brightfuture@gmail.com"
}

students = [
    {"name": "Anuradha", "subject": "Python", "time": "6:00 AM - 8:00 AM"},
    {"name": "Kranti", "subject": "Python", "time": "6:00 AM - 8:00 AM"},
    {"name": "Vaishnvi", "subject": "Java", "time": "8:30 AM - 10:30 AM"},
    {"name": "Rutuja", "subject": "Microprecessor", "time": "11:00 AM - 12:00 PM"},
    {"name": "Aarti", "subject": "Data communication", "time": "4:00 PM - 5:00 PM"},
    {"name": "Shivani", "subject": "C", "time": "7:00 PM - 8:00 PM"},
    {"name": "Pooja", "subject": "C++", "time": "7:00 PM - 8:00 PM"},
   
]
    
teachers = [
    {"name": "Mehta sir", "subject": "Python", "experience": 10},
    {"name": "Satore sir", "subject": "Java", "experience": 8},
    {"name": "Zelam mam", "subject": "Microprecessor", "experience": 12},
    {"name": "Patil mam", "subject": "Data communication", "experience": 7},
    {"name": "Satore sir", "subject": "C++", "experience": 9}    
]

attendance = [
    {"name": "Anuradha", "status": "Present"},
    {"name": "Kranti", "status": "Absent"},
    {"name": "Vaishnvi", "status": "Present"},
    {"name": "Rutuja", "status": "Present"},
    {"name": "Aarti", "status": "Absent"},
    {"name": "Shivani", "status": "Present"},
    {"name": "Pooja", "status": "Present"}
]
fees = [
    {"name": "Anuradha", "total_fees": 4000, "paid_fees": 3000, "pending_fees": 1000},
    {"name": "Kranti", "total_fees": 4000, "paid_fees": 1500, "pending_fees": 2500},
    {"name": "Vaishnvi", "total_fees": 4000, "paid_fees": 2500, "pending_fees": 1500},
    {"name": "Rutuja", "total_fees": 4000, "paid_fees": 3000, "pending_fees":1000},
    {"name": "Aarti", "total_fees": 4000, "paid_fees": 2000, "pending_fees": 2000},
    {"name": "Shivani", "total_fees": 4000, "paid_fees": 3500, "pending_fees": 500},
    {"name": "Pooja", "total_fees": 4000, "paid_fees": 4000, "pending_fees": 0}
]
@app.route("/")
def home():
    return render_template("home.html", institute=institute)

@app.route("/students")
def students_page():
    return render_template("students.html", students=students)

@app.route("/teachers")
def teachers_page():
    return render_template("teachers.html", teachers=teachers)

@app.route("/attendance")
def attendance_page():
    return render_template("attendance.html", attendance=attendance)

@app.route("/fees")
def fees_page():
    return render_template("fees.html", fees=fees) 


if __name__ == "__main__":
    app.run(debug=True)