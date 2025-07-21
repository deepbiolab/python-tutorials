x = 1
if x > 0:
    print("Positive")
    
def func():
	print("Hello")  # 没有缩进

func()

value = 1    
print(value)


result = 'Age: ' + '18'

num = int("123")

lst = [1, 2, 3]
print(lst[2])

d = {'a': 1}
print(d['a'])

lst = [1, 2, 3]
# lst.upper()

n = 2
eps = 1e-9
x = 10 / (n + eps)
print(x)

import numpy

# n = 1
# try:
# 	x = 10 / n # 易出错的语句
# 	result = 'Age: ' + n # 易出错的语句
# except ZeroDivisionError:
# 	print(f"Error for division: {n}")
# else:
# 	x *= 2
# 	print(f"==> {x}")
# finally:
# 	print(f"-> {n}")

# n = 0
# try:
# 	result = 'Age: ' + n # 易出错的语句
# except TypeError:
# 	print("Cannot add int to str")

# try:
# 	x = 10 / n # 易出错的语句
# except ZeroDivisionError:
# 	print(f"Error for division: {n}")


# n = int(input("Number: "))
# try:
# 	x = 10 / n # 易出错的语句
# 	result = 'Age: ' + n # 易出错的语句
# except (ZeroDivisionError, TypeError) as e:
# 	print(f"Error for division or type error: {n}")
# 	print(e)

# n = 0
# try:
# 	x = 10 / n # 易出错的语句
# except ZeroDivisionError as e:
# 	print(f"Error for division: {n}")
# 	print(e)


n = int(input("Number: "))
try:
	x = 10 / n # 易出错的语句
	result = 'Age: ' + n # 易出错的语句
except Exception as e:
	print(e)