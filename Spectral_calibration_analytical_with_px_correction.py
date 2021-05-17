import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import math
import plot_filter
import px_shift_on_picture_array
import calibration_analytical_from_array
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
        return self.binned_roi_y, self.x_axis_nm

    def scale_array_per_second(self, constant):
        self.binned_roi_y = basic_file_app.constant_array_scaling(self.binned_roi_y, constant)
        return self.binned_roi_y

    def save_sum_of_y(self):
        result = np.stack((self.x_axis_nm, self.binned_roi_y), axis=1)

        np.savetxt(self.filename[:-4] + '_binned_y' + ".txt", result, delimiter=' ',
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


class PxCorrectionOnStack:
    def __init__(self, path, reference_point_list):
        self.path = path
        self.file_list = basic_image_app.get_file_list(path_picture)
        self.reference_points = reference_point_list
        self.pre_process_stack()

    def pre_process_stack(self):
        for x in self.file_list:
            open_picture = basic_image_app.SingleImageOpen(x, path_picture)
            my_picture = open_picture.return_single_image()
            PreProcess = ImagePreProcessing(my_picture, x, my_background, name_background[:-4], roi_list)
            # Test.view_control()
            PreProcess.reference_scaling()
            PreProcess.background_subtraction()
            PreProcess.bin_in_y()
            PreProcess.scale_array_per_second(per_second_correction)
            PreProcess.save_sum_of_y()
        print("xxxxxxxxx - all px shifted xxxxxxxxxxxx")

    def px_shift(self, path):
        self.file_list = basic_file_app.get_file_list(path)
        print(len(self.file_list))
        reference = basic_file_app.load_2d_array(self.file_list[0], 0, 1, 1)
        print("new file list", self.file_list)
        for x in self.file_list[1:]:
            image_array = basic_file_app.load_2d_array(x, 0, 1, 1)
            ShiftIt = px_shift_on_picture_array.PixelShift(reference, self.reference_points)
            corrected_array = ShiftIt.evaluate_shift_for_input_array(image_array)
            self.overwrite_original(x, corrected_array)

    def overwrite_original(self, file_name, array):
        print("overwriting original file..: ", file_name)
        np.savetxt(file_name[:-4] + ".txt", array, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')


class BatchCalibration:
    def __init__(self, calibration_file_path, file_path):
        self.calibration_parameter = basic_file_app.load_1d_array(calibration_file_path, 0, 0)
        print(self.calibration_parameter, 'used calibration_files')
        self.file_path = file_path

    def calibrate_array(self):
        self.file_list = basic_file_app.get_file_list(self.file_path)
        my_calibration = calibration_analytical_from_array.CalibrateArray(self.calibration_parameter)
        for x in self.file_list:
            my_array = basic_file_app.load_2d_array(self.file_path + x, 0, 1, 2)
            my_calibration.set_input_array(my_array, x)
            my_calibration.main()
            my_calibration.save_data("back: " + path_background + "RZP-structure:___" + rzp_structure_name, roi_list)




path_background = "data/stray_light/945ms_straylight/"
name_background = path_background
path_picture = "data/A9_Lrot56_105ms_Gonio1460/LT18350/raw/"

# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 380, 1730, 1670])

emission_lines = basic_file_app.load_1d_array("calibration_files/Fe_XPL_detected_20210202.txt", 1, 3)

# px size in um, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
# is now given via read in txt - should look like this:
#rzp_structure_parameter = np.array([1.350e-02, 2.130e+00, 1.338e+03, 3.714e+00, 2.479e+03, 0.000e+00])

laser_gate_time_data = 105  # ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZPA9-S3_" + str(laser_gate_time_data) + "ms"

# create input pictures

file_list_background = basic_image_app.get_file_list(path_background)
batch_background = basic_image_app.ImageStackMeanValue(file_list_background, path_background)
my_background = batch_background.average_stack()
my_y_limit = 3.3E7

# reference positions (px) for minimum in roi for px shift evaluation
reference_point_list = [949, 987]
# path_binned_array_files to be opened for px-shifted arrays (usually excecution path for this python routine)
# Test = PxCorrectionOnStack(path_picture, reference_point_list)
# Test.px_shift(path_binned_array_files)

binned_file_path = "data/A9_Lrot56_105ms_Gonio1460/LT18350/px_shifted_cal/binned/"
calibration_path = "data/A9_Lrot56_105ms_Gonio1460/LT18350/A9_Lrot56_105ms_Gonio1460_LT18350_cal.txt"
calibration = BatchCalibration(calibration_path, binned_file_path)
calibration.calibrate_array()

plt.show()
