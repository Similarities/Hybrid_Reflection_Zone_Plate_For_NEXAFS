import numpy as np
import basic_file_app
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


my_array = np.zeros([2048,3])
my_array1 = np.zeros([2048,3])



def something(something_arg):
    print(something_arg)









'poly fit means y(x) = x0 + C1 * x + C2 * x**2, where ** is the power of notation'
' one part of the excercise is - to google or find out how the coefficients are ordered '
' poly_coefficients = [x0, C1, C2] or = [C2, C1, x0] chances are 50/50 :) '

a = (400, 4) # input (x1,y2)
b = (1500, 90) # input (x2,y2)
poly_coefficients =  np.polyfit(a, b, 2)
print(poly_coefficients)

my_array_px = np.linspace(0,2048, 2048)
my_array_nm = np.linspace(0,2048, 2048)

for counter, value in enumerate (my_array_nm):
    my_array_nm[counter] = poly_coefficients[0] + value * poly_coefficients[1] + (value ** 2) * poly_coefficients[2]




plt.figure(1)
plt.plot(my_array_px[:], my_array_nm [:], label = "fit function px to nm")
plt.vlines(ymin = 0 , ymax= 3E8, x= 400, label = "first data point", color = "r")
plt.vlines(ymin = 0 , ymax= 3E8, x= 1500, label = "second data point", color = "r")
plt.xlabel("px")
plt.ylabel("nm")
plt.legend()
plt.show()




