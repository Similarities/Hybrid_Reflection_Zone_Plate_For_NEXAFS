import numpy as np
import basic_file_app
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


class FWHM:
    def __init__(self, array, file_name, energy_list):
        self.file_name = file_name[:-4]
        self.spectrum = array
        self.energy_list = energy_list
        self.result = np.empty([1, 5])
        self.range_for_selection = 0.006
        self.all_results = np.zeros([1, 5])
        self.offset_const = 10000
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
        return np.amax(array[:, 1])

    def spectral_selection(self, selection_energy):
        index = np.where(self.spectrum[:, 0] <= selection_energy)[0][0]
        index_L = np.where(self.spectrum[:, 0] <= selection_energy + self.range_for_selection)[0][0]
        index_R = np.where(self.spectrum[:, 0] <= selection_energy - self.range_for_selection)[0][0]
        print(index_L, index_R, "index selected energy: ", selection_energy, )
        return self.spectrum[index_L:index_R, :]


    def substracte_baseline(self):
        self.spectrum[:,1] = self.spectrum[:,1] - self.offset_const
        return self.spectrum

    def interpolate_spectral_selection(self, selected_energy):
        subarray = self.spectral_selection(selected_energy)
        #linear interpolation
        f = interp1d(subarray[:,0],subarray[:,1])
        xnew = np.linspace(subarray[0,0], subarray[-1,0], num=150, endpoint= True)
        plt.figure(2)
        plt.plot(subarray[:,0],subarray[:,1], '.', xnew, f(xnew), '-')
        plt.xlim(1.22,1.2)
        plt.ylim(0,1.1E7)
        return np.stack((xnew, f(xnew)), axis = 1)



    def find_FWHM(self, array, max_counts):
        zero_line = 0
        half_max = (max_counts - zero_line) / 2
        # gives for one peak stepfunction
        # width of step function is FWHM
        d = np.where(array[:, 1] - half_max >= 0)[0][0]
        indexL_upper = d
        indexR_lower = np.where(array[indexL_upper:, 1] - half_max <= 0)[0][0] + indexL_upper
        indexL_lower = d - 1
        indexR_upper = indexR_lower + 1
        plt.figure(2)
        plt.scatter(array[:, 0], array[:, 1], marker=".", s=3, alpha = 0.5)
        plt.hlines(y=array[indexL_lower, 1], xmin=array[0, 0], xmax=array[-1, 0], color="g")
        plt.hlines(y=array[indexL_upper, 1], xmin=array[0, 0], xmax=array[-1, 0], color="r")
        FWHM = array[indexL_lower, 0] - array[indexR_lower, 0]
        FWHM_upper = array[indexL_upper, 0] - array[indexR_upper, 0]
        return FWHM, FWHM_upper


    def full_width_half_max_interpolated(self, selection_energy):
        self.result[0, 0] = selection_energy
        sub_array = self.interpolate_spectral_selection(selection_energy)
        self.result[0, 1] = self.find_max(sub_array)
        fwhm_low, fwhm_up = self.find_FWHM(sub_array, self.result[0, 1])
        self.result[0, 2] = fwhm_low
        self.result[0, 3] = fwhm_up
        avg = (fwhm_low + fwhm_up) / 2
        print(fwhm_up, fwhm_low, 0.5*(fwhm_up+fwhm_low), "fwhm up, fwhm low, fwhm avg")
        self.result[0, 4] = selection_energy / avg

        return self.result

    def batch_over_energy_list(self):
        for x in self.energy_list:
            self.all_results = np.concatenate((self.all_results, self.full_width_half_max_interpolated(x)), axis=0)

        self.all_results = self.all_results[1:, :]
        plt.figure(1)
        plt.scatter(self.all_results[:, 0], self.all_results[:, 4], label=self.file_name[9:14], alpha=0.9, s=10, marker="x")
        plt.xlabel("nm")
        plt.ylabel("Delta lambda/ lambda")
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


path = "data/A9_Lrot56_105ms_Gonio1460/LT18350/px_shifted_cal/px_cal/"


lambda_list = (1.50, 1.526, 1.226, 1.21, 1.419, 1.675, 1.705, 1.38)


file_list = basic_file_app.get_file_list(path)
avg_over_stack = basic_file_app.StackMeanValue(file_list, path, 0, 2, 4)
avg_array = avg_over_stack.get_result()

def open_file(file_name, path):
    spectral = basic_file_app.load_1d_array(path + '/' + file_name, 0, 4)
    counts = basic_file_app.load_1d_array(path + '/' + file_name, 2, 4)
    return basic_file_app.stack_arrays(spectral, counts, 1)


plt.figure(11)
plt.plot(avg_array[:,0], avg_array[:,1], label = "A9_Lrot56_105ms_Gonio1460LT18350_avg")
plt.legend()
for x in file_list:

    file = open_file(x, path)
    plt.figure(10)
    plt.plot(file[:,0], file[:,1])
    plt.xlim(1.4, 1.5)


testing = FWHM(avg_array, "A9_Lrot56_105ms_Gonio1460LT18350_avg_wo____", lambda_list)
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
plt.savefig("FWHM_A9_Lrot56_105ms_Gonio1460LT18350_px_shifted" + ".png", bbox_inches="tight", dpi=500)
plt.show()

