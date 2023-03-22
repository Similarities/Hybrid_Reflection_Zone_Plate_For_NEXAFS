import matplotlib.pyplot as plt
import numpy as np
import basic_file_app
import px_shift_on_picture_array_rolling
import os
import time





class PxCorrectionOnStack:
    def __init__(self,  lineout_array, reference_point_list , new_dir2, key, figurenumber, save_name):
        self.reference_points = reference_point_list
        self.lineout_array= lineout_array
        self.number_of_lineouts = len(self.lineout_array[0])
        print("number of lineouts:", self.number_of_lineouts)
        self.shift_directory = new_dir2
        self.shift_list = []
        self.method= key
        self.plot_number = figurenumber
        self.key_threshold = False
        self.threshold_limit = 650000
        self.px_shift_range = 10
        self.result_shifted_spectra = np.zeros([roi_list[2], self.number_of_lineouts])
        print(len(self.result_shifted_spectra))
        print(np.ndim(self.result_shifted_spectra))
        self.save_name = save_name



    def set_range_px_shift(self, range):
        self.px_shift_range = range
        return self.px_shift_range

    def append_shifted_array(self, corrected_array, index):
        self.result_shifted_spectra[:, index] = corrected_array
        return self.result_shifted_spectra

    def apply_threshold(self, bool, value):
        self.key_threshold = bool
        self.threshold_limit = value
        return self.key_threshold, self.threshold_limit

    def px_shift(self):

        reference = self.lineout_array[:, 0]
        tshift = time.time()
        for x in range(0, self.number_of_lineouts - 1):
            single_binned_spectra = self.lineout_array[:, x]
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
                raise 'error'

            self.shift_list.append(shift)
            self.append_shifted_array(corrected_array, x)
        print("time elapsed for px-shift on stack:", time.time() - tshift)
        self.save_shift_list()
        self.save_px_shifted_arrays()

    def plot_shift_list(self, name):
        plt.figure(105)
        plt.title("shift_plot")
        plt.plot(self.shift_list, label=name)
        plt.xlabel("shot no")
        plt.ylabel("px shift")
        plt.legend()

    def return_name_of_shifted_arrays_file(self):
        return str(self.shift_directory + "/" + "Shifted_spectra" + self.save_name + ".txt")

    def save_shift_list(self):
        save_shift_name = os.path.join(self.shift_directory, "Shiftlist" + ".txt")
        np.savetxt(save_shift_name, self.shift_list, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

    # ToDo: shift array processing saves one array  each line a spectra, not single spectra
    def save_px_shifted_arrays(self):
        save_name = os.path.join(self.shift_directory, "Shifted_spectra" + self.save_name + ".txt")
        np.savetxt(save_name, self.result_shifted_spectra, delimiter=' ')


class PxShiftOnArrays:
    def __init__(self, avg_picture, avg_reference, reference_point, method, plot_number):
        self.avg_picture = avg_picture
        self.avg_reference = avg_reference
        self.reference_point = reference_point
        self.method = method
        self.px_shift_range = 10
        self.plot_number = plot_number

    def px_shift_both(self):
        evaluate_shift = px_shift_on_picture_array_rolling.PixelShift(self.avg_picture, self.reference_point,
                                                                      self.method)

        if self.method == "min" or self.method == "max":
            self.avg_reference, shift = evaluate_shift.evaluate_shift_for_input_array(self.avg_reference, self.plot_number)
        elif self.method == "fft":
            self.avg_reference, shift = evaluate_shift.evaluate_correct_shift_via_fft_for_input_array(self.avg_reference,
                                                                                            self.plot_number,
                                                                                            self.px_shift_range)
        else:
            raise 'error'

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
    roi = ("roi:", roi_list)
    pointing = ("pointing ref:", reference_point_list)
    param = np.vstack((names, name2, roi, pointing))
    np.savetxt(result_folder + "/" + name_picture + "_parameter" + ".txt", param, delimiter=' ',
               header='string', comments='',
               fmt='%s')


# Todo give path name background and image folder (1)

path_lineout_array_1= "data/20221101/pp_TiN_300s_10ms_8mJ_440delayIntegratedSingleEvenB/pp_TiN_300s_10ms_8mJ_440delay_1_ALL_binned_y.txt"
path_lineout_array_2= "data/20221101/pp_TiN_300s_10ms_8mJ_440delayIntegratedSingleBODD/pp_TiN_300s_10ms_8mJ_440delay_1_ALL_binned_y.txt"
name_picture = "TiN10ms_450_pxshiftedFFTeven"
name_reference = name_picture[:-4] +"odd"



even_lineout_array = basic_file_app.load_all_columns_from_file(path_lineout_array_1,0)
odd_lineout_array = basic_file_app.load_all_columns_from_file(path_lineout_array_2, 0)
print(even_lineout_array)
print("len", len(even_lineout_array))
print("shape", len(even_lineout_array[0]), len(even_lineout_array.shape))

# ToDo. set roi range spectrum and roi range background
# DEFINE ROI for EVAL and BACKGROUND
# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 57, 2000, 188])
back_roi = ([0, 0, 0, 0])

# ToDo change result folder binned spectra name
# RESULT-PATH
shift_path_image = name_picture + "FFTShiftedEven1"
create_result_directory(shift_path_image)
shift_path_reference = name_reference + "FFTShiftedOdd1"
create_result_directory(shift_path_reference)

# ToDo change result avg and od folder
result_folder = name_picture[:-4]+ "FFTPxshifted_on_StackB1"
create_result_directory(result_folder)


# toDo BIN AND PX-SHIFT CORRECTION:

# reference positions (px) for minimum for px shift evaluation
# note ! that this position is relating to the ROI- of your image
reference_point_list = [1688]
# path_binned_array_files to be opened for px-shifted arrays (usually excecution path for this python routine)
# key decides between max and min method for pixel-shift ("max" or "min" or "fft")
# set_range_px applies the range in px on which the px-shift is evaluated (usually with a wide range it is not accurate
# if you have a low signal)

Picture = PxCorrectionOnStack( even_lineout_array,  reference_point_list,  shift_path_image,
                              "fft", 2, name_picture)

Picture.set_range_px_shift(8)
Picture.px_shift()
Picture.plot_shift_list("image")

shifted_image_stack_file = Picture.return_name_of_shifted_arrays_file()

Reference = PxCorrectionOnStack(odd_lineout_array,  reference_point_list,
                                shift_path_reference,
                                "fft", 11, name_reference)

Reference.set_range_px_shift(8)
Reference.px_shift()
Reference.plot_shift_list("reference")

shifted_reference_stack_file = Reference.return_name_of_shifted_arrays_file()


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

plt.figure(133)
plt.title("image reference plot")
plt.plot(image_avg, label="image")
plt.plot(reference_avg, label="reference")
save_pic = os.path.join(result_folder, "PlotTogether" + name_picture + name_reference + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)



shift_it = PxShiftOnArrays(image_avg, reference_avg, [1745], "min", 4)
# ToDo: if you want to norm one of the spectras to the other here give a range for max evaluation (choose a peak)
# my_shifte_reference = shift_it.norm_to_maximum_in_range(1725, 1740)
my_shifte_reference = shift_it.px_shift_both()
plt.figure(133)
plt.plot(my_shifte_reference, label="shifted ref")
plt.legend()
my_od = np.zeros(len(my_shifte_reference))

my_od = -np.log((image_avg[:]) / (my_shifte_reference[:]))
plt.figure(23)
plt.title("transient shifted stacks (EVEN_ODD)")
plt.plot(my_od, label="shifted to each other nexafs")

plt.xlabel("px")
plt.ylabel("ODD")
plt.ylim(-0.05, 0.05)
plt.xlim(20, 1740)
plt.legend()

save_pic = os.path.join(result_folder, "ODD_image_reference_shifted" + name_picture + name_reference + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)

plt.figure(22)
plt.title("Transient not shifted stacks (EVEN_ODD)")
plt.plot(-np.log((image_avg[:]) / (reference_avg[:])), label="ODD" + name_picture + name_reference)
plt.xlabel("px")
plt.ylabel("ODD")
plt.ylim(-0.05, 0.05)
plt.xlim(20, 1740)
plt.legend()

save_pic = os.path.join(result_folder, "ODD_unshifted" + name_picture + name_reference + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)
plt.show()


make_parameter_file()
