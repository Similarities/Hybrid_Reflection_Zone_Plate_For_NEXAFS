import matplotlib.pyplot as plt
import os
import calibration_analytical_from_1Darray
import basic_file_app
import numpy as np



def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else:
        os.mkdir(name)


def plot_nexafs(array1, array2, name, figure_number):
    my_od = -np.log((array1[:]) / (array2[:]))
    # np.savetxt(bin_path_image + "/ODD" + name_picture + name_reference + ".txt", my_od, delimiter=' ',
    #          header='string', comments='')
    plt.figure(figure_number)
    plt.title("AVG two stacks")
    plt.plot(my_od, label=name)
    plt.xlim(30,2000)
    #plt.ylim(0.1,0.3)
    plt.xlabel("px")
    plt.ylabel("Nexafs")
    plt.legend()
    #plt.ylim(-0.5, 0.5)
    print("max odd:", np.amax(my_od), "min odd:", np.amin(my_od))



result_folder = "20220823_cal"
create_result_directory(result_folder)


calibration_file = "calibration_files/202209_calibration_S2.txt"

calibration= basic_file_app.load_all_columns_from_file(calibration_file, 0)
my_calibration = calibration_analytical_from_1Darray.CalibrateArray(calibration, result_folder)


my_raw_file = "20220823_resultFFTPxshifted_on_StackBdark/AvgBTi_100ms_I.txt"
my_raw_array = basic_file_app.load_1d_array(my_raw_file, 0, 1)

my_calibration.set_input_array(my_raw_array, "AvgBTi_100ms_I.txt", True)
my_calibration.main()

calibration[3] = calibration[3] + 0.25
my_calibration.change_calibration_parameter(calibration)
my_calibration.main()



plt.show()