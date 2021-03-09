import numpy as np
import matplotlib.pyplot as plt


class CalibrationFit:
    def __init__(self, reference_points, order, file_name):
        self.name = file_name
        self.reference_points = reference_points
        self.order = order
        # print(reference_points_x_y)
        self.poly_coefficients = self.fit_refernce_points()
        self.poly_reciproce = self.fit_reciproce()
        # print(self.poly_coefficients, 'coefficients')

    def fit_refernce_points(self):
        fit_parameter = np.polyfit(self.reference_points[:, 1], self.reference_points[:, 0], self.order)
        np.savetxt(self.name + "_poly_fit" + ".txt", fit_parameter, fmt='%.3E', delimiter='\t')
        return fit_parameter


    def fit_reciproce(self):
        return np.polyfit(self.reference_points[:, 0], self.reference_points[:, 1], self.order)

    def give_fit(self):
        return self.poly_coefficients


    def compare_fit(self):
        x_axis = np.linspace(np.min(self.reference_points[:, 1]), np.max(self.reference_points[:, 1]), 400)
        fit_y = np.linspace(np.min(self.reference_points[:, 1]), np.max(self.reference_points[:, 1]), 400)
        for counter, value in enumerate(x_axis):
            fit_y[counter] = self.poly_coefficients[-1] + self.poly_coefficients[0] * x_axis[counter]
        plt.figure(1)
        plt.scatter(self.reference_points[:, 1], self.reference_points[:, 0])
        plt.plot(x_axis, fit_y)
        plt.plot()
