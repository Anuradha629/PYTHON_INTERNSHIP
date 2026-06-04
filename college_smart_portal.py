Students=  ["Mina","Riya","Siya","Priya","Manvi"]
marks=  [85,90,78,92,88]
attendance=[95,98,92,97,96]
Notice="""
  Students must Write Weekly diary
  Complete your Assignments on time
  Attend all the lectures"""

print("***** College Smart Portal *****")
def student_login():
  name=input("Enter your name:")
   
  for i in range(len(Students)):
         if Students[i]==name:
            print("Name:",name)
            print("Marks:",marks[i])     
            print("Attendance:",attendance[i],"%")
            print("Congratulations...Login successful!")
            print("         NOTICE BOARD       ")
            print(Notice)   
            return   
  print("Login unsuccessful. Please check your Name.")
student_login()