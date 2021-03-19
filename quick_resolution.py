import numpy as np
import basic_file_app
import matplotlib.pyplot as plt


class FWHM:
    def __init__(self, file, path, energy_list):
        self.file = file
        self.path = path
        self.file_name = self.file[:-4]
        self.spectrum = self.open_file()
        self.energy_list = energy_list
        self.result = np.empty([1, 5])
        self.range_for_selection = 0.009
        self.all_results = np.zeros([1, 5])

    def open_file(self):
        spectral = basic_file_app.load_1d_array(self.path + '/' + self.file, 0, 4)
        counts = basic_file_app.load_1d_array(self.path + '/' + self.file, 2, 4)
        return basic_file_app.stack_arrays(spectral, counts, 1)

    def plot_fulls_spectra(self):
        plt.figure(3)
        plt.plot(self.spectrum[:, 0], self.spectrum[:, 1])
        plt.xlabel("nm")
        plt.ylabel("counts/s")
        plt.legend()

    def find_max(self, array):
        return np.amax(array[:, 1])

    def spectral_selection(self, selection_energy):
        index = np.where(self.spectrum[:, 0] <= selection_energy)[0][0]
        index_L = np.where(self.spectrum[:, 0] <= selection_energy + self.range_for_selection)[0][0]
        index_R = np.where(self.spectrum[:, 0] <= selection_energy - self.range_for_selection)[0][0]
        print(index_L, index_R, "index selected energy: ", selection_energy, )
        return self.spectrum[index_L:index_R, :]

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
        print(indexR_lower, indexR_upper, indexL_lower, indexL_upper,
              "indexR_lower, indexR_upper, indexL_lower, indexL_upper")
        print(array[indexR_lower, 1] / max_counts, array[indexR_upper, 1] / max_counts,
              array[indexL_lower, 1] / max_counts, array[indexL_upper, 1] / max_counts, "correspoding counts/maxcounts")
        print(max_counts, "max counts")
        plt.figure(3)
        plt.plot(array[:, 0], array[:, 1], marker=".")
        plt.hlines(y=array[indexL_lower, 1], xmin=array[0, 0], xmax=array[-1, 0], color="g")
        plt.hlines(y=array[indexL_upper, 1], xmin=array[0, 0], xmax=array[-1, 0], color="r")
        FWHM = array[indexL_lower, 0] - array[indexR_lower, 0]
        FWHM_upper = array[indexL_upper, 0] - array[indexR_upper, 0]
        return FWHM, FWHM_upper

    def determine_full_width_half_max(self, selection_energy):
        self.result[0, 0] = selection_energy
        sub_array = self.spectral_selection(selection_energy)
        self.result[0, 1] = self.find_max(sub_array)
        fwhm_low, fwhm_up = self.find_FWHM(sub_array, self.result[0, 1])
        self.result[0, 2] = fwhm_low
        self.result[0, 3] = fwhm_up
        avg = (fwhm_low + fwhm_up) / 2
        self.result[0, 4] = selection_energy / avg

        return self.result

    def batch_over_energy_list(self):
        for x in self.energy_list:
            self.all_results = np.concatenate((self.all_results, self.determine_full_width_half_max(x)), axis=0)

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
        ['lambda nm', 'max_counts/s', 'delta lambda FWHM low', 'delta_lambda FWHM up', "lambda/delta_lambda(avg)"])
        names = (
        ['file:' + str(self.file_name), '##########', '########', 'taken fwhm from existing points not fitted ',
         '......'])
        parameter_info = (
            ['description:', "FWHM determination", "no fit just max_counts/2",
             "taken at for next point over and under the half-max counts", 'xxxxx'])
        return np.vstack((parameter_info, names, header_names, self.all_results))

    def save_data(self):
        result = self.prepare_header()
        print('...saving:', self.file_name)
        np.savetxt(self.file_name + '_resolution' + ".txt", result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')


path = "data/"

lambda_list = (1.50, 1.526, 1.226, 1.21, 1.419, 1.675, 1.7, 1.38)



file_list = basic_file_app.get_file_list(path)

for x in file_list:

    Test = FWHM(x, path, lambda_list)
    Test.plot_fulls_spectra()
    Test.batch_over_energy_list()
    Test.save_data()

plt.figure(1)
plt.savefig("FWHM_210205_PM012548_calibrated_analytical" + ".png", bbox_inches="tight", dpi=500)
plt.show()
