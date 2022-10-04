import basic_file_app
import numpy as np
import matplotlib.pyplot as plt
from depreciated_methods import sandwich_target
import os

path = "data/sandwich/data_sandwichprobe.txt"


class OpenRebinPlot:
    def __init__(self, file):
        self.file_name = file

    def open_file(self):
        my_ar = basic_file_app.load_2d_array(self.file_name, 2, 3, 0)
        # my_ar = np.transpose(my_ar)
        print(my_ar)
        return my_ar

    def plot_it(self, array, name):
        plt.figure(1, figsize=(10, 5))

        plt.plot(array[:-1, 0], array[:-1, 1], label=name)
        plt.xlabel("eV")
        plt.ylabel("i.a.u.")
        plt.yscale("log")
        # plt.xscale("log")
        plt.ylim(1E-1, 2)
        plt.xlim(350, 650)
        plt.legend()

    def add_filter(self, path_filter, scaling):
        sandwich30nm = sandwich_target.BatchFilter(path_filter, scaling)
        sandwich30nm.plot_resulting_transmission()

    def rescale_spectrum_fit(self, array, fits):
        for counter, value in enumerate(array[:, 0]):
            array[counter, 0] = fits[-1] + fits[-2] * value + fits[-3] * value ** 2 + fits[0] * value ** 3
        return array

    def insert_resolution(self, array, x1, x2):
        indexR = np.where(array[:, 0] <= x1)[0][0]
        indexL = np.where(array[:, 0] <= x2)[0][0]
        print(indexR, indexL)
        subarray = array[indexL:indexR,:2]


        plt.figure(2)
        plt.plot(subarray[:,0], subarray[:,1])


        max = np.amax(subarray[:, 1])
        min = np.amin(subarray[:, 1])

        max_delta_y = max-min
        max_70 = 0.7*max_delta_y + min
        max_30 = 0.3 * max_delta_y + min

        ten_pc = np.where(subarray[:, 1] <= max_30)[0][0]
        ninty_pc = np.where(subarray[:, 1] >= max_70)[0][0]
        plt.figure(2)
        #plt.hlines (1.3*min, xmin=np.amin(subarray[:,0]), xmax=np.amax(subarray[:,0]))
        #plt.hlines (0.70*max, xmin=np.amin(subarray[:,0]), xmax=np.amax(subarray[:,0]))
        plt.hlines (subarray[ninty_pc,1], xmin=np.amin(subarray[:,0]), xmax=np.amax(subarray[:,0]), label = "70%", color = "m")
        plt.hlines (subarray[ten_pc,1], xmin=np.amin(subarray[:,0]), xmax=np.amax(subarray[:,0]), label = "30%", color = "c")
        plt.ylabel("Transmission")
        plt.xlabel("energy in eV")

        delta = subarray[ten_pc,0]-subarray[ninty_pc,0]
        energy = subarray[ninty_pc,0]-delta
        print('resolution', energy/delta, delta)


        print(max, min, subarray[ninty_pc], subarray[ten_pc])
        plt.legend()
        plt.savefig("Sandwich_detail_452eV", bbox_inches="tight", dpi=500)



    def process(self, fits):
        array = self.open_file()
        # self.plot_it(array, 'anke')
        array = self.rescale_spectrum_fit(array, fits)
        self.plot_it(array, 'fitted')
        self.insert_resolution(array, 449, 457)
        np.savetxt("sandwich_spectrum" + ".txt", array, fmt='%.3E', delimiter='\t')


poly_fit = ([7.41635912e-07, 2.15965971e-04, 2.06832951e-01, 2.47610490e+02])

Test = OpenRebinPlot(path)
Test.process(poly_fit)
Test.add_filter("filter/sandwich_mix2/", 5)
plt.savefig("Sandwich", bbox_inches="tight", dpi=500)

plt.show()
