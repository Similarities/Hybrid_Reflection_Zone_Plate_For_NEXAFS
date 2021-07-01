import basic_file_app
import numpy as np
import matplotlib.pyplot as plt
import os


# averages over stack (columnwise)
class AvgOnStack1Column:
    def __init__(self, path, constant, column):
        self.path = path
        self.scaling = constant
        self.file_list = self.create_file_list()
        self.column = column
        self.x_axis = self.get_x_axis()
        self.avg = np.zeros([self.size_of_input_data()])
        self.std = np.zeros([len(self.avg)])

    def create_file_list(self):
        return basic_file_app.get_file_list(self.path)

    def open_single_file(self, file_name):
        return basic_file_app.load_1d_array(self.path + '/' + file_name, self.column, 6)

    def size_of_input_data(self):
        return len(basic_file_app.load_1d_array(self.path + '/' + self.file_list[0], self.column, 6))

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

    def get_x_axis(self):
        return basic_file_app.load_1d_array(self.path+ '/' +self.file_list[0], self.column-1, 6 )

    def save_statistics(self, new_dir, file_name):
        result = np.column_stack((self.x_axis, self.avg, self.std))
        print(result)
        header = (["eV", "counts avg", "std"])
        header2 = (["mi", "xxx", str(self.path)])
        print(header)
        result = np.vstack((header, header2, result))
        save_name = os.path.join(new_dir, file_name + 'avg' + ".txt")
        np.savetxt(save_name , result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')







my_path = "results_cal_5000ms_pos2/"
avg_path = "results_avg"

result_file_name = "20210628_5000ms_pos2_avg"
#os.mkdir(avg_path)
my_files = basic_file_app.get_file_list(my_path)
#class(path, scale, column) -> skiprows in the code
test = AvgOnStack1Column(my_path,1.,2)
my_avg = test.integrate_over_stack()
#create x-axis from one of the files (path+name, column, skip-rows)
my_x = basic_file_app.load_1d_array( my_path + '/' +my_files[0], 1,6)
my_error = test.standard_deviation()
test.save_statistics(avg_path, result_file_name)

#plt.scatter(my_x[:], my_avg[:])
plt.figure(1)
plt.errorbar(my_x[:], my_avg[:], yerr=my_error, fmt="o", label = result_file_name)
plt.xlim(520,550)
plt.legend()

save_name = os.path.join(avg_path, result_file_name + ".png")
plt.savefig(save_name, bbox_inches="tight", dpi=500)


#plt.figure(2)
#plt.scatter(my_x, my_error/my_avg, label = "deviation decimal")
#plt.legend()

plt.show()

