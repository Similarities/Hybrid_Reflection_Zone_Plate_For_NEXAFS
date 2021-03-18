import numpy as np
import Basic_file_app
import matplotlib.pyplot as plt



class FWHM:
    def __init__(self, file,path, energy_list):
        self.file = file
        self.path = path
        self.file_name = self.file[:-4]
        self.spectrum = self.open_file()
        self.energy_list = energy_list
        self.result = np.empty([1,4])
        self.range_for_selection = 0.013


    def open_file(self):
        spectral = Basic_file_app.load_1d_array(self.path + '/' + self.file, 0, 4)
        counts = Basic_file_app.load_1d_array(self.path + '/' + self.file, 2, 4)
        return Basic_file_app.stack_arrays(spectral, counts, 1)


    def find_max(self, array):
        return np.amax(array[:,1])

    def spectral_selection(self, selection_energy):
        index = np.where(self.spectrum[:,0] <= selection_energy)[0][0]
        index_L = np.where(self.spectrum[:,0] <= selection_energy + self.range_for_selection)[0][0]
        index_R = np.where(self.spectrum[:,0] <= selection_energy - self.range_for_selection)[0][0]
        print(index_L, index_R, "index selected energy: ", selection_energy,)
        return self.spectrum[index_L:index_R,:]

    def find_FWHM(self, array, max_counts):

        zero_line  = 0
        half_max = (max_counts - zero_line) / 2
            # gives for one peak stepfunction
            # width of step function is FWHM
        d = np.where(array[:, 1]-half_max >= 0)[0][0]
        indexL = d
        indexR = np.where(array[indexL:, 1] -half_max <= 0)[0][0] + indexL
        print(indexR)
        plt.figure(3)
        plt.plot(array[:,0], array[:,1])
        plt.hlines(y = array[indexL,1], xmin = array[0,0], xmax = array[-1,0])
        #print(indexR, indexL, len(array), 'indexR, indexL, len', len(d))
        print(array[indexR,1], array[indexL,1],max_counts, 'max counts')
       # print(array[indexR,:]- array[indexL,:])
        #plt.figure(2)
        #plt.plot(array[:,0], d)
        FWHM = array[indexR,0]- array[indexL,0]
        return FWHM

    def determine_full_width_half_max(self, selection_energy):
        self.result[0,0] = selection_energy
        sub_array = self.spectral_selection(selection_energy)
        self.result[0,1] = self.find_max(sub_array)
        self.result[0,2] = self.find_FWHM( sub_array, self.result[0,1])
        self.result[0,3] = selection_energy/self.result[0,2]
        return self.result

    def batch_over_energy_list(self):
        for x in self.energy_list:
            self.result = np.concatenate((self.result, self.determine_full_width_half_max(x)), axis = 0)

        plt.figure(1)
        plt.scatter(self.result[:,0], self.result[:,3], label= str(self.result[:,0]) + " nm")
        plt.xlabel("nm")
        plt.ylabel("Delta lambda/ lambda")
        plt.legend()
       # print(self.result)
        return self.result

    def prepare_header(self):
        # insert header line and change index
        header_names = (['lambda nm', 'max_counts/s', 'delta lambda FWHM', "lambda/delta_lambda"])
        names = (['file:' + str(self.filename), '##########', '########'])
        parameter_info = (
            ['description:', "FWHM determination", "no fit just max_counts/2"])
        return np.vstack((parameter_info, names, header_names, self.result))

    def save_data(self):
        result = self.prepare_header()
        print('...saving:', self.filename[:-4])
        plt.figure(1)
        plt.savefig(self.filename[:-4] + "_resolution" + ".png", bbox_inches="tight", dpi=500)
        np.savetxt(self.filename[:-4] + '_resolution' + ".txt", result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')







path = "data/210315_LT13730_Lrot71results0318/"
file = "210315_PM052004_calibrated_analytical.txt"
lambda_list = ( 1.50, 1.419, 1.675)#, 1.41,1.49, 1.675)


Test = FWHM(file, path, lambda_list)
Test.batch_over_energy_list()
plt.show()


