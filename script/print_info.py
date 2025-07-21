# module for print snake

def print_snake(name, how_many_snakes):
   snake_string = f"""
   Welcome to Python3!

               ____
               / . .|
               \  ---<
               \  /
      __________/ /
   -=:___________/

   :), {name}
   """

   print(snake_string * how_many_snakes)

if __name__ == "__main__":
   # test
   print(__name__)
   print_snake("tim", 1)