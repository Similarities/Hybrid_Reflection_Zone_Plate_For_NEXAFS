import matplotlib.pyplot as plt
import numpy as np
import basic_file_app
import px_shift_on_picture_array_rolling
import os
import calibration_analytical_from_1Darray
import poly_fit






def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else:
        os.mkdir(name)

def fit_my_data(reference_in, result_folder, spectrum_in , filename):
    my_fit = poly_fit.CalibrationFit(reference_points=reference_in , order =  2, directory = result_folder)
    my_fit.fit_refernce_points()
    my_fit.compare_fit()
    #plt.show()
    my_fit.calibrate_input_array(np.linspace(0, len(spectrum_in), len(spectrum_in)), spectrum_in, "Fe_S3_30ms", filename)




path_1 = "data/Result_Cu_10ms_S4FFTshifted_on_StackBdark/AvgBCu_S4_10ms.txt"
cal_directory = "Cu_10ms_S4_avg_shifted"
create_result_directory(cal_directory)

name1 = "Cu_10ms_S4_avg_shifted"
array_1 = basic_file_app.load_1d_array(path_1, 0, 1)



my_od1 = array_1

" calibrate first set of data:"
calibration_file = "calibration_files/Cu_linesXX_gruppe3_for_fit.txt"
lines = basic_file_app.load_1d_array("calibration_files/Cu_linesXX_gruppe3_for_fit.txt", 1, 2)


calibration= basic_file_app.load_2d_array(calibration_file, 1,2, 2)




" calibrate first set of data:"
reference = basic_file_app.load_2d_array(calibration_file, 1,2, 2)

file_name = "Cu_S4_cal"

fit_my_data(reference, cal_directory, array_1, file_name)

my_eV = basic_file_app.load_2d_array(cal_directory +"/"+file_name + ".txt", 0,2,4 )
my_nm = basic_file_app.load_2d_array(cal_directory + "/"+ file_name + ".txt", 1,2, 4)

plt.figure(1)
plt.plot(my_nm[:,0], my_nm[:,1], label = "Cu_S4_ 1 shot pointing corrected")
for x in lines:
    plt.vlines(ymin = 0, ymax = np.amax(my_nm[:,1]), x=x)

plt.xlabel("nm")
plt.ylabel("counts/s avg")
plt.legend()







plt.show()