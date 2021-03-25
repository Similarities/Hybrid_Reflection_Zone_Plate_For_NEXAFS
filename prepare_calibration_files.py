import matplotlib.pyplot as plt
import numpy as np
import basic_file_app
import linear_interpolation
import Linear_fit

class Prepare_Files_and_Interpolate:
    def __init__(self, original_file, binsize, file_name):
        self.file = original_file
        self.binsize = binsize
        self.initial_array = self.prepare_file(2)
        self.file_name = file_name
        self.result = np.empty([])

    def prepare_file(self, skip_row):
        # ToDo: test if not empty, otherwise raise error
        array_x = basic_file_app.load_1d_array(self.file, 1, skip_row)
        array_y = basic_file_app.load_1d_array(self.file, 0, skip_row)
        return basic_file_app.stack_arrays(array_x, array_y, 1)

    def linear_interpolation(self):
        interpolation = linear_interpolation.LinearInterpolation(self.binsize, self.initial_array, self.file_name)
        self.result = interpolation.interpolate_array()
        new_file_name = interpolation.save_result()
        return new_file_name

    def fit_linear(self,  order):
        my_fit = Linear_fit.CalibrationFit(self.initial_array, 1, self.file_name)
        my_fit.fit_refernce_points()
        my_fit.compare_fit()



    def convert_nm_to_electron_volt(self, unit):
        if unit:
            planck_constant = 4.135667516 * 1E-15
            c = 299792458
            self.initial_array[:, 0] = planck_constant * c / (self.initial_array[:, 0] * 1E-9)
            plt.figure(2)
            plt.plot(self.initial_array[:,0], self.initial_array[:,1])
            plt.show()
            print(self.initial_array[-1,0],self.initial_array[-2,0])
            return self.initial_array

        else:
            None

    def plot_result(self):
        plt.plot(self.initial_array[::, 0], self.initial_array[::, 1], label=self.file_name + ' initial', color="b",
                 marker='.', ms=20)
        plt.plot(self.result[::, 0], self.result[::, 1], label=self.file_name + ' interpolated', color='r', marker=".",
                 ms=1, alpha=0.2)
        plt.legend()




#my_quantum_efficiency = "QE_greateyesGE_BI.txt"
#Test_files = Prepare_Files_and_Interpolate(my_quantum_efficiency, 0.01, my_quantum_efficiency[:-4])
#my_quantum_efficiency = Test_files.linear_interpolation()
#Test_files.plot_result()

number_of_electrons_per_photon = "electrons_per_photon.txt"
Test_files = Prepare_Files_and_Interpolate(number_of_electrons_per_photon, 0.01, number_of_electrons_per_photon[:-4])
number_of_electrons_per_photon = Test_files.fit_linear(2)
#plt.figure(2)
#Test_files.plot_result()

#my_al_filter =  "Al_500nm_eV.txt"
#Test_files = Prepare_Files_and_Interpolate(my_al_filter, 0.05, my_al_filter[:-4])
#al_filter = Test_files.linear_interpolation()
#lt.figure(1)
#Test_files.plot_result()

#my_mylar_filter = "Mylar_900nm_eV.txt"
#Test_files = Prepare_Files_and_Interpolate(my_mylar_filter, 0.05, my_mylar_filter[:-4])
#mylar_filter = Test_files.linear_interpolation()
#plt.figure(1)
#Test_files.plot_result()

plt.show()