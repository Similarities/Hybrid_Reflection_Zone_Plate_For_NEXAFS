import numpy as np
import matplotlib.pyplot as plt
import os


class CalibrationFit:
    def __init__(self, reference_points, order, directory):
        self.directory = directory
        self.reference_points = reference_points
        print(reference_points, 'reference points')
        self.order = order
        # print(reference_points_x_y)
        self.poly_coefficients = self.fit_refernce_points()
        print(self.poly_coefficients, 'coefficients')

    def fit_refernce_points(self):
        #use reciprocal if column 0 is px and column is eV
        fit_parameter = np.polyfit(self.reference_points[:, 1], self.reference_points[:, 0], self.order)
        np.savetxt("_poly_fit" + ".txt", fit_parameter, fmt='%.3E', delimiter='\t')
        return fit_parameter


    def fit_reciproce(self):
        self.poly_coefficients =  np.polyfit(self.reference_points[:, 0], self.reference_points[:, 1], self.order)
        print("reciprocal fit px = 1 nm = 2")
        np.savetxt("_poly_fit" + ".txt", self.poly_coefficients, fmt='%.3E', delimiter='\t')
        return self.poly_coefficients

    def give_fit(self):
        return self.poly_coefficients


    def compare_fit(self):
        x_axis = np.linspace(np.min(self.reference_points[:, 0]), np.max(self.reference_points[:, 0]), 400)
        fit_y = np.linspace(np.min(self.reference_points[:, 1]), np.max(self.reference_points[:, 1]), 400)
        for counter, value in enumerate(x_axis):
            fit_y[counter] = self.poly_coefficients[-1] + self.poly_coefficients[1] * x_axis[counter] + self.poly_coefficients[0]* (x_axis[counter] ** 2)
        plt.figure(55)
        plt.title("fit")
        plt.scatter(self.reference_points[:, 0], self.reference_points[:, 1])
        plt.ylabel("nm")
        plt.xlabel("px")
        plt.plot(x_axis, fit_y)
        plt.legend()
        plt.plot()

    def calibrate_input_array(self, array_in, file_array, description):
        array_in[:,0] = self.poly_coefficients[-1] + self.poly_coefficients[1] * array_in[:,0] + self.poly_coefficients[0]* (array_in[:,0] ** 2)
        array_eV = self.convert_single_value_nm_to_electron_volt(array_in[:,0])
        array_in = self.stack_column(array_eV, array_in)
        self.save_data(description, file_array, array_in)

    def convert_single_value_nm_to_electron_volt(self, value_nm):
        planck_constant = 4.135667516 * 1E-15
        c = 299792458
        return planck_constant * c / (value_nm * 1E-9)

    def stack_column(self, array_1D, array_2D):
        return np.column_stack((array_1D, array_2D[:,0], array_2D[:,1]))




    def prepare_header(self, description1, file_name, array_converted):
        # insert header line and change index
        header_names = (['eV', 'nm', 'counts/s'])
        names = (['converted file:' + str(file_name[:-4]), str(description1), "xxx "])
        #print(description1, description1, names)
        parameter_info = (
            ['description:' + description1, "px_shifted, calibration parameter: " + str(self.poly_coefficients), "xxx "])
        #print(np.ndim(header_names), np.ndim(parameter_info), np.ndim(array_converted))
        return np.vstack((parameter_info, names, header_names, array_converted))

    def save_data(self, description1, file_name, array_converted):

        result = self.prepare_header(description1, file_name, array_converted)
        print('...saving:', file_name[:-4])
        save_name = os.path.join(self.directory, file_name[:-4] + "cal" + ".txt")
        np.savetxt(save_name, result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')


