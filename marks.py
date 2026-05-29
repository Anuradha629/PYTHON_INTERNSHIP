sub1=int(input("Enter marks for Subject 1:"))
sub2=int(input("Enter marks for Subject 2:"))
sub3=int(input("Enter marks for Subject 3:"))
sub4=int(input("Enter marks for Subject 4:"))
sub5=int(input("Enter marks for Subject 5:"))

Total=sub1+sub2+sub3+sub4+sub5
percentage=Total/5
 
print("Total marks =",Total)
print(" Percentage =",percentage)

if percentage >= 75:
    print("Congratulations...you got Distinction")

elif  percentage >= 60:
    print("Congratulations...you got First class")

elif percentage >= 45:
     print("Congratulations...you passed")

else:
      print("You failed")

