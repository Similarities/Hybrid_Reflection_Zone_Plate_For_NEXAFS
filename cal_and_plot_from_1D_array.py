import matplotlib.pyplot as plt
import numpy as np
import basic_file_app
import px_shift_on_picture_array_rolling
import os
import calibration_analytical_from_1Darray



class PxShiftOnArrays:
    def __init__(self, avg_picture, avg_reference, reference_point, method, plot_number):
        self.avg_picture = avg_picture
        self.avg_reference = avg_reference
        self.reference_point = reference_point
        self.method = method
        self.plot_number = plot_number

    def set_new_arrays(self, array_picture, array_reference):
        self.avg_picture = array_picture
        self.avg_reference = array_reference
        return self.avg_reference, self.avg_picture

    def px_shift_both(self):
        evaluate_shift = px_shift_on_picture_array_rolling.PixelShift(self.avg_picture, self.reference_point,
                                                                      self.method)
        self.avg_reference, shift = evaluate_shift.evaluate_shift_for_input_array(self.avg_reference, self.plot_number)
        #plt.show()
        return self.avg_reference



    def x_binning(self, array_in):
        binned_spectra = np.zeros([int(round(len(array_in/2),0))+1])
        for counter, value in enumerate(array_in):
            if counter %2 == 0:
                binned_spectra[int(round(counter/2,0))] = array_in[counter-1]+array_in[counter]
        plt.figure(1111)
        plt.plot(binned_spectra)
        return binned_spectra

    def set_reference_point(self, reference):
        self.reference_point = reference
        return self.reference_point


def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else:
        os.mkdir(name)



path_1 = "Gruppe2 Result_stackAVG_B/Gruppe2 _binned_y.txt"
cal_directory = "Gruppe2_test"
create_result_directory(cal_directory)

name1 = "Gruppe2 Cu "
array_1 = basic_file_app.load_1d_array(path_1, 0, 1)



my_od1 = array_1

" calibrate first set of data:"
calibration_file = "calibration_files/20230215_calibration_parameter_S4.txt"
lines = basic_file_app.load_1d_array("calibration_files/Cu_linesXXI.txt", 1, 1)
lines2 = basic_file_app.load_1d_array("calibration_files/Cu_linesXX.txt", 1, 1)

calibration= basic_file_app.load_all_columns_from_file(calibration_file, 0)
my_calibration = calibration_analytical_from_1Darray.CalibrateArray(calibration, cal_directory)
my_calibration.set_input_array(my_od1, "test_spectrum", True)
my_calibration.main()
my_calibration.plot_x_axis_nm()
my_calibration.plot_calibration_nm(lines, "r")
my_calibration.plot_calibration_nm(lines2, "b")

# px size, alpha , d, beta, distance
a = 0.00
calibration[1]=calibration[1]+a
calibration[3] = calibration[3] +0.1
calibration[1] = calibration[1]*1.1
calibration[-1] = 0
my_calibration.change_calibration_parameter(calibration)
my_calibratedod1 = my_calibration.main()
my_calibration.save_data("Gruppe2_test", "see cal paramter here")



x_px = np.linspace(0,2048, 2048)
x_eV = np.linspace(0, 2048, 2048)
def convert_single_value_nm_to_electron_volt( value_nm):
    planck_constant = 4.135667516 * 1E-15
    c = 299792458
    return planck_constant * c / (value_nm * 1E-9)

def poly_fit():
    for counter, value in enumerate(x_px):
        x_eV[counter] = -5.63*1E-8 * (value**3)+1.95*1E-4 * (value**2) - (4.62*1E-1)*value +1.4*1E3

    return x_eV


reference_cu_xx =basic_file_app.load_1d_array("calibration_files/Cu_linesXX_gruppe1.txt",1,1)
reference_cu_xx[:] =  convert_single_value_nm_to_electron_volt(reference_cu_xx[:])
px_reference = basic_file_app.load_1d_array("calibration_files/Cu_linesXX_gruppe1.txt", 2,1)
px_reference[:] = 2048-px_reference[:]-350
print(reference_cu_xx, px_reference)





print(len(reference_cu_xx), len(px_reference))


plt.figure(10)
plt.plot(x_px, poly_fit(), label = "calibration Gruppe1")
plt.scatter(px_reference, reference_cu_xx)
plt.xlabel("px")
plt.ylabel("eV")
plt.legend()






plt.show()