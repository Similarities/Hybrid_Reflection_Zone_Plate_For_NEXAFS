import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import math
from depreciated_methods import plot_filter
import px_shift_on_picture_array_rolling
import poly_fit
import os
import time


# make sure the image-array (picture, background) is in 32bit
class ImagePreProcessing:
    # toDo give input pictures instead of calling class to often
    def __init__(self, background, background_name, roi_list1, number_of_files):
        self.filename = str
        self.picture = np.zeros([])
        self.background = background
        self.background_name = background_name
        self.binned_roi_y = np.zeros([])
        self.roi_list = roi_list1
        self.binned_mean_back = self.prepare_background_binned_and_roi()
        self.x_axis = np.arange(0, self.roi_list[2] - self.roi_list[0]).astype(np.float32)
        self.result_array = np.zeros([len(self.x_axis), number_of_files])

    def prepare_background_binned_and_roi(self):
        self.background = (self.background[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        return np.sum(self.background, axis=0)

    # addon (in pre-processing)
    def threshold_cleaner(self, value):
        self.picture[self.picture > value] = np.mean(self.binned_mean_back)
        # plt.imshow(picture)
        # plt.show()
        return self.picture

    def extract_roi_picture(self):
        self.picture = basic_image_app.convert_32_bit(
            self.picture[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        return self.picture

    def load_new_picture(self, picture, picture_name):
        self.picture = picture
        self.filename = picture_name
        self.extract_roi_picture()
        return self.picture, self.filename

    def background_subtraction_on_image(self):
        self.picture[:, :] = self.picture[:, :] - self.background[:, :]
        # self.picture[self.picture < 0] = 1
        return self.picture

    def bin_in_y(self):
        self.binned_roi_y = np.sum(self.picture, axis=0)
        # print(len(self.binned_roi_y), "len binned roi")
        return self.binned_roi_y, self.x_axis

    def background_substraction_on_binned_image(self):
        self.binned_roi_y = self.binned_roi_y - self.binned_mean_back
        return self.binned_roi_y

    def scale_array_per_second(self, constant):
        self.binned_roi_y = basic_file_app.constant_array_scaling(self.binned_roi_y, constant)
        return self.binned_roi_y

    def reverse_array(self):
        self.binned_roi_y = self.binned_roi_y[::-1]
        return self.binned_roi_y

    def append_sum_y(self, index):
        self.result_array[:, index] = self.binned_roi_y
        # print(self.result_array[:-1])
        return self.result_array

    def x_binning(self):
        binned_spectra = np.zeros([int(round(len(self.binned_roi_y / 2), 0)) + 1])
        for counter, value in enumerate(self.binned_roi_y):
            if counter % 2 == 0:
                binned_spectra[int(round(counter / 2, 0))] = self.binned_roi_y[counter - 1]
        plt.figure(1111)
        plt.plot(binned_spectra)
        plt.show()

    def save_result_array(self, new_dir):
        print(self.result_array[:, -1])
        save_name = os.path.join(new_dir, self.filename[:-8] + 'ALL_binned_y' + ".txt")
        np.savetxt(save_name, self.result_array, delimiter=' ', fmt="%.4e")
        return save_name

    def save_sum_of_y(self, new_dir):
        result = self.binned_roi_y
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
    def __init__(self, path, file_list, reference_point, new_dir1, new_dir2, key, figurenumber):
        self.path = path
        self.file_list = file_list
        print(self.file_list, self.path)
        self.reference_points = reference_point
        self.new_dir = new_dir1
        self.shift_directory = new_dir2
        self.shift_list = []
        self.method = "fft"
        self.plot_number = figurenumber
        self.key_back = False
        self.key_threshold = False
        self.threshold_limit = 650000
        self.processed_file = str
        self.px_shift_range = 10
        self.result_shifted_spectra = np.zeros([roi_list[2], len(self.file_list)])
        print(len(self.result_shifted_spectra))
        print(np.ndim(self.result_shifted_spectra))

    def switch_on_off_back_correction(self, bool):
        self.key_back = bool
        return self.key_back

    def append_shifted_array(self, corrected_array, index):
        self.result_shifted_spectra[:, index] = corrected_array
        return self.result_shifted_spectra

    def apply_threshold(self, bool, value):
        self.key_threshold = bool
        self.threshold_limit = value
        return self.key_threshold, self.threshold_limit

    def set_range_px_shift(self, range):
        self.px_shift_range = range
        return self.px_shift_range

    def select_px_shift_method(self, key_string):
        self.method = key_string
        # "max", "min", "fft" = or anything else
        return self.method

    def pre_process_stack(self):
        # roi_list is a general public variable
        PreProcess = ImagePreProcessing(my_background, name_background[:-4], roi_list, len(self.file_list))
        for counter, x in enumerate(self.file_list):
            tx = time.time()
            open_picture = basic_image_app.SingleImageOpen(x, self.path)
            my_picture = open_picture.return_single_image()

            # Test.view_control()
            PreProcess.load_new_picture(my_picture, x)

            # be careful with that one here:
            if self.key_threshold:
                PreProcess.threshold_cleaner(self.threshold_limit)

            PreProcess.bin_in_y()
            # PreProcess.reference_scaling()
            if self.key_back:
                # print("xxxxxxxxxxxxx back ground substraction on single image of stack")
                PreProcess.background_substraction_on_binned_image()

            PreProcess.scale_array_per_second(per_second_correction)
            # IMPORTANT: reverse array if high energy part is left
            # PreProcess.reverse_array()
            PreProcess.append_sum_y(counter)
            print("calc time per image:", round(time.time() - tx, 2))

        self.processed_file = PreProcess.save_result_array(self.new_dir)

    def px_shift(self):

        all_integrated_spectra = basic_file_app.load_all_columns_from_file(self.processed_file, 0)
        reference = all_integrated_spectra[:, 0]
        tshift = time.time()
        for x in range(0, len(self.file_list) - 1):
            single_binned_spectra = all_integrated_spectra[:, x]
            shiftIt = px_shift_on_picture_array_rolling.PixelShift(reference, self.reference_points, self.method)
            """ Pixel-shift Method: """
            if self.method == "fft":
                corrected_array, shift = shiftIt.evaluate_correct_shift_via_fft_for_input_array(single_binned_spectra,
                                                                                                self.plot_number,
                                                                                                self.px_shift_range)
            elif self.method == "max":
                corrected_array, shift = shiftIt.evaluate_shift_for_input_array(single_binned_spectra, self.plot_number)

            elif self.method == "min":
                corrected_array, shift = shiftIt.evaluate_shift_for_input_array(single_binned_spectra, self.plot_number)

            else:
                raise error

            self.shift_list.append(shift)
            self.append_shifted_array(corrected_array, x)
        print("time elapsed for px-shift on stack:", time.time() - tshift)
        self.save_shift_list()
        self.save_px_shifted_arrays(self.file_list[0])

    def plot_shift_list(self):
        plt.figure(105)
        plt.title("shift_plot")
        plt.plot(self.shift_list)
        plt.show()

    def return_name_of_shifted_arrays_file(self):
        file_name = self.file_list[0]
        return str(self.shift_directory + "/" + "Shifted_spectra" + file_name[:-8] + ".txt")

    def save_shift_list(self):
        save_shift_name = os.path.join(self.shift_directory, "Shiftlist" + ".txt")
        np.savetxt(save_shift_name, self.shift_list, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

    # ToDo: shift array processing saves one array  each line a spectra, not single spectra
    def save_px_shifted_arrays(self, file_name):
        save_name = os.path.join(self.shift_directory, "Shifted_spectra" + file_name[:-8] + ".txt")
        np.savetxt(save_name, self.result_shifted_spectra, delimiter=' ')


class PxShiftOnArrays:
    def __init__(self, avg_picture, avg_reference, reference_point, method, plot_number):
        self.avg_picture = avg_picture
        self.avg_reference = avg_reference
        self.reference_point = reference_point
        self.method = method
        self.plot_number = plot_number
        self.px_shift_range = 10

    def px_shift_both(self):
        evaluate_shift = px_shift_on_picture_array_rolling.PixelShift(self.avg_picture, self.reference_point,
                                                                      self.method)

        if self.method == "min" or method == "max":
            self.avg_reference, shift = evaluate_shift.evaluate_shift_for_input_array(self.avg_reference, self.plot_number)
        elif self.method == "fft":
            self.avg_reference, shift = shiftIt.evaluate_correct_shift_via_fft_for_input_array(self.avg_reference,
                                                                                            self.plot_number,
                                                                                            self.px_shift_range)
        else:
            raise error

        return self.avg_reference

    def norm_to_maximum_in_range(self, x1, x2):
        max_ref = np.amax(self.avg_reference[x1:x2])
        max_img = np.amax(self.avg_picture[x1:x2])
        self.avg_reference[:] = max_img / max_ref * (self.avg_reference[:])
        return self.avg_reference


def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else:
        os.mkdir(name)


def make_parameter_file():
    names = ("picture:", name_picture)
    name2 = ("reference:", name_reference)
    name3 = ("background:", name_background)
    roi = ("roi:", roi_list)
    pointing = ("pointing ref:", reference_point_list)
    param = np.vstack((names, name2, name3, roi, pointing))
    np.savetxt(result_folder + "/" + name_picture + "_parameter" + ".txt", param, delimiter=' ',
               header='string', comments='',
               fmt='%s')


# Todo give path name background and image folder (1)
path_background = "data/20220914x/"
name_background = "AVG_dark_100ms"
path_picture = "data/20220914x/Ti_100msII"

reference_path = "data/20220914x/W_100msII"

picture_list = basic_image_app.get_file_list(path_picture)
reference_list = basic_image_app.get_file_list(reference_path)
# Todo give path name background and image folder (2)
name_picture = "Ti_100ms_03"
name_reference = "W_100ms_02"

# ToDo. set roi range spectrum and roi range background
# DEFINE ROI for EVAL and BACKGROUND
# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 213, 1850, 332])
back_roi = ([0, 0, 0, 0])

parameter = (roi_list, back_roi, name_reference, name_picture)

# ToDo change result folder binned spectra name
# RESULT-PATH - important for processing
bin_path_image = str(path_picture) + "IntegratedSingleB"
create_result_directory(bin_path_image)
bin_path_reference = str(path_picture) + "IntegratedSingleB"
create_result_directory(bin_path_reference)
shift_path_image = bin_path_image + "FFTshift"
create_result_directory(shift_path_image)
shift_path_reference = bin_path_reference + "FFTshift"
create_result_directory(shift_path_reference)

# ToDo change result avg and od folder
result_folder = "TwoFolder20220914" + "_result" + "FFTshifted_on_StackBdark"
create_result_directory(result_folder)

# px size in mm, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
# is now given via read in txt - should look like this:
# rzp_structure_parameter = np.array([1.350e-02, 2.130e+00, 1.338e+03, 3.714e+00, 2.479e+03, 0.000e+00])

# toDo: give integration time to calculate in counts/s
# SCALING PARAMETER FOR counts + HEADER DESCRIPTION
laser_gate_time_data = 100  # ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZP_S2" + str(laser_gate_time_data) + "ms"

# BACKGROUND MEAN FROM IMAGE STACK, simplified version with threshold cleaner


t1 = time.time()
my_mean_background_picture = basic_image_app.read_image(path_background + name_background + ".tif")
my_background = basic_image_app.threshold_low_pass_cleaner(my_mean_background_picture, 1200)
# my_background_lineout = np.sum(my_background, axis = 0)
t2 = time.time()
print(t1 - t2, "seconds for background preparation")

# toDo BIN AND PX-SHIFT CORRECTION:

# reference positions (px) for minimum in +/- 20px for px shift evaluation
# note ! that this position is relating to the ROI- of your image
reference_point_list = [1645]
# path_binned_array_files to be opened for px-shifted arrays (usually excecution path for this python routine)
# key decides between max and min method for pixel-shift ("max" or "min")


Picture = PxCorrectionOnStack(path_picture, picture_list, reference_point_list, bin_path_image, shift_path_image, "fft",
                              2)
Picture.switch_on_off_back_correction(True)
# Picture.apply_threshold(True, 800)
Picture.set_range_px_shift(8)
Picture.pre_process_stack()
Picture.px_shift()
Picture.plot_shift_list()

shifted_image_stack_file = Picture.return_name_of_shifted_arrays_file()

plt.show()

reference_point_list = [1645]
Reference = PxCorrectionOnStack(reference_path, reference_list, reference_point_list, bin_path_reference,
                                shift_path_reference,
                                "fft", 2)
print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", path_picture)
Reference.switch_on_off_back_correction(True)
# Reference.apply_threshold(True, 1000)
Reference.set_range_px_shift(10)
Reference.pre_process_stack()
Reference.px_shift()
Reference.plot_shift_list()

shifted_reference_stack_file = Reference.return_name_of_shifted_arrays_file()

# SAVE AVG OF STACK UNCALIBRATED (after px-shift)
file_path_uncalibrated_stack = basic_file_app.get_file_list(bin_path_image)

average_image = basic_file_app.AvgOverAxis1(shifted_image_stack_file, 0)
image_avg = average_image.average_stack()
# image_avg = image_avg - my_background_lineout[:-4]
np.savetxt(result_folder + "/AvgB" + name_picture + ".txt", image_avg, delimiter='',
           header='string', comments='',
           fmt='%s')

avg_for_reference = basic_file_app.AvgOverAxis1(shifted_reference_stack_file, 0)
reference_avg = avg_for_reference.average_stack()
# reference_avg = reference_avg - my_background_lineout[:-4]
np.savetxt(result_folder + "/AvgB" + name_reference + ".txt", reference_avg, delimiter=' ',
           header='string', comments='',
           fmt='%s')

shift_it = PxShiftOnArrays(image_avg, reference_avg, reference_point_list, "min", 4)
# ToDo: if you want to norm one of the spectras to the other here give a range for max evaluation (choose a peak)
# my_shifte_reference = shift_it.norm_to_maximum_in_range(1725, 1740)
my_shifte_reference = shift_it.px_shift_both()

plt.figure(1696)
plt.title("in stack shifted two measurements")
plt.plot(image_avg, label="image")
plt.plot(reference_avg, label="reference unshifted")
plt.plot(my_shifte_reference, label="reference shifted")
plt.legend()
save_pic = os.path.join(result_folder, "PlotTogether" + name_picture + name_reference + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)


my_od = -np.log((image_avg[:]) / (my_shifte_reference[:]))
plt.figure(23)
plt.title("in stack and to stack shifted to measurments")
plt.plot(my_od, label="shifted to each other nexafs")

plt.xlabel("px")
plt.ylabel("ODD")
plt.xlim(0, 2000)
plt.legend()

save_pic = os.path.join(result_folder, "ODD_image_reference_shifted" + name_picture + name_reference + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)

plt.figure(22)
plt.title("in stack shiftedt not to stack shifted, 2 measurements")
plt.plot(-np.log((image_avg[:]) / (reference_avg[:])), label="ODD" + name_picture + name_reference)
plt.xlabel("px")
plt.ylabel("ODD")
plt.xlim(0, 2000)
plt.legend()

save_pic = os.path.join(result_folder, "ODD_not_shifted" + name_picture + name_reference + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)
plt.show()

make_parameter_file()

# ToDo: externalise Image processing
# ToDo: better logic for switching the method - with automatically changing file-nomination
# ToDO: adapt concept to other scripts - delete unwanted solutions
# ToDo: version control git for different purposes
# Todo: avg picture as reference for shift
