import basic_file_app
import numpy as np
import matplotlib.pyplot as plt


# averages over stack (columnwise)
class AvgOnStack1Column:
    def __init__(self, path, constant):
        self.path = path
        self.scaling = constant
        self.file_list = self.create_file_list()
        self.avg = np.zeros([self.size_of_input_data()])
        self.std = np.zeros([len(self.avg)])

    def create_file_list(self):
        return basic_file_app.get_file_list(self.path)

    def open_single_file(self, file_name):
        return basic_file_app.load_1d_array(self.path + '/' + file_name, 4, 4)

    def size_of_input_data(self):
        return len(basic_file_app.load_1d_array(self.path + '/' + self.file_list[0], 4, 4))

    def integrate_over_stack(self):
        for x in self.file_list:
            print(self.file_list)
            single_file_data = self.open_single_file(x)
            single_file_data = self.constant_scaling_on_array(single_file_data)
            self.avg[:] = self.avg[:] + single_file_data[:]

        self.avg = self.avg[:]/len(self.file_list)
        return self.avg

    def constant_scaling_on_array(self, array):
        #print('!! array scaled of about: ', self.scaling)
        return array[:] * self.scaling

    def standard_deviation(self):
        for counter, value in enumerate(self.file_list):
            single_file_data = self.open_single_file(value)
            single_file_data = self.constant_scaling_on_array(single_file_data)
            self.std[:] =  self.std[:] + (single_file_data[:] ** 2) - (self.avg[:] ** 2)
        self.std[:] = (self.std[:]/len(self.file_list)) ** 0.5
        return self.std





my_path = "data/A9_Lrot31_105ms_LT19250LG_1300LT19250/FWHM_wo_px_shift/"
test = AvgOnStack1Column(my_path,1.)
my_avg = test.integrate_over_stack()
my_x = basic_file_app.load_1d_array( my_path + '/' +'210315_PM050607_calibrated_analytical_resolution.txt', 0,4)
my_error = test.standard_deviation()

#plt.scatter(my_x[:], my_avg[:])
plt.errorbar(my_x[:], my_avg[:], yerr=my_error, fmt="o", label = "avg_std Lrot31_105ms_LT19250LG_1300 ")


plt.figure(2)
plt.scatter(my_x, my_error/my_avg, label = "deviation decimal")
plt.legend()

plt.show()

