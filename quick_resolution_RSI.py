import numpy as np
import basic_file_app
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from lmfit.models import GaussianModel
import math





class FWHM:
    def __init__(self, array, file_name, energy_list):
        self.file_name = file_name
        self.spectrum = array
        self.energy_list = energy_list
        self.result = np.empty([1, 5])
        self.range_for_selection = 0.005
        self.all_results = np.zeros([1, 5])
        self.offset_const = 0
        self.sigma_temp = 0
        self.amplitude_temp = 0
        self.center_temp = 0
        print(self.offset_const, 'base line offset')

    def plot_fulls_spectra(self):
        plt.figure(3)
        plt.plot(self.spectrum[:, 0], self.spectrum[:, 1])
        plt.xlabel("nm")
        plt.ylabel("counts/s")
        plt.legend()

    def offset(self):
        plt.figure(4)
        plt.plot(self.spectrum[:100,0], self.spectrum[:100,1])
        return np.mean(self.spectrum[:20,1])

    def find_max(self, array):
        print("np.amax")
        return np.amax(array[:, 1])

    def spectral_selection(self, selection_energy):

        index_L = np.where(self.spectrum[:, 0] >= selection_energy - self.range_for_selection)[0][0]
        mid = np.where(self.spectrum[:,0]>=selection_energy)[0][0]
        print(mid, index_L, "mid and index L")

        print(index_L, 2*(mid-index_L), "index selected energy: ", selection_energy, )
        return self.spectrum[index_L:int(index_L+2*(mid-index_L)), :]


    def substracte_baseline(self):
        self.spectrum[:,1] = self.spectrum[:,1] - self.offset_const
        return self.spectrum

    def interpolate_spectral_selection(self, selected_energy):

        subarray = self.spectral_selection(selected_energy)
        #linear interpolation
        plt.figure(2)
        plt.plot(subarray[:,0],subarray[:,1], marker = ".")
        #plt.xlim(1.22,1.2)
        #plt.ylim(0,1.1E7)

        return subarray

    def fit_gaussian(self, array, figure_number):
        mod = GaussianModel()
        pars = mod.guess(array[:,1], x=array[:,0])
        out = mod.fit(array[:,1], pars, x=array[:,0])
        self.sigma_temp = out.params['sigma'].value
        self.amplitude_temp = out.params['amplitude'].value
        self.center_temp = out.params['center'].value
        self.plot_fit_function(array[:,0], figure_number)
        return self.sigma_temp, self.amplitude_temp, self.center_temp

    def plot_fit_function(self, array_x, figure_number):
        # IMPORTANT sigma  corresponds to w(0) beamwaist = half beam aperture
        yy = np.zeros([len(array_x), 1])
        for counter, value in enumerate(array_x):
            a = (self.amplitude_temp / (self.sigma_temp * ((2 * math.pi) ** 0.5)))
            b = -(array_x[counter] - self.center_temp) ** 2
            c = 2 * self.sigma_temp ** 2
            yy[counter] = (a * math.exp(b / c))

        plt.figure(figure_number)
        plt.plot(array_x, yy)

    def FWHM_from_sigma(self, sigma):
        return (2 * sigma * (2 * 0.69) ** 0.5)

    def full_width_half_max_interpolated(self, selection_energy):
        sub_array = self.interpolate_spectral_selection(selection_energy)
        self.result[0,0], self.result[0,1], self.result[0,2] = self.fit_gaussian(sub_array, 2)
        self.result[0,3] = self.result[0,2]/self.FWHM_from_sigma(self.result[0,0])
        print("FWHM", self.FWHM_from_sigma(self.result[0,0]))
        print("sigma", self.result[0,0])
        print("Amplitude", self.result[0,1])
        print("E in nm", self.result[0,2])
        print("DE/E", self.result[0,3])
        return self.result

    def batch_over_energy_list(self):
        for x in self.energy_list:
            self.all_results = np.concatenate((self.all_results, self.full_width_half_max_interpolated(x)), axis=0)

        self.all_results = self.all_results[1:, :]
        plt.figure(1)
        plt.scatter(self.all_results[:, 2], self.all_results[:, 3], label=self.file_name, alpha=0.9, s=10, marker="x")
        plt.xlabel("nm")
        plt.ylabel("lambda/Delta_Lamda")
        plt.legend()
        print(self.all_results)
        return self.all_results

    def prepare_header(self):
        # insert header line and change index
        header_names = (
        ['nm', 'max_counts/s', 'delta lambda FWHM low', 'delta_lambda FWHM up', "lambda/delta_lambda(avg)"])
        names = (
        ['file:' + str(self.file_name), '##########', '########', 'taken fwhm from existing points linear interpolated ',
         '......'])
        parameter_info = (
            ['description:', "FWHM determination", "max_counts/2",
             "taken at for next point over and under the half-max counts", 'xxxxx'])
        return np.vstack((parameter_info, names, header_names, self.all_results))

    def save_data(self):
        result = self.prepare_header()
        print('...saving:', self.file_name)
        np.savetxt(self.file_name + '_resolution' + ".txt", result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')


path = "data/20230315_Cu/Cu_50ms_S4_avg_shifted"
file_name = "Cu_S4_cal_50ms.txt"

lambda_list = (1.257, 1.283, 1.0594, 1.1383, 1.16, 0.927, 0.911 )





def open_file(file_name, path):
    spectral = basic_file_app.load_1d_array(path + '/' + file_name, 1, 4)
    counts = basic_file_app.load_1d_array(path + '/' + file_name, 2, 4)
    spectral= np.flip(spectral)
    counts = np.flip(counts)
    return basic_file_app.stack_arrays(spectral, counts, 1)

avg_array = open_file(file_name, path)

plt.figure(11)
plt.plot(avg_array[:,0], avg_array[:,1], label = file_name[:-4])
plt.legend()


testing = FWHM(avg_array, file_name[:-4], lambda_list)
testing.substracte_baseline()
testing.batch_over_energy_list()
testing.save_data()



#batch
#for x in file_list:
 #   array = open_file(path, x)
  #  name = x[:-4]
   # Test = FWHM(array, name, lambda_list)
    #Test.substracte_baseline()
    #Test.batch_over_energy_list()
    #Test.save_data()




plt.figure(1)
plt.savefig("FWHM_"+file_name[:-4] + ".png", bbox_inches="tight", dpi=500)
plt.show()

