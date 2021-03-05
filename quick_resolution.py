import numpy as np
import Basic_file_app
import matplotlib.pyplot as plt


path = "data/S3_Fe_per_s/"
file = "210205_PM012548_calibrated_analytical.txt"

array_x = Basic_file_app.load_1d_array(path + file, 0, 4)
array_y = Basic_file_app.load_1d_array(path+file, 2,4)



Basic_file_app.plot_range_of_array(array_x, array_y, 1.49, 1.51)
plt.ylim(1.385E7, 3.7E7)
plt.show()

#shot 1x745ms first one
print("_______________")
print(1.67288-1.67651)
print(1.6748/(1.67288-1.67651))
print("_______________")
print(1.41613-1.42056)
print(1.41825/(1.41613-1.42056))

print("_______________")
print(1.49742-1.50177)
print(1.49948/(1.49742-1.50177))
print("_______________")

#shot 1x45ms PM 014010

print("1.67535")
print(1.67355 - 1.67687)
print(1.67536/(1.67355-1.67687))
print("_______________")
print(1.41694-1.42087)
print(1.41911/(1.41694-1.42087))

print("_______________")
#main line
print(1.4979-1.50194)
print(1.5/(1.4979-1.50194))
print("_______________")
print("_______________")
#shot 1x45ms PM 014017
#main line
print(1.6744-1.67762)
print(1.67601/(1.6744-1.67762))
print("_______________")

print(1.42173-1.41778)
print(1.4198/(1.42173-1.41778))
print("_______________")
print(1.49887-1.50274)
print(1.50065/(1.49887-1.50274))
