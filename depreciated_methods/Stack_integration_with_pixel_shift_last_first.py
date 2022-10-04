import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import math
from depreciated_methods import plot_filter
import px_shift_on_picture_array_rolling
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
        self.extract_roi_picture()

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
        self.background = (self.background[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        self.picture[:, :] = self.picture[:, :] - self.background[:, :]

        # self.picture[self.picture < 0] = 1
        return self.picture

    def extract_roi_picture(self):
        self.picture = basic_image_app.convert_32_bit(
            self.picture[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
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
        result =  self.binned_roi_y
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
    def __init__(self, path, file_list, reference_point_list, new_dir, key, figurenumber):
        self.path = path
        self.file_list = file_list
        self.reference_points = reference_point_list
        self.new_dir = new_dir
        self.max_min_key = key
        self.plot_number = figurenumber
        self.key_back = False

    # addon (in pre-processing)
    def threshold_cleaner(self, picture, threshold):
        picture[picture > threshold] = 0
        # plt.imshow(picture)
        # plt.show()
        return picture

    def switch_on_off_back_correction(self, key):
        if key == True:
            self.key_back = True
        return self.key_back

    def pre_process_stack(self):
        print("file_list", self.file_list)
        for x in self.file_list:
            open_picture = basic_image_app.SingleImageOpen(x, self.path)
            my_picture = open_picture.return_single_image()
            # my_picture = self.threshold_cleaner(my_picture, 65000)
            PreProcess = ImagePreProcessing(my_picture, x, my_background, name_background[:-4], roi_list, back_roi)
            # Test.view_control()
            # PreProcess.reference_scaling()
            if self.key_back:
                PreProcess.background_subtraction()
            PreProcess.bin_in_y()
            PreProcess.scale_array_per_second(per_second_correction)
            # IMPORTANT: reverse array if high energy part is left
            #PreProcess.reverse_array()
            PreProcess.save_sum_of_y(self.new_dir)
            # plt.close()
        print("xxxxxxxxx - all px shifted xxxxxxxxxxxx")

    def px_shift(self):
        self.file_list = basic_file_app.get_file_list(self.new_dir)
        print(len(self.file_list), "number of files to be processed")

        reference = basic_file_app.load_1d_array(self.new_dir + '/' + self.file_list[0], 0, 1)
        # print("new file list", self.file_list)
        for x in self.file_list[1:]:
            image_array = basic_file_app.load_1d_array(self.new_dir + '/' + x, 0, 1)
            ShiftIt = px_shift_on_picture_array_rolling.PixelShift(reference, self.reference_points, self.max_min_key)
            corrected_array = ShiftIt.evaluate_shift_for_input_array(image_array, self.plot_number)
            self.overwrite_original(x, corrected_array)

    def overwrite_original(self, file_name, array):
        plt.figure(103)
        plt.plot( array)
        plt.title("px shifted stack")
        plt.ylabel("counts")
        plt.xlabel("px")
        plt.legend()
        print("overwriting original file..: ", file_name)
        save_name = os.path.join(self.new_dir, file_name[:-4] + ".txt")
        np.savetxt(save_name, array, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')



class PxShiftOnArrays:
    def __init__(self, avg_picture, avg_reference, reference_point, method, plot_number):
        self.avg_picture = avg_picture
        self.avg_reference = avg_reference
        self.reference_point = reference_point
        self.method = method
        self.plot_number = plot_number

    def px_shift_both(self):
        evaluate_shift = px_shift_on_picture_array_rolling.PixelShift(self.avg_picture, self.reference_point, self.method)
        self.avg_reference= evaluate_shift.evaluate_shift_for_input_array(self.avg_reference, self.plot_number)
        return self.avg_reference

    def norm_to_maximum_in_range(self,x1, x2):
        max_ref = np.amax(self.avg_reference[x1:x2])
        max_img = np.amax(self.avg_picture[x1:x2])
        self.avg_reference[:] = max_img/max_ref * (self.avg_reference[:])
        return self.avg_reference





def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else:
        os.mkdir(name)


# Todo give path name background and image folder (1)
path_background = "data/20220808/free_run_39_10ms_dunkelbilder"
name_background = path_background
path_picture = "data/20220808/free_run_21_70ms_50rpm"
all_picture_list= basic_image_app.get_file_list(path_picture)
first_pictures_list = all_picture_list[:99]
first_name = "21first"


# Todo give path name background and image folder (2)

path_reference_picture = path_picture
last_pictures_list = all_picture_list[len(all_picture_list)-110:-10]
print(len(last_pictures_list), "sssssssssssssssssssssssssssssss")
last_name = "21last"

#toDo implement in Test
for x in enumerate(last_pictures_list):
    if x in enumerate(first_pictures_list):
        print(x, "doubles")

plt.show()
# ToDo. set roi range spectrum and roi range background
# DEFINE ROI for EVAL and BACKGROUND
# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 180, 2048, 552])
back_roi = ([100, 0, 2048, 2000])

# ToDo change result folder name
# RESULT-PATH - important for processing
bin_path_image = str(path_picture) + "TESTFIRST"
create_result_directory(bin_path_image)
bin_path_reference = str(path_reference_picture) + "TESTLAST"
create_result_directory(bin_path_reference)
avg_path = "AVG"+first_name[:-4]
create_result_directory(avg_path)

# px size in mm, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
# is now given via read in txt - should look like this:
# rzp_structure_parameter = np.array([1.350e-02, 2.130e+00, 1.338e+03, 3.714e+00, 2.479e+03, 0.000e+00])

# toDo: give integration time to calculate in counts/s
# SCALING PARAMETER FOR counts + HEADER DESCRIPTION
laser_gate_time_data = 70 # ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZP_S2" + str(laser_gate_time_data) + "ms"

# BACKGROUND MEAN FROM IMAGE STACK
#file_list_background = basic_image_app.get_file_list(path_background)
#batch_background = basic_image_app.ImageStackMeanValue(file_list_background, path_background)
#my_background = batch_background.average_stack()
my_background = np.zeros([1,1])
# BIN AND PX-SHIFT CORRECTION:

# reference positions (px) for minimum in +/- 20px for px shift evaluation
# note ! that this position is relating to the ROI- of your image
reference_point_list = [102]
# path_binned_array_files to be opened for px-shifted arrays (usually excecution path for this python routine)
#key decides between max and min method for pixel-shift ("max" or "min")

Picture = PxCorrectionOnStack(path_picture, first_pictures_list, reference_point_list, bin_path_image, "min", 2)
print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", first_pictures_list)
Picture.pre_process_stack()
Picture.px_shift()

Reference = PxCorrectionOnStack(path_reference_picture, last_pictures_list,reference_point_list, bin_path_reference, "min",2)
print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", last_pictures_list)
Reference.pre_process_stack()
Reference.px_shift()

# SAVE AVG OF STACK UNCALIBRATED (after px-shift)
file_path_uncalibrated_stack = basic_file_app.get_file_list(bin_path_image)

my_uncalibrated_avg = basic_file_app.AvgOnColumn(file_path_uncalibrated_stack, bin_path_image, 0, 1)
np.savetxt(avg_path+ "/avg"+ first_name + ".txt", my_uncalibrated_avg.get_result(), delimiter=' ',
           header='string', comments='',
           fmt='%s')
image_avg = my_uncalibrated_avg.get_result()

get_reference_list= basic_file_app.get_file_list(bin_path_reference)
avg_for_reference = basic_file_app.AvgOnColumn(get_reference_list, bin_path_reference, 0, 1)
np.savetxt(avg_path +"/avg" + last_name + ".txt" , avg_for_reference.get_result(), delimiter=' ',
           header='string', comments='',
           fmt='%s')
reference_avg = avg_for_reference.get_result()
plt.figure(133)
plt.plot(image_avg)
plt.plot(reference_avg)
save_pic = os.path.join(avg_path, "PlotTogether"+first_name+last_name+ ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)


shift_it = PxShiftOnArrays(image_avg, reference_avg, reference_point_list, "min",4)

#my_shifte_reference = shift_it.norm_to_maximum_in_range(1725,1740)
my_shifte_reference = shift_it.px_shift_both()
#my_shifted_reference = np.roll(my_shifte_reference,-2)



plt.figure(22)
plt.plot(-np.log((image_avg[:]+2E5)/(my_shifte_reference[:]+2E5)), label = "ODD" + first_name + last_name)
plt.xlabel("px")
plt.ylabel("ODD")
plt.legend()
plt.xlim(50,1990)
plt.ylim(-0.05, 0.05)

save_pic = os.path.join(avg_path, "ODD"+first_name+last_name+ ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)
plt.show()


