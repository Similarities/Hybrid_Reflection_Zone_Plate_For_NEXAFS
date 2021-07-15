import matplotlib.pyplot as plt
import basic_file_app
import numpy as np


def plot_them_all(path, column_x, column_y, skip_rows):
    file_list = basic_file_app.get_file_list(path)
    for x in file_list[7:13]:
        array = basic_file_app.load_2d_array(path + '/' + x, column_x, column_y, skip_rows )

        plt.figure(1)
        plt.plot(array[:,0], -np.log(array[:,1])+14, marker=".", markersize = 3)
        plt.xlabel("eV")
        plt.ylabel("-log(signal) - const")
        plt.legend()


    plt.show()

#plt.ylim(-1, 2.5)
plt.xlim(840, 890)
plot_them_all("cal__LT3250_50ms",1,2, 6 )

