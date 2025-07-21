
names = input("Names: ").split(', ')									# AA, BA, CA
num_of_assignments = [int(n) for n in input("Numbers: ").split(', ')]   # 10, 8, 6
grades = [int(n) for n in input("Grades: ").split(', ')]				# 70, 80, 90

for student_name, num_of_assignments, curr_grade in zip(
	names, num_of_assignments, grades
	):

	potential_grade = 2 * num_of_assignments + curr_grade
	msg = f"""
	Hi {student_name},

	This is a reminder that you have {num_of_assignments} 
	assignments left to submit before you can graduate. 
	Your current grade is {curr_grade} and 
	can increase to {potential_grade} if you submit 
	all assignments before the due date.
	"""
	print(msg)