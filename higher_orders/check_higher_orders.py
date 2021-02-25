import matplotlib.pyplot as plt
import numpy as np
import Basic_File_App
import plotFilter


class ScaleAndOverlaySpectra:
    def __init__(self ):
        self.array_1 = np.empty([])
        self.array_2 = np.empty([])
        self.array_any = np.empty([])
        self.name_original = str()
        self.name_higher_order = str()
        self.counter_order = int


    def load_array(self, filename, path, scale_x, scale_y):
        array_x = Basic_File_App.load_1d_array(path + '/' + filename, 0, 5 )
        array_y = Basic_File_App.load_1d_array(path + '/'+ filename, 2,5)
        array_x = Basic_File_App.constant_array_scaling(array_x, scale_x)
        array_y = Basic_File_App.constant_array_scaling(array_y, scale_y)
        return Basic_File_App.stack_arrays(array_x, array_y, 1)

    def load_original(self, filename, path):
        self.array_1 = self.load_array(filename, path, 1, 1)
        self.name_original = str(path[-2:]) + "original"
        return self.array_1, self.name_original


    def load_second_order(self, filename, path, scale_y):
        self.array_2 = self.load_array(filename, path, 2, scale_y)
        self.counter_order = 2
        self.name_higher_order = str(path) + 'order:' +str(self.counter_order)
        return self.array_2, self.name_higher_order

    def load_any_oder(self, filename, path, order, scale_y):
        self.array_any = self.load_array(filename, path, order, scale_y)
        self.counter_order = order
        print(self.counter_order)
        self.name_higher_order = str(path) +'order:' +str(self.counter_order)
        self.add_single_array_to_plot()





    def add_single_array_to_plot(self):
        plt.figure(1)
        plt.plot(self.array_any[:,0], self.array_any[:,1], label = self.name_higher_order )
        plt.legend()

    def plot_both(self):
        plt.figure(1)
        plt.plot(self.array_1[:,0], self.array_1[:,1], label = self.name_original )
        plt.plot(self.array_2[:,0], self.array_2[:,1], label = self.name_higher_order, alpha = 0.5)
        plt.xlabel("nm")
        plt.xlim(6, 3)
        plt.legend()

    def save_plot(self, description1, description2):
        plt.figure(1)
        plt.savefig(description1 + '_' + description2 + ".png", bbox_inches="tight", dpi=500)


my_first = ScaleAndOverlaySpectra()
my_first.load_original("210205_PM023351_calibrated_analytical.txt", "higher_order_FE/S1")
my_first.load_second_order("210205_PM012930_calibrated_analytical.txt", "higher_order_FE/S3", 0.1)
my_first.plot_both()
my_first.load_any_oder("210205_PM012930_calibrated_analytical.txt", "higher_order_FE/S3", 3, 0.2)
my_first.load_any_oder("210205_PM012930_calibrated_analytical.txt", "higher_order_FE/S3", 4, 0.2)

my_first.save_plot("S1", "S3")



plt.show()