import matplotlib.pyplot as plt
import Basic_Image_App


class PlotFilter:
    def __init__(self, filename, path, unit, figure_number):
        self.filename = filename
        self.path = path
        self.unit = unit
        self.figure_number = figure_number
        self.filter_data = self.load_data()

    def load_data(self):
        x = Basic_Image_App.load_1d_array(self.path + '/' + self.filename, 0, 2)
        y = Basic_Image_App.load_1d_array(self.path + '/' + self.filename, 1, 2)
        return Basic_Image_App.stack_arrays(x, y, 0)

    def convert_nm_to_electron_volt(self):
        if self.unit == "eV":
            planck_constant = 4.135667516 * 1E-15
            c = 299792458
            self.filter_data[:, 0] = planck_constant * c / (self.filter_data[:, 0] * 1E-9)
            return self.filter_data

        else:
            None

    def plot_filter_data(self, y_scale):
        plt.figure(self.figure_number)
        plt.plot(self.filter_data[:,0], self.filter_data[:,1] * y_scale, label=self.filename[:-4])
        plt.xlabel(self.unit)
        plt.ylabel('i.a.')
        plt.legend()
        return self.x_axis
