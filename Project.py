
students = [
    {
        "name": "Amit",
        "subject": "Python",
        "batch": "A", 
        "fees_paid": 2000, 
        "total_fees": 4000, 
        "attendance": 85
    },

    {
        "name": "Anuradha",
        "subject": "Python",
        "batch": "B", 
        "fees_paid": 1300, 
        "total_fees": 4000, 
        "attendance": 92
       
    },

    {   
        "name":"Sunita",
        "subject": "Python",
        "batch": "A", 
        "fees_paid": 1800, 
        "total_fees": 4000, 
        "attendance": 85
    },

    {
       "name": "Neha",
        "subject": "Python",
        "batch": "B", 
        "fees_paid": 2500, 
        "total_fees": 4000, 
        "attendance": 60
    },

    {
        "name": "Rohit",
        "subject": "Python",
        "batch": "A", 
        "fees_paid": 4000, 
        "total_fees": 4000, 
        "attendance": 95
    }
]
batches ={

    "A": "Morning Batch (8 AM - 10 AM)",
    "B": "Evening Batch (5 PM - 7 PM)",
  
    }
def get_status():
    stu_name=input("Enter Student Name which you want to search:") 
    for s in students:
        if s["name"]==stu_name:

            print("Name:", s["name"])
            print("Subject:", s["subject"])
            print("Batch:", s["batch"])
            print("Fees Paid:", s["fees_paid"])
            print("Fees Pending:", s["total_fees"] - s["fees_paid"])
            print("Attendance:", s["attendance"], "%")
            print("---------------------------------")
get_status()
