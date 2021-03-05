import matplotlib.pyplot as plt
import numpy as np
import Basic_file_app


class CountsToPhotonNumber:
    def __init__(self, data, calibration_q_a, calibration_electron_per_photon):
        self.data = data
        self.sensitivity = 0.83 / 2.5  # counts per electron for low gain
        self.capture_angle = 4.72E-3  # sr for RZP A9
        self.calibration_photon_number, self.quantum_efficiency = \
            self.prepare_calibration_files(calibration_electron_per_photon, calibration_q_a)
        self.result = np.zeros([len(data), 2])

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
        self.quantum_efficiency = Basic_file_app.stack_arrays(calibration_energy, calibration_quantum, axis=1)

        return self.calibration_photon_number, self.quantum_efficiency

    def number_of_electrons(self, counts):
        return counts / self.sensitivity

    def correct_quantum_efficiency_ccd(self, photon_energy):
        for counter, x in enumerate(self.quantum_efficiency[:, 0]):
            #ToDo: solve via fit function -- does not work logically wrong
            if x <= photon_energy:
                return self.quantum_efficiency[counter, 1]

            else:
                print("! Warning, energy range not in calibration file:", photon_energy, "eV")
                return None

    def number_of_photons(self, photon_energy, electron_number):
        for counter, x in enumerate(self.calibration_photon_number[:, 0]):
            #ToDo: solve via np.where... is too slow
            if x >= round(photon_energy,2):
                quantum_efficiency = self.correct_quantum_efficiency_ccd(photon_energy)
                return electron_number * (self.calibration_photon_number[counter, 1] / quantum_efficiency)



    def number_of_photons_per_sr(self, number_of_photons):
        return number_of_photons / self.capture_angle

    def bandwidth_correction(self, energy_1, energy_2):
        delta_energy = energy_2 - energy_1
        print('bandwith:', delta_energy, "at:", energy_1)
        return delta_energy / 0.001

    def evaluate_data(self):
        for counter, value in enumerate(data[:-1, 0]):
            self.result[counter, 0] = value
            counts = data[counter, 1]
            electrons = self.number_of_electrons(counts)
            photons = self.number_of_photons(value, electrons)
            photons_per_sr = self.number_of_photons_per_sr(photons)
            self.result[counter, 1] = photons_per_sr / self.bandwidth_correction(value, data[counter + 1, 0])
        return self.result


data_file = "data_intensity/210205_PM012548_calibrated_analytical.txt"
data = Basic_file_app.stack_arrays(Basic_file_app.load_1d_array(data_file, 1, 4),
                                   Basic_file_app.load_1d_array(data_file, 2, 4), axis=1)

data_below_1000ev = data[0:1059]

calibration_number_e_per_photon = "electrons_per_photon_interpolation_bin_size_0.01.txt"
calibration_q_a = "QE_greateyesGE_BI_interpolation_bin_size_0.01.txt"


Test = CountsToPhotonNumber(data_below_1000ev, calibration_number_e_per_photon, calibration_q_a)
aha = Test.evaluate_data()


plt.plot(aha[:-1,0], aha[:-1,1])
plt.show()

# hmmm? whats better here... to make the value an argument of the function, or to make an object out of it... hmmm

# ToDo: sort by initial energy (or by value) then: calc with sensitivity for value calibration value
# ToDo: implement filter - do the same with filter
# ToDo: implement capture angle / per s for measurement
# ToDo: join it.
