import numpy as np


class LinearInterpolation:
    def __init__(self, resulting_bin_size, array, file_name):
        self.resulting_bin_size = resulting_bin_size
        self.initial_array = array
        self.filename = file_name
        self.delta_x = float(0.)
        self.temporal_array = np.zeros([1, 2])
        self.sub_array = np.zeros([1, 2])
        self.last_entry = np.zeros([1, 2])
        self.bin_number = int(0)
        self.incremental_step = float(0)
        self.upper_bin = int(0)
        self.accuracy = int

    def find_digit(self):
        x = 0
        first_digit = self.resulting_bin_size
        if first_digit > 1:
            return None
        else:
            while first_digit < 1:
                first_digit = first_digit * 10
                x = x + 1
        return x

    def round_accuracy(self):
        for x in range(0, len(self.initial_array)):
            self.accuracy = self.find_digit()
            self.initial_array[x, 0] = round(self.initial_array[x, 0], self.accuracy)
        return self.initial_array

    def sub_arraying(self):
        # ratio = int, increment = float (bin size that should be reached),
        # excerpt= element  to be started (lower limit), 2D
        filling = np.zeros([self.bin_number, 2])
        x = self.upper_bin[0, ]
        v = self.upper_bin[1, ]
        for i in range(0, self.bin_number):
            filling[i, 0] = x + i * self.resulting_bin_size
            filling[i, 1] = v + i * self.incremental_step
        return filling

    def interpolate_element(self, counter):
        ratio = self.delta_x[0, ] / self.resulting_bin_size
        self.bin_number = int(round(ratio))
        self.incremental_step = self.delta_x[1, ] / ratio
        self.initial_array[counter + 1, 0] = (self.initial_array[counter, 0]
                                              + self.bin_number * self.resulting_bin_size)
        self.upper_bin = self.initial_array[counter]
        self.sub_array = self.sub_arraying()
        self.temporal_array = np.concatenate((self.sub_array, self.temporal_array))
        self.temporal_array.view('i8,i8').sort(order=['f0'], axis=0)

    def last_entry_array(self):
        counter_last_entry = -1
        self.last_entry[0, 0] = self.initial_array[counter_last_entry, 0]
        self.last_entry[0, 1] = self.initial_array[counter_last_entry, 1]
        self.delta_x = self.last_entry[0, ] - self.temporal_array[counter_last_entry, ]
        ratio = self.delta_x[0, ] / self.resulting_bin_size
        self.bin_number = int(round(ratio)) + 1
        self.incremental_step = self.delta_x[1, ] / ratio
        self.upper_bin = self.temporal_array[counter_last_entry, ]
        self.sub_array = self.sub_arraying()
        self.temporal_array = np.concatenate((self.sub_array, self.temporal_array))
        self.temporal_array.view('i8,i8').sort(order=['f0'], axis=0)
        self.temporal_array = np.delete(self.temporal_array, 0, axis=0)
        self.temporal_array = np.delete(self.temporal_array, -2, axis=0)
        return self.temporal_array

    def interpolate_array(self):
        self.round_accuracy()

        for counter, value in enumerate(self.initial_array[:-1, 0]):
            self.delta_x = self.initial_array[counter + 1] - self.initial_array[counter]
            if self.delta_x[0, ] > self.resulting_bin_size:
                self.interpolate_element(counter)

            elif self.delta_x > self.resulting_bin_size:
                print('!! wanted bin size > initial bin size !! ')
                return None

        self.last_entry_array()
        return self.temporal_array

    def save_result(self):
        np.savetxt(self.filename + "_interpolation_bin_size" + "_" + repr(self.resulting_bin_size) + ".txt",
                   self.temporal_array, fmt='%.3E', delimiter='\t')
        print("length of old array", len(self.initial_array))
        print("length of new array", len(self.temporal_array))
        return str(self.filename + "_interpolation_bin_size" + "_" + repr(self.resulting_bin_size) + ".txt")
