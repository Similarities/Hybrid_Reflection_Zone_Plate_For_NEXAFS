import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import math
from depreciated_methods import px_shift_on_picture_array, plot_filter
import poly_fit
import os


# make sure the image-array (picture, background) is in 32bit
class ImagePreProcessing:

    def __init__(self, picture, picture_name, background, background_name, roi_list, back_roi):
        self.filename = picture_name
        self.picture = picture
        self.background = background
        self.background_name = background_name
        # x1, y1, x2, y2
        self.back_roi = back_roi
        self.binned_roi_y = np.empty([])
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
        self.picture = basic_image_app.convert_32_bit(
            self.picture[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        self.background = (self.background[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        self.picture[:, :] = self.picture[:, :] - self.background[:, :]

        # self.picture[self.picture < 0] = 1
        return self.picture

    def bin_in_y(self):
        self.binned_roi_y = np.sum(self.picture,
                                   axis=0)
        # print(len(self.binned_roi_y), "len binned roi")
        self.x_axis = np.arange(0, self.roi_list[2] - self.roi_list[0]).astype(np.float32)
        return self.binned_roi_y, self.x_axis

    def scale_array_per_second(self, constant):
        self.binned_roi_y = basic_file_app.constant_array_scaling(self.binned_roi_y, constant)
        return self.binned_roi_y

    def reverse_array(self):
        self.binned_roi_y = self.binned_roi_y[::-1]
        return self.binned_roi_y

    def save_sum_of_y(self, new_dir):
        result = np.stack((self.x_axis, self.binned_roi_y), axis=1)
        save_name = os.path.join(new_dir, self.filename[:-4] + '_binned_y' + ".txt")
        self.plot_sum()
        np.savetxt(save_name, result, delimiter=' ',
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

    def plot_sum(self):
        plt.figure(111)
        plt.plot(self.x_axis, self.binned_roi_y, label="single image sum")
        plt.ylabel("counts")
        plt.xlabel("px")
        plt.legend()


class PxCorrectionOnStack:
    def __init__(self, path, reference_point_list, new_dir, key):
        self.path = path
        self.file_list = basic_image_app.get_file_list(path_picture)
        self.reference_points = reference_point_list
        self.new_dir = new_dir
        self.max_min_key = key

    # addon (in pre-processing)
    def threshold_cleaner(self, picture, threshold):
        picture[picture > threshold] = 0
        # plt.imshow(picture)
        # plt.show()
        return picture

    def pre_process_stack(self):
        print("file_list", self.file_list)
        for x in self.file_list:
            open_picture = basic_image_app.SingleImageOpen(x, path_picture)
            my_picture = open_picture.return_single_image()
            # my_picture = self.threshold_cleaner(my_picture, 65000)
            PreProcess = ImagePreProcessing(my_picture, x, my_background, name_background[:-4], roi_list, back_roi)
            # Test.view_control()
            # PreProcess.reference_scaling()
            PreProcess.background_subtraction()
            PreProcess.bin_in_y()
            PreProcess.scale_array_per_second(per_second_correction)
            # IMPORTANT: reverse array if high energy part is left
            PreProcess.reverse_array()
            PreProcess.save_sum_of_y(self.new_dir)
            # plt.close()
        print("xxxxxxxxx - all px shifted xxxxxxxxxxxx")

    def px_shift(self):
        self.file_list = basic_file_app.get_file_list(self.new_dir)
        print(len(self.file_list), "number of files to be processed")

        reference = basic_file_app.load_2d_array(self.new_dir + '/' + self.file_list[0], 0, 1, 1)
        # print("new file list", self.file_list)
        for x in self.file_list[1:]:
            image_array = basic_file_app.load_2d_array(self.new_dir + '/' + x, 0, 1, 1)
            ShiftIt = px_shift_on_picture_array.PixelShift(reference, self.reference_points, self.max_min_key)
            corrected_array = ShiftIt.evaluate_shift_for_input_array(image_array)
            self.overwrite_original(x, corrected_array)

    def overwrite_original(self, file_name, array):
        plt.figure(103)
        plt.plot(array[:, 0], array[:, 1])
        plt.title("px shifted stack")
        plt.ylabel("counts")
        plt.xlabel("px")
        plt.legend()
        print("overwriting original file..: ", file_name)
        save_name = os.path.join(self.new_dir, file_name[:-4] + ".txt")
        np.savetxt(save_name, array, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')


class BatchCalibration:
    def __init__(self, calibration_file, file_path, save_directory):
        print(calibration_file, "calibration file")
        print("folder where calibrated spectra is saved:", save_directory)
        self.test = basic_file_app.load_1d_array(calibration_file, 0, 2)
        self.calibration_parameter_px = basic_file_app.load_2d_array(calibration_file, 0, 1, 1)
        print(self.calibration_parameter_px, 'used calibration_file')
        self.file_path = file_path
        self.directory = save_directory
        self.order = 2

    def calibrate_array(self):
        self.file_list = basic_file_app.get_file_list(self.file_path)
        my_calibration = poly_fit.CalibrationFit(self.calibration_parameter_px, self.order, self.directory)
        my_calibration.fit_reciproce()
        my_calibration.compare_fit()
        # file description uses general variables
        description = "back: " + str(path_background) + "RZP-structure:___" + str(rzp_structure_name) + 'Roi:' + str(
            roi_list)
        for x in self.file_list:
            my_array = basic_file_app.load_2d_array(self.file_path + x, 0, 1, 2)
            my_calibration.calibrate_input_array(my_array, x, description)

    def avg_of_stack(self):
        self.file_list = basic_file_app.get_file_list(self.directory)
        print("xxxxxxxxxxxxxx mean value of stack xxxxxxxxxxxxx")
        print(self.directory, "path")
        print(self.file_list)
        my_avg = basic_file_app.StackMeanValue(self.file_list, self.directory, 0, 1, 4)
        my_result = my_avg.get_result()
        # print(my_result)
        plt.figure(10)
        plt.title("calibrated_spectrum")
        plt.plot(my_result[:, 0], my_result[:, 1], label="mean value")
        save_pic = os.path.join(self.directory, self.directory[4:] + "mean_spectrum" + ".png")
        plt.savefig(save_pic, bbox_inches="tight", dpi=500)
        np.savetxt(save_pic + "avg" + ".txt", my_result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

        return my_result


def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else:
        os.mkdir(name)


# Todo give path name background and image folder
path_background = "data/20220727/RZPL/test_eval/dark"
name_background = path_background
path_picture = "data/20220727/RZPL/test_eval/Ti"

# ToDo. set roi range spectrum and roi range background
# DEFINE ROI for EVAL and BACKGROUND
# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 159, 2048, 768])
back_roi = ([100, 0, 2048, 2000])

# ToDo change result folder name
# RESULT-PATH - important for processing
bin_path =str(path_picture)+"results_binned"
create_result_directory(bin_path)

# px size in mm, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
# is now given via read in txt - should look like this:
# rzp_structure_parameter = np.array([1.350e-02, 2.130e+00, 1.338e+03, 3.714e+00, 2.479e+03, 0.000e+00])

# toDo: give integration time to calculate in counts/s
# SCALING PARAMETER FOR counts + HEADER DESCRIPTION
laser_gate_time_data = 500  # ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZP_S2" + str(laser_gate_time_data) + "ms"

# BACKGROUND MEAN FROM IMAGE STACK
file_list_background = basic_image_app.get_file_list(path_background)
batch_background = basic_image_app.ImageStackMeanValue(file_list_background, path_background)
my_background = batch_background.average_stack()

# BIN AND PX-SHIFT CORRECTION:

# reference positions (px) for minimum in +/- 20px for px shift evaluation
# note ! that this position is relating to the ROI- of your image
reference_point_list = [233]
# path_binned_array_files to be opened for px-shifted arrays (usually excecution path for this python routine)
#key decides between max and min method for pixel-shift ("max" or "min")
Test = PxCorrectionOnStack(path_picture, reference_point_list, bin_path, "max")
Test.pre_process_stack()
Test.px_shift()

# SAVE AVG OF STACK UNCALIBRATED (after px-shift)
file_path_uncalibrated_stack = basic_file_app.get_file_list(bin_path)
my_uncalibrated_avg = basic_file_app.StackMeanValue(file_path_uncalibrated_stack, bin_path, 0, 1, 1)
np.savetxt("avg " + file_path_uncalibrated_stack[0], my_uncalibrated_avg.get_result(), delimiter=' ',
           header='string', comments='',
           fmt='%s')

plt.show()