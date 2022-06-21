import numpy as np
import matplotlib.pyplot as plt

# reference point list: method evaluates minimum in +/- range, the px-position (in x) of minimum is needed

class PixelShift:
    def __init__(self, array_reference, reference_point_list, keyword):

        self.array_reference = array_reference
        self.reference_points = reference_point_list
        self.array_in = np.empty([])
        self.binned_reference = np.empty([])
        self.position_reference = int
        self.prepare_reference()
        self.max_min_logic = keyword

    def prepare_reference(self):
        self.position_reference = self.minimum_analysis(self.array_reference)
        return  self.position_reference

    def evaluate_shift_for_input_array(self, picture_array):
        self.array_in = picture_array
        self.test_plot(self.array_in, 1, "original")
        reference_position = self.max_min_decision()
        shift = self.shift_to_reference(reference_position)
        print(shift, '#####shift##########')
        print(reference_position, '#### reference ### ')
        corrected_array = self.correct_for_shift(shift, picture_array)
        self.test_plot(corrected_array, 2, "px-shifted")
        return corrected_array

    def max_min_decision(self):
        if self.max_min_logic == "min":
            minimum_position = self.minimum_analysis(self.array_in)
            #print("reference position minimum:")
            return minimum_position
        elif self.max_min_logic == "max":
            #print("reference position maximum:")
            maximum_position = self.maximum_analysis(self.array_in)
            return maximum_position


    def shift_to_reference(self, minimum_position):
        return self.position_reference - minimum_position

    def correct_for_shift(self, shift, array):
        corrected_array = np.zeros([len(self.array_reference), 2])
        corrected_array[:, 0] = self.array_reference[:, 0]
        if shift == 0:
            corrected_array[:, 1] = array[:, 1]

        elif shift < 0 & shift > -15:
            corrected_array[:shift,1] = array[-shift:,1]

        elif shift > 0 & shift < 15:
            corrected_array[shift:,1] = array[:-shift,1]
        return corrected_array


    def minimum_analysis(self, array):
        left = self.reference_points[0] - 20
        right = self.reference_points[0] +20
        sub_array = array[left:right, 1]
        minimum = np.amin(sub_array)
        #print(minimum)
        #print([idx for idx, val in enumerate(sub_array) if val == minimum] )
        shift_1 = [idx for idx, val in enumerate(sub_array) if val == minimum][0] + left
        return shift_1

    def maximum_analysis(self, array):
        left = self.reference_points[0] - 20
        right = self.reference_points[0] +20
        sub_array = array[left:right, 1]
        maximum = np.amax(sub_array)
        #print(maximum)
        #print([idx for idx, val in enumerate(sub_array) if val == maximum] )
        shift_1 = [idx for idx, val in enumerate(sub_array) if val == maximum][0] + left
        return shift_1

    def test_plot(self, array, figure_number, name):
        plt.figure(figure_number)
        plt.title(name)
        plt.plot(array[:, 0], array[:, 1])
        plt.xlim(self.reference_points[0] -60, self.reference_points[0] + 60)
