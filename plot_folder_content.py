import matplotlib.pyplot as plt
import basic_file_app


def plot_them_all(path, column_x, column_y, skip_rows):
    file_list = basic_file_app.get_file_list(path)
    for x in file_list:
        array = basic_file_app.load_2d_array(path + '/' + x, column_x, column_y, skip_rows )
        name = x[:-13]
        scale = array[272, 1]
        print(array[272,1])
        if scale >0:
            array[:,1] = array[:,1]-scale
        else:
            array[:,1] = array[:,1]+(abs(scale))

        print(array[262,1])
        plt.figure(1)
        plt.plot(array[:,0], array[:,1], label = name)
        plt.xlabel("eV")
        plt.ylabel("-log(signal) - const")
        plt.legend()


    plt.show()

plt.ylim(-1, 2.5)
plt.xlim(520, 550)
plot_them_all("results_avg",0, 1, 6 )

