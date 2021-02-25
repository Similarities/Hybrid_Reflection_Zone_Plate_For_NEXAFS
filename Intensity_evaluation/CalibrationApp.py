import matplotlib.pyplot as plt
import numpy as np
import Basic_file_app
import Linear_Interpolation


class Prepare_Files_and_Interpolate:
    def __init__(self, original_file, binsize, file_name):
        self.file = original_file
        self.binsize = binsize
        self.initial_array = self.prepare_file(2)
        self.file_name = file_name
        self.result = self.linear_interpolation()

    def prepare_file(self, skip_row):
        # ToDo: test if not empty, otherwise raise error
        array_x = Basic_file_app.load_1d_array(self.file, 0, skip_row)
        array_y = Basic_file_app.load_1d_array(self.file, 1, skip_row)
        return Basic_file_app.stack_arrays(array_x, array_y, 1)

    def linear_interpolation(self):
        interpolation = Linear_Interpolation.LinearInterpolation(self.binsize, self.initial_array, self.file_name)
        self.result = interpolation.interpolate_array()
        new_file_name = interpolation.save_result()
        return new_file_name

    def plot_result(self):
        plt.plot(self.initial_array[::, 0], self.initial_array[::, 1], label=self.file_name + ' initial', color="b",
                 marker='.', ms=20)
        plt.plot(self.result[::, 0], self.result[::, 1], label=self.file_name + ' interpolated', color='r', marker=".",
                 ms=1, alpha=0.2)
        plt.legend()


my_quantum_efficiency = "QE_greateyesGE_BI.txt"
Test_files = Prepare_Files_and_Interpolate(my_quantum_efficiency, 0.01, my_quantum_efficiency[:-4])
my_quantum_efficiency = Test_files.linear_interpolation()
Test_files.plot_result()

number_of_electrons_per_photon = "electrons_per_photon.txt"
Test_files = Prepare_Files_and_Interpolate(number_of_electrons_per_photon, 0.01, number_of_electrons_per_photon[:-4])
number_of_electrons_per_photon = Test_files.linear_interpolation()
plt.figure(2)
Test_files.plot_result()

plt.show()


class CalibrateSingleValue:
    def __init__(self, photon_energy, counts):
        self.photon_energy = photon_energy
        self.counts = counts
        self.sensitivity = 0.8  # counts per electron
        self.calibration_photon_number = np.empty([])
        self.quantum_efficiency = np.empty([])

    def change_energy(self, photon_energy, counts):
        self.photon_energy = photon_energy
        self.counts = counts
        return self.photon_energy, self.counts

    def prepare_calibration_files(self, electron_calibration_file, quantum_efficiency_calibration_file):
        calibration_energy = Basic_file_app.load_1d_array(electron_calibration_file, 0, 0)
        calibration_electrons_per_photon_energy = Basic_file_app.load_1d_array(electron_calibration_file, 1, 0)
        self.calibration_photon_number = Basic_file_app.stack_arrays(calibration_energy,  #
                                                                     calibration_electrons_per_photon_energy, axis=1)

        calibration_energy = Basic_file_app.load_1d_array(quantum_efficiency_calibration_file, 0, 0)
        calibration_quantum = Basic_file_app.load_1d_array(quantum_efficiency_calibration_file, 1, 0)
        self.quantum_efficiency = Basic_file_app.stack_arrays(calibration_energy, calibration_quantum, axis = 1)

        return self.calibration_photon_number, self.quantum_efficiency



    def number_of_electrons(self):
        return self.counts / self.sensitivity

    def number_of_photons(self, photon_energy, counts):
        for counter, x in enumerate(self.calibration_photon_number[:, 0]):
            if x >= photon_energy:
                return counts / self.calibration_photon_number[counter, 1]

            else:
                print("! Warning, energy range not in calibration file")
                return None

# hmmm? whats better here... to make the value an argument of the function, or to make an object out of it... hmmm

# ToDo: sort by initial energy (or by value) then: calc with sensitivity for value calibration value
# ToDo: implement filter - do the same with filter
# ToDo: implement capture angle / per s for measurement
# ToDo: join it.
