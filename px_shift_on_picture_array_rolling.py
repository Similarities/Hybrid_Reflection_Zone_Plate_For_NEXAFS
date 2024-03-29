import numpy as np
import matplotlib.pyplot as plt
from scipy import fftpack
from scipy import signal


# reference point list: method evaluates minimum in +/- range, the px-position (in x) of minimum is needed

class PixelShift:
    def __init__(self, array_reference, reference_point_list, keyword):

        self.array_reference = array_reference
        self.reference_points = reference_point_list
        self.array_in = np.empty([])
        self.binned_reference = np.empty([])
        self.position_reference = int
        self.shift = int
        self.prepare_reference()
        self.method = keyword

    def prepare_reference(self):
        self.position_reference = self.minimum_analysis(self.array_reference)
        return self.position_reference

    def evaluate_shift_for_input_array(self, picture_array, figure_number):
        self.array_in = picture_array
        self.test_plot(self.array_in, 1, "original")
        reference_position = self.max_min_decision()
        self.shift = self.shift_to_reference(reference_position)
        print(self.shift, '#####shift##########')
        print(reference_position, '#### Minimum  ### ', "### reference:", self.position_reference)
        corrected_array = self.correct_for_shift(picture_array)
        self.test_plot(corrected_array, figure_number, "px-shifted")
        return corrected_array, self.shift


    def evaluate_correct_shift_via_fft_for_input_array(self, picture_array, figure_number, range):
        self.array_in = picture_array
        self.test_plot(self.array_in, 1, "original")

        left = self.reference_points[0] - range
        right = self.reference_points[0] + range
        sub_array = picture_array[left:right]
        sub_array_reference = self.array_reference[left:right]
        a = fftpack.fft(sub_array)
        b = fftpack.fft(sub_array_reference)
        b = -b.conjugate()
        self.shift = len(sub_array) - np.argmax(np.abs(fftpack.ifft(a * b)))
        if np.argmax(np.abs(fftpack.ifft(a * b))) < range:
            self.shift = -1 * np.argmax(np.abs(fftpack.ifft(a * b)))
            if self.shift<0:
                self.shift = self.shift

        elif self.shift > range:
            self.shift = 0
        elif self.shift < -range:
            self.shift = 0
        else:
            self.shift = self.shift

        print(self.shift, "shift from fft, ", np.argmax(np.abs(fftpack.ifft(a * b))))
        corrected_array = self.correct_for_shift(picture_array)
        self.test_plot(corrected_array, figure_number, "px-shifted")
        return corrected_array, self.shift

    def return_shift(self):
        print(self.shift)
        return self.shift

    def max_min_decision(self):
        if self.method == "min":
            minimum_position = self.minimum_analysis(self.array_in)
            # print("reference position minimum:")
            return minimum_position
        elif self.method== "max":
            # print("reference position maximum:")
            maximum_position = self.maximum_analysis(self.array_in)
            return maximum_position

    def shift_to_reference(self, minimum_position):
        return self.position_reference - minimum_position

    def correct_for_shift(self, array):
        corrected_array = np.zeros([len(self.array_reference), 1])

        if self.shift == 0:
            corrected_array = array

        elif self.shift < 0 & self.shift > -25:

            corrected_array = np.roll(array, self.shift)
        elif self.shift > 0 & self.shift < 25:
            corrected_array = np.roll(array, self.shift)

        return corrected_array

    def minimum_analysis(self, array):
        left = self.reference_points[0] - 15
        right = self.reference_points[0] + 15
        sub_array = array[left:right]
        minimum = np.amin(sub_array)
        # print(minimum, "minimum")
        # print(sub_array)
        # print([idx for idx, val in enumerate(sub_array) if val == minimum] )
        shift_1 = [idx for idx, val in enumerate(sub_array) if val == minimum][0] + left
        return shift_1

    def maximum_analysis(self, array):
        left = self.reference_points[0] - 15
        right = self.reference_points[0] + 15
        sub_array = array[left:right, 1]
        maximum = np.amax(sub_array)
        # print(maximum)
        # print([idx for idx, val in enumerate(sub_array) if val == maximum] )
        shift_1 = [idx for idx, val in enumerate(sub_array) if val == maximum][0] + left
        return shift_1

    def test_plot(self, array, figure_number, name):
        plt.figure(figure_number)
        plt.title(name)
        plt.plot(array, label=self.shift)
        # plt.legend()
        plt.xlim(self.reference_points[0] - 80, self.reference_points[0] + 80)

    def return_shift(self):
        return self.shift()
