import Basic_File_App
import numpy as np
import matplotlib as plt


class AvgOnStack:
    def __init__(self, path, constant):
        self.path = path
        self.scaling = constant
        self.file_list = self.create_file_list()
        self.avg = np.zeros([self.size_of_input_data()])
        self.std = np.zeros([len(self.avg)])

    def create_file_list(self):
        return Basic_File_App.get_file_list(self.path)

    def open_single_file(self, file_name):
        return Basic_File_App.load_1d_array(self.path + '/' + file_name, 1, 2)

    def size_of_input_data(self):
        return len(Basic_File_App.load_1d_array(self.path + '/' + self.file_list[0], 1, 2))

    def integrate_over_stack(self):
        for counter, value in enumerate(self.file_list):
            single_file_data = self.open_single_file(value)
            single_file_data = self.constant_scaling_on_array(single_file_data, self.scaling)
            self.avg[:] = self.avg[:] + single_file_data[:]

        self.avg[:]/len(self.file_list)
        return self.avg

    def constant_scaling_on_array(self, array):
        print('!! array scaled of about: ', self.scaling)
        return array[:] * self.scaling

    def standard_deviation(self):
        for counter, value in enumerate(self.file_list):
            single_file_data = self.open_single_file(value)
            single_file_data = self.constant_scaling_on_array(single_file_data)
            self.std[:] =  self.std[:] + (single_file_data[:] ** 2) - (self.avg[:] ** 2)
        self.std[:] = (self.std[:]/len(self.file_list)) ** 0.5
        return self.std





