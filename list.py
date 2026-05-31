#List -one variabl with multiple values
students=["mina","riya","priya","sneha","manu"]
print(students)
print(students[0]) #first element
print(students[1]) #second element
print(students[2]) #third element
print(students[3])
print(students[4])


#function
def greet(name):
    print(f"Hello, {name}!welcome to the world of Python programming.")
greet("mina")
greet("riya")
greet("priya")
greet("sneha")
greet("manu")   

for student in students:
    greet(student)