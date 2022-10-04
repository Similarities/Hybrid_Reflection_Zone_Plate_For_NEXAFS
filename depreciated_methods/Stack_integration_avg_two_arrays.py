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
        self.x_axis = np.arange(0, self.roi_list[2] - self.roi_list[0]).astype(np.float32)

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
        self.binned_roi_y = np.sum(self.picture,  axis=0)
        # print(len(self.binned_roi_y), "len binned roi")
        return self.binned_roi_y, self.x_axis

    def scale_array_per_second(self, constant):
        self.binned_roi_y = basic_file_app.constant_array_scaling(self.binned_roi_y, constant)
        return self.binned_roi_y

    def reverse_array(self):
        self.binned_roi_y = self.binned_roi_y[::-1]
        return self.binned_roi_y

    def save_sum_of_y(self, new_dir):
        result = self.binned_roi_y
        save_name = os.path.join(new_dir, self.filename + '_binned_y' + ".txt")
        print(save_name)
        self.plot_sum()
        np.savetxt(save_name , result, delimiter=' ',
                   header='string', comments='',         fmt='%s')

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
        plt.plot(self.x_axis, self.binned_roi_y, label=self.filename)
        plt.ylabel("counts")
        plt.xlabel("px")
        plt.legend()



class PxShiftOnArrays:
    def __init__(self, avg_picture, avg_reference, reference_point, method, plot_number):
        self.avg_picture = avg_picture
        self.avg_reference = avg_reference
        self.reference_point = reference_point
        self.method = method
        self.plot_number = plot_number

    def px_shift_reference(self):
        evaluate_shift = px_shift_on_picture_array_rolling.PixelShift(self.avg_picture, self.reference_point,
                                                                      self.method)
        self.avg_reference = evaluate_shift.evaluate_shift_for_input_array(self.avg_reference, self.plot_number)
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

def plot_nexafs(array1, array2, name, figure_number):
    my_od = -np.log((array1[:]) / (array2[:]))
    # np.savetxt(bin_path_image + "/ODD" + name_picture + name_reference + ".txt", my_od, delimiter=' ',
    #          header='string', comments='')
    plt.figure(figure_number)
    plt.plot(my_od, label=name)
    plt.xlabel("px")
    plt.ylabel("Nexafs")
    plt.legend()
    plt.ylim(-0.5, 0.5)
    save_pic = os.path.join(result_folder, "ODD" + name + "Small_RoinB" + ".png")
    plt.savefig(save_pic, bbox_inches="tight", dpi=500)

    print("max odd:", np.amax(my_od), "min odd:", np.amin(my_od))


# Todo give path name background and image folder (1)
path_background = "../data/20220818_ZnO_pp_dunkelbild"
name_background = path_background
path_picture = "../data/20220818_ZnO_pp_oc_429_01"
name_picture = "20220808_oc429ppnoShifttB"

# Todo give path name background and image folder (2)

path_reference_picture = "../data/20220818_ZnO_up_oc_429_01"
name_reference = "20220808_oc429upnoShiftB"

# ToDo. set roi range spectrum and roi range background
# DEFINE ROI for EVAL and BACKGROUND
# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 0, 392, 600])
back_roi = ([100, 600, 2048, 2000])

# ToDo change result folder binned spectra name
# RESULT-PATH - important for processing
bin_path_image = "data/"+"Result_stack" + name_picture + name_reference
create_result_directory(bin_path_image)

#bin_path_reference = str(path_reference_picture) + "BackIntegratedStack"
#create_result_directory(bin_path_reference)

# ToDo change result avg and od folder
result_folder = "AVGStacks" + "Result" + "20220818"
create_result_directory(result_folder)

# px size in mm, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
# is now given via read in txt - should look like this:
# rzp_structure_parameter = np.array([1.350e-02, 2.130e+00, 1.338e+03, 3.714e+00, 2.479e+03, 0.000e+00])

# toDo: give integration time to calculate in counts/s
# SCALING PARAMETER FOR counts + HEADER DESCRIPTION
laser_gate_time_data = 10  # ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZP_S2" + str(laser_gate_time_data) + "ms"

# BACKGROUND MEAN FROM IMAGE STACK
t1 = time.time()
my_mean_background_picture = basic_image_app.read_image(path_background + name_background + ".tif")
my_background = basic_image_app.threshold_low_pass_cleaner(my_mean_background_picture, 3030)
t2 = time.time()
print(t1-t2, "seconds for background preparation")


# AVG on Stack
file_list_image = basic_image_app.get_file_list(path_picture)
avg_on_stack = basic_image_app.ImageStackMeanValue(file_list_image, path_picture)
avg_picture = avg_on_stack.average_stack()

file_list_referencce = basic_image_app.get_file_list(path_reference_picture)
avg_on_stack_2 = basic_image_app.ImageStackMeanValue(file_list_referencce, path_reference_picture)
avg_reference = avg_on_stack_2.average_stack()


Integrate = ImagePreProcessing(avg_picture, name_picture, my_background, name_background[:-4], roi_list, back_roi)
Integrate.background_subtraction()
Integrate.bin_in_y()
Integrate.scale_array_per_second(per_second_correction)
Integrate.save_sum_of_y(bin_path_image)

Integrate_reference = ImagePreProcessing(avg_reference, name_reference, my_background, name_background[:-4], roi_list, back_roi)
Integrate.background_subtraction()
Integrate_reference.bin_in_y()
Integrate_reference.scale_array_per_second(per_second_correction)
Integrate_reference.save_sum_of_y(bin_path_image)

plt.figure(111)
save_pic = os.path.join(result_folder, "PlotTogether" + name_picture+name_reference+ ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)



file_list = basic_file_app.get_file_list(bin_path_image)
print("binned files", file_list)
avg_picture_array = basic_file_app.load_1d_array(bin_path_image + "/" + file_list[0], 0,1)
avg_reference_array = basic_file_app.load_1d_array(bin_path_image+"/"+file_list[1], 0, 1)
np.savetxt(result_folder + "/AVG" + name_picture + ".txt", avg_picture_array, delimiter=' ',
           header='string', comments='')
np.savetxt(result_folder + "/AVG" + name_reference + ".txt", avg_reference_array, delimiter=' ',
           header='string', comments='')

plot_nexafs(avg_picture_array, avg_reference_array, name_picture + name_reference, 100)


#reference_point = [102]
#shift_it = PxShiftOnArrays(avg_picture_array, avg_reference_array, reference_point, "min", 114)
#shifted_reference = shift_it.px_shift_reference()
#plot_nexafs(avg_picture_array, shifted_reference, "shifted" + name_picture + name_reference, 101)



plt.show()
