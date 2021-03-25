import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import math
import plot_filter
import os


# make sure the image-array (picture, background) is in 32bit
class ImagePreProcessing:

    def __init__(self, picture, picture_name, background, background_name, roi_list):
        self.filename = picture_name
        self.picture = picture
        self.background = background
        self.background_name = background_name
        # x1, y1, x2, y2
        self.back_roi = ([1245, 1884, 2048, 1902])
        self.binned_roi_y = np.empty([])
        self.x_axis_eV = np.empty([])
        self.x_axis_nm = np.empty([])
        self.roi_list = roi_list

    def reference_scaling(self):
        # opens tif is flipped vertical, array_image[y:y1, x:x1] (warum auch immer....)
        subarray_reference = self.background[self.back_roi[1]:self.back_roi[3], self.back_roi[0]:self.back_roi[2]]
        subarray_picture = self.picture[self.back_roi[1]:self.back_roi[3], self.back_roi[0]:self.back_roi[2]]
        mean_background_reference_x = np.mean(subarray_reference, axis=0)
        mean_background_picture_x = np.mean(subarray_picture, axis=0)
        scaling_factor = np.mean(mean_background_picture_x / mean_background_reference_x)
        print("scalingfactor", scaling_factor)
        self.background[::] = self.background[::] * scaling_factor
        return self.background

    def background_subtraction(self):
        for counter, x in enumerate(self.picture[0, ::]):
            self.picture[::, counter] = self.picture[::, counter] - self.background[::, counter]
        self.picture[self.picture < 0] = 0
        return self.picture

    def bin_in_y(self):
        self.binned_roi_y = np.sum(self.picture[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]],
                                   axis=0)
        self.x_axis_nm = np.arange(0, self.roi_list[2] - self.roi_list[0]).astype(np.float32)
        plt.figure(3)
        plt.imshow(self.picture[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        plt.colorbar()
        return self.binned_roi_y, self.x_axis_eV

    def calibrate_analytical(self, rzp_parameter):
        print("input:")
        print("pixel size in mm: ", rzp_parameter[0])
        print("alpha in degree: ", rzp_parameter[1])
        print("grating constant in nm", rzp_parameter[2])
        print("beta in degree: ", rzp_parameter[3])
        print("distance RZP detector in mm: ", rzp_parameter[4])
        print("offset in px for design energy : ", rzp_parameter[5])

        self.x_axis_nm[:] = rzp_parameter[0] * (self.x_axis_nm[:] + rzp_parameter[-1])
        for counter, value in enumerate(self.x_axis_nm):
            # simplified equation
            self.x_axis_nm[counter] = rzp_parameter[2] * (math.cos(rzp_parameter[1] * math.pi / 180)
                                                          - math.cos(
                        math.atan(self.x_axis_nm[counter] / rzp_parameter[4])
                        - (rzp_parameter[3] * math.pi / 180)))
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
        plt.figure(7)
        plt.plot(self.x_axis_eV, self.binned_roi_y, label=self.filename[:-4], marker=".", ms=3)
        plt.xlabel('eV')
        plt.ylabel('counts')
        plt.legend()
        return self.x_axis_eV

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

    def scale_array_per_second(self, constant):
        self.binned_roi_y = basic_file_app.constant_array_scaling(self.binned_roi_y, constant)
        return self.binned_roi_y

    def prepare_header(self, description1, description2):
        # insert header line and change index
        result = np.column_stack((self.x_axis_nm, self.x_axis_eV, self.binned_roi_y))
        self.spectral_range()
        header_names = (['nm', 'eV', 'counts/s'])
        names = (['file' + str(self.filename), 'back:' + str(self.background_name), 'roi list:' + str(self.roi_list)])
        parameter_info = (
            ['description:', description1, description2])
        return np.vstack((parameter_info, names, header_names, result))

    def save_data(self, description1, description2):

        result = self.prepare_header(description1, description2)
        print('...saving:', self.filename[:-4])
        plt.figure(7)
        plt.savefig(self.filename[:-4] + ".png", bbox_inches="tight", dpi=500)
        np.savetxt(self.filename[:-4] + '_calibrated_analytical' + ".txt", result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

    def view_control(self):
        plt.figure(1)
        plt.imshow(self.picture)
        plt.hlines(self.back_roi[1], xmax=2048, xmin=0)
        plt.hlines(self.back_roi[-1], xmax=2048, xmin=0)
        plt.vlines(self.back_roi[0], ymax=2048, ymin=0)
        plt.vlines(self.back_roi[2], ymax=2048, ymin=0)

    def figure_raw(self):
        plt.figure(8)
        plt.imshow(self.picture)
        plt.colorbar()


path_background = "data/StrayLight_W_4x945ms_5s/"
name_background = path_background
path_picture = "data/S1_W_4x945ms_5s/test/"
laser_gate_time_data = 45  # ms

# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 222, 2048, 1401])

emission_lines = basic_file_app.load_1d_array("calibration_files/Fe_XPL_detected_20210202.txt", 1, 3)

# px size in um, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
rzp_structure_parameter = np.array([1.350e-02,  2.130e+00 , 4.150e+03,  3.659e+00 , 2.575e+03, -1.470e+02])
laser_gate_time_data = 4 * 945  # ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZPA9-S1_" + str(laser_gate_time_data) + "ms"

# create input pictures

file_list_background = basic_image_app.get_file_list(path_background)
batch_background = basic_image_app.ImageStackMeanValue(file_list_background, path_background)
my_background = batch_background.average_stack()

my_y_limit = .3E7

def batch_folder_in_single_picture():
    my_pictures = basic_image_app.get_file_list(path_picture)
    print(my_pictures)
    for x in my_pictures:
        open_picture = basic_image_app.SingleImageOpen(x, path_picture)
        my_picture = open_picture.return_single_image()
        Test = ImagePreProcessing(my_picture, x, my_background, name_background[:-4], roi_list)
        # Test.view_control()
        Test.reference_scaling()
        Test.background_subtraction()
        Test.bin_in_y()
        Test.scale_array_per_second(per_second_correction)
        Test.calibrate_analytical(rzp_structure_parameter)
        Test.plot_x_axis_nm()
        # Test.plot_calibration(background[:, 0])
        Test.plot_result_ev()
        Test.plot_calibration_ev(emission_lines[:], my_y_limit, "b")
        my_filter_1 = plot_filter.PlotFilter("Mylar_900nm.txt", "filter/Mylar_filter", "eV", 7)
        my_filter_1.convert_nm_to_electron_volt()
        my_filter_1.plot_filter_data(my_y_limit)
        my_filter_2 = plot_filter.PlotFilter("Al_0.5um.txt", "filter/Al_0.5_filter", "eV", 7)
        my_filter_2.convert_nm_to_electron_volt()
        my_filter_2.plot_filter_data(my_y_limit)
        plt.xlim(150, 450)
        plt.ylim(0, my_y_limit)
        Test.save_data(str(rzp_structure_parameter), rzp_structure_name)


batch_folder_in_single_picture()

plt.show()
