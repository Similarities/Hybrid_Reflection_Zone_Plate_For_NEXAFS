import numpy as np
import matplotlib.pyplot as plt



class calibration_fit:
    def __init__(self, reference_points):
        self.reference_points = reference_points
        #print(reference_points)
        self.poly_coefficients = self.fit_refernce_points()
        self.poly_reciproce = self.fit_reciproce()
        #print(self.poly_coefficients, 'coefficients')

    def fit_refernce_points(self):
        return np.polyfit(self.reference_points[:, 1], self.reference_points[:, 0], 2)

    def fit_reciproce(self):
        return np.polyfit(self.reference_points[:, 0], self.reference_points[:, 1], 2)

    def give_fit(self):
        return self.poly_coefficients

    def compare_fit(self):
        x_axis = np.linspace(np.min(self.reference_points[:, 1]), np.max(self.reference_points[:, 1]), 400)
        fit_y = np.linspace(np.min(self.reference_points[:, 1]), np.max(self.reference_points[:, 1]), 400)
        for counter, value in enumerate(x_axis):
            fit_y[counter] = self.poly_coefficients[-1] + self.poly_coefficients[1] * x_axis[counter] + \
                             self.poly_coefficients[0] * x_axis[counter] ** 2

        plt.figure(1)
        plt.scatter(self.reference_points[:, 1], self.reference_points[:, 0])
        plt.plot(x_axis, fit_y)
        plt.plot()
