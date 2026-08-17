#Write python code using normal loop, list comprehension and using numpy package for the following questions.  Observed the techniques used, which is the easiest technique? 
# Given  A and B, perform calculation for A-B  
# A = [[-1, 0], [0, 1]]
# B = [[-1, 2], [3, -2]]
import numpy as np

arr_a = np.array([[-1, 0], [0, 1]])
arr_b = np.array([[-1, 2], [3, -2]], dtype=int)
result_np = arr_a - arr_b
print("NumPy:\n", result_np)
# b) Create a 3x3 matrix which comprise of the following values.  Multiply the matrix with 10.  
# A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
