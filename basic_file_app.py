import numpy as np
import matplotlib.pyplot as plt
import os


def load_1d_array(file, column_1, skiprows):
    data = np.loadtxt(file, skiprows=skiprows, usecols=(column_1,))
    return data


def load_1d_array_with_name(path, column_1, skip_rows, name):
    data_files = []
    counter = 0
    for file in os.listdir(path):
        print(file)
        try:
            if file.endswith(name + ".txt" or ".csv"):
                data_files.append(str(file))
                counter = counter + 1
            else:
                print("only other files found")
        except Exception as e:
            raise e
    data = np.loadtxt(data_files[0], skiprows=skip_rows, usecols=(column_1,))
    return data


def load_2d_array(file, column_1, column_2, skiprows):
    data_x = load_1d_array(file, column_1, skiprows)
    data_y = load_1d_array(file, column_2, skiprows)
    return stack_arrays(data_x, data_y, 1)


def stack_arrays(array_1, array_2, axis):
    return np.stack((array_1, array_2), axis=axis)


def constant_array_scaling(array, constant):
    return array[:] * constant


def get_file_list(path_txt):
    data_files = []
    counter = 0
    for file in os.listdir(path_txt):
        print(file)
        try:
            if file.endswith(".txt" or ".csv"):
                data_files.append(str(file))
                counter = counter + 1
            else:
                print("only other files found")
        except Exception as e:
            raise e
    return data_files


def plot_range_of_array(array_x, array_y, x_min, x_max):
    plt.plot(array_x, array_y)
    plt.xlim(x_min, x_max)


class StackMeanValue:

    def __init__(self, file_list, file_path, col_x, col_y, skip_rows):
        self.file_list = file_list
        self.file_path = file_path
        self.skip_rows = skip_rows
        self.col_y = col_y
        self.col_x = col_x
        self.result = np.zeros([self.length_input_array(), 2])
        self.average_stack()



    def length_input_array(self):
        return len(load_1d_array(self.file_path + '/' + self.file_list[0], 0, self.skip_rows))

    def average_stack(self):
        for x in self.file_list:
            x = str(self.file_path + '/' + x)
            single_array = load_1d_array(x, self.col_y, self.skip_rows)
            self.result[:, 1] = self.result[:, 1] + single_array

        self.result[:, 1] = self.result[:, 1] / (len(self.file_list))
        return self.result

    def get_result(self):
        self.result[:, 0] = load_1d_array(self.file_path + '/' + self.file_list[0], self.col_x, self.skip_rows)
        print(self.result)
        return self.result
