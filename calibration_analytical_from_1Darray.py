import basic_file_app
import numpy as np
import matplotlib.pyplot as plt
import math
import os




class CalibrateArray:
    # calibration parameter is a list: px size, alpha, dgrating, beta, detector x-offset
    def __init__(self, calibration_parameter, result_directory):
        self.binned_roi_y = []
        self.filename = str()
        self.x_axis_nm = []
        self.calibration_parameter = calibration_parameter
        self.result_directory = result_directory
        print("input:")
        print("pixel size in mm: ", self.calibration_parameter[0])
        print("alpha in degree: ", self.calibration_parameter[1])
        print("grating constant in nm", self.calibration_parameter[2])
        print("beta in degree: ", self.calibration_parameter[3])
        print("distance RZP detector in mm: ", self.calibration_parameter[4])
        print("offset in px for design energy : ", self.calibration_parameter[5])

    def set_input_array(self, array, filename, inverse):
        #Todo reverse array by switch
        print(self.filename)
        self.filename = filename[:-4]
        self.binned_roi_y = array
        if inverse == True: self.reverse_array()
        self.create_px_x_axis(len(self.binned_roi_y))
        return self.filename, self.binned_roi_y, self.x_axis_nm


    def create_px_x_axis(self, length_array):
        self.x_axis_nm = np.linspace(length_array, 0, length_array)

    def reverse_array(self):
        self.binned_roi_y =self.binned_roi_y[::-1]
        return self.binned_roi_y

    def change_calibration_parameter (self, calibration):
        self.calibration_parameter = calibration
        self.filename = self.filename + str(self.calibration_parameter[3]) + "beta"
        self.create_px_x_axis(len(self.x_axis_nm))

    def main(self):
        self.calibrate_analytical()
        self.convert_array_nm_to_eV()
        self.plot_result_ev()
        self.save_data("calibrationfile:", self.calibration_parameter)
        result = self.stack_y_x_in_eV()
        return result

    def stack_y_x_in_eV(self):
        result = np.column_stack((self.x_axis_eV, self.binned_roi_y))
        return result


    def calibrate_analytical(self):
        # !!! self.x_axis_nm is as input px-x-axis....
        # returns in nm
        self.x_axis_nm[:] = self.calibration_parameter[0] * (self.x_axis_nm[:] + self.calibration_parameter[-1])
        for counter, value in enumerate(self.x_axis_nm):
            # simplified equation
            self.x_axis_nm[counter] = self.calibration_parameter[2] * (
                    math.cos(self.calibration_parameter[1] * math.pi / 180)
                    - math.cos(
                math.atan(self.x_axis_nm[counter] / self.calibration_parameter[4])
                - (self.calibration_parameter[3] * math.pi / 180)))
        return self.x_axis_nm

    def plot_x_axis_nm(self):
        plt.figure(6)
        plt.plot(self.x_axis_nm, self.binned_roi_y, label=self.filename[:-4] + "analytical", marker=".")
        plt.xlabel("nm")
        plt.ylabel("counts")
        plt.legend()

    def plot_calibration_nm(self, lines):
        for x in lines:
            plt.figure(6)
            plt.vlines(x, ymin=0, ymax=1E7)

    def plot_calibration_ev(self, lines, ymax, color):
        for x in lines:
            x = self.convert_single_value_nm_to_electron_volt(x)
            plt.figure(7)
            plt.vlines(x, ymin=0, ymax=ymax, linewidth=0.5, color=color)

    def plot_result_ev(self):
        self.convert_array_nm_to_eV()
        plt.title("result of calibration in eV")
        plt.figure(2)
        plt.plot(self.x_axis_eV, self.binned_roi_y, label=self.calibration_parameter[3], marker=".", ms=3)
        plt.xlabel('eV')
        plt.ylabel('counts')
        plt.legend()

    def convert_single_value_nm_to_electron_volt(self, value_nm):
        planck_constant = 4.135667516 * 1E-15
        c = 299792458
        return planck_constant * c / (value_nm * 1E-9)

    def convert_array_nm_to_eV(self):
        self.x_axis_eV = np.zeros([len(self.x_axis_nm)])
        self.x_axis_eV[:] = self.convert_single_value_nm_to_electron_volt(self.x_axis_nm[:])
        return self.x_axis_eV

    def spectral_range(self):
        print(np.amax(self.x_axis_nm), np.amin(self.x_axis_nm), 'spectral range in nm')

    # description 1 (e.g. file_background), description2: Roi-list for binned y
    def prepare_header(self, description1, description2):
        # insert header line and change index
        result = np.column_stack((self.x_axis_nm, self.x_axis_eV, self.binned_roi_y))
        header_names = (['nm', 'eV', 'counts/s'])
        names = (['file' + str(self.filename), str(description1), 'roi list:' + str(description2)])
        print(description1, description1, names)
        parameter_info = (
            ['description:', "px_shifted, calibration parameter:", str(self.calibration_parameter)])

        return np.vstack((parameter_info, names, header_names, result))

    def save_data(self, description1, description2):

        result = self.prepare_header(description1, description2)
        print('...saving:', self.filename[:-4])
        plt.figure(7)
        plt.xlim(520, 570)
        save_name = os.path.join(self.result_directory, self.filename[:-4] + "cal" + ".txt")
        # save_pic = os.path.join(self.directory, self.filename[:-4] +"_pxshifted_cal"+ ".png")
        # plt.savefig(save_pic, bbox_inches="tight", dpi=500)
        np.savetxt(save_name, result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

        plt.close()
