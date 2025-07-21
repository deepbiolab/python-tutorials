import print_info
# print(print_info.__name__) # print_info != '__main__'


name = input("Enter your name: ")
how_many_snakes = int(input("How many snakes to print: "))

print_info.print_snake(name, how_many_snakes)
