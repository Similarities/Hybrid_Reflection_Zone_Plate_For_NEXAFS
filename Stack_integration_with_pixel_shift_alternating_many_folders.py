import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import px_shift_on_picture_array_rolling
import os
import time


# make sure the image-array (picture, background) is in 16bit
'This is the batched batch script'
'it will process (extract roi, substract background, integrate, pixelshift) images sequences'
'it will generate from files in one folder 2 sequences by even and odd numbered files'
'it will create according results folder'
'it will do this for each folder'



class ImagePreProcessing:
    # toDo give input pictures instead of calling class to often
    def __init__(self, background_picture, background_name, roi_list, number_of_files):
        self.filename = str
        self.picture = np.zeros([])
        self.background = background_picture
        self.background_name = background_name
        self.binned_roi_y = np.zeros([])
        self.roi_list = roi_list
        self.binned_mean_back = self.extract_roi_on_back_array_to_lineout()
        self.x_axis = np.arange(0, self.roi_list[2] - self.roi_list[0]).astype(np.float32)
        self.result_array = np.zeros([len(self.x_axis), number_of_files])


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

    def extract_roi_on_back_array_to_lineout(self):
        self.background = basic_image_app.convert_32_bit(
            self.background[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        self.background = np.sum(self.background, axis  = 0)
        return self.background





    def load_new_picture(self, picture, picture_name):
        self.picture = picture
        self.filename = picture_name
        self.extract_roi_picture()
        return self.picture, self.filename


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

    def check_intensity(self, file_list):
        cross_sum = []
        print(self.result_array)
        cross_sum= np.sum(self.result_array, axis = 0)


        print(len(cross_sum), len(self.result_array))
        maximum = np.max(cross_sum)
        for counter, value in enumerate(cross_sum):
            print(value, counter)

            if value < 0.6*maximum:

                self.result_array[:,counter] = self.result_array[:,counter]*0
                print("set on line to zero", "index of the line is", counter)
                print(file_list[counter])




    def x_binning(self):
        binned_spectra = np.zeros([int(round(len(self.binned_roi_y / 2), 0)) + 1])
        for counter, value in enumerate(self.binned_roi_y):
            if counter % 2 == 0:
                binned_spectra[int(round(counter / 2, 0))] = self.binned_roi_y[counter - 1]
        plt.figure(1109)
        plt.plot(binned_spectra)
        # plt.show()

    def save_result_array(self, new_dir):
        # print(self.result_array[:,-1])
        save_name = os.path.join(new_dir, self.filename[:-8] + 'ALL_binned_y' + ".txt")
        np.savetxt(save_name, self.result_array, delimiter=' ', fmt="%.4e")
        test = basic_file_app.load_all_columns_from_file(save_name, 0)

        # plt.figure(11)
        # plt.plot(self.result_array[:,0])
        # plt.plot(test[:,0])
        # plt.show()
        return save_name

    def save_sum_of_y(self, new_dir):
        result = self.binned_roi_y
        save_name = os.path.join(new_dir, self.filename[:-4] + '_binned_y' + ".txt")
        self.plot_sum()
        np.savetxt(save_name, result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

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
    def __init__(self, path, file_list, reference_point_list, new_dir1, new_dir2, key, name, background_picture):
        self.path = path
        self.sequence_name = name
        self.file_list = file_list
        print(self.file_list, self.path)
        self.background = background_picture
        self.reference_points = reference_point_list
        self.new_dir = new_dir1
        self.shift_directory = new_dir2
        self.shift_list = []
        self.method= key
        self.plot_number = 2
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

    def pre_process_stack(self):
        # roi_list is a general public variable
        PreProcess = ImagePreProcessing(self.background, name_background[:-4], roi_list, len(self.file_list))
        tstack = time.time()
        for counter, x in enumerate(self.file_list):
            #tx = time.time()
            open_picture = basic_image_app.SingleImageOpen(x, self.path)
            my_picture = open_picture.return_single_image()
            PreProcess.load_new_picture(my_picture, self.sequence_name)
            # Test.view_control()
            if self.key_threshold:
                PreProcess.threshold_cleaner(self.threshold_limit)
            PreProcess.bin_in_y()
            if self.key_back:
                PreProcess.background_substraction_on_binned_image()

            #PreProcess.scale_array_per_second(per_second_correction)
            # IMPORTANT: reverse array if high energy part is left
            # PreProcess.reverse_array()
            PreProcess.append_sum_y(counter)
            #print("calc time per image:", round(time.time() - tx, 2), "__", counter)
            print("image number__", counter)
        PreProcess.check_intensity(self.file_list)
        print("time elapsed for stack image calculation", (time.time()-tstack)/60, "min")
        self.processed_file = PreProcess.save_result_array(self.new_dir)

    def px_shift(self):
        all_integrated_spectra = basic_file_app.load_all_columns_from_file(self.processed_file, 0)
        print("xxxxxxxxxxxxx", np.random.randint(low =0, high=len(self.file_list), size=1))
        reference = all_integrated_spectra[:, np.random.randint(low =1, high=len(self.file_list)-1, size=1)]
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
                raise EOFError

            self.shift_list.append(shift)
            self.append_shifted_array(corrected_array, x)
        print("time elapsed for px-shift on stack:", time.time() - tshift)
        self.save_shift_list()
        self.save_px_shifted_arrays(self.file_list[0])

    def plot_shift_list(self, name):
        plt.figure(105)
        plt.title("shift_plot")
        plt.plot(self.shift_list, label=name)
        plt.xlabel("shot no")
        plt.ylabel("px shift")
        plt.legend()

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
        self.px_shift_range = 40
        self.plot_number = plot_number

    def px_shift_both(self):
        evaluate_shift = px_shift_on_picture_array_rolling.PixelShift(self.avg_picture, self.reference_point,
                                                                      self.method)

        if self.method == "min" or self.method == "max":
            self.avg_reference, shift = evaluate_shift.evaluate_shift_for_input_array(self.avg_reference, self.plot_number)
            print(shift, "shift of even to odd")
        elif self.method == "fft":
            self.avg_reference, shift = evaluate_shift.evaluate_correct_shift_via_fft_for_input_array(self.avg_reference,
                                                                                            self.plot_number,
                                                                                            self.px_shift_range)
            print(shift, "shift of even to odd")
        else:
            raise EOFError

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

def make_parameter_file(folder_name_to_save, param):
    names = ("picture:", "str")
    name2 = ("reference:", "str")
    name3 = ("background:", name_background)
    roi = ("roi:", roi_list)
    pointing = ("pointing ref:", reference_point_list)
    param = np.vstack((names, name2, name3, roi, pointing))
    np.savetxt(folder_name_to_save+ "/" + "str" + "_parameter" + ".txt", param, delimiter=' ',
               header='string', comments='',
               fmt='%s')

class BatchOverFolderListWithAlternatingSequences:
    def __init__(self, path, folder_list, roi_list, reference_points, background_array):
        self.path = path
        self.folder_list = folder_list
        self.roi_list = roi_list
        self.reference_point = reference_points
        self.background_array = background_array
        self.name = folder_list[0]
        self.result_folder = str
        self.list_even, self.list_odd = [], []
        self.name_even = str
        self.name_odd = str
        self.bin_path_name_even = str
        self.shift_path_name_even = str
        self.bin_path_name_odd = str
        self.shift_path_name_odd = str



    def create_result_folders(self):
        create_result_directory(self.result_folder)
        create_result_directory(self.bin_path_name_odd)
        create_result_directory(self.bin_path_name_even)
        create_result_directory(self.shift_path_name_even)
        create_result_directory(self.shift_path_name_odd)


    def change_folder_name(self):
        self.bin_path_name_even = "Integrated_Even" + self.name
        self.shift_path_name_even = "Shifted_Even" + self.name
        self.bin_path_name_odd = "Integrated_Odd" + self.name
        self.shift_path_name_odd = "Shifted_Odd" + self.name
        self.result_folder = "Result" + self.name
        self.create_result_folders()


    def separate_alternating_stack_lists(self):
        all_picture_list = basic_image_app.get_file_list(self.path + "/" + self.name)
        self.list_even, self.list_odd = basic_file_app.even_odd_lists_string_sort(all_picture_list)
        self.name_even = self.name + "_even"
        self.name_odd = self.name + "odd"
        return self.list_even, self.list_odd, self.name_even, self.name_odd





    def process_image_sequence(self, bin_path, shift_path, file_liste, name):
        path_even = self.path + '/' + self.name
        Picture = PxCorrectionOnStack(path_even, file_liste, self.reference_point, bin_path,
                                      shift_path,
                                      "min",  name, self.background_array)
        Picture.switch_on_off_back_correction(True)
        Picture.pre_process_stack()
        Picture.set_range_px_shift(7)
        Picture.px_shift()
        Picture.plot_shift_list("image")

        shifted_image_stack_file = Picture.return_name_of_shifted_arrays_file()
        return shifted_image_stack_file

    def average_over_sequence(self, file_name, name):
        avg_for_reference = basic_file_app.AvgOverAxis1(file_name, 0)
        reference_avg = avg_for_reference.average_stack()
        # reference_avg = reference_avg - my_background_lineout[:-4]
        print(self.result_folder)
        save_csv = os.path.join(self.result_folder, "AVG" + name + ".txt")
        np.savetxt(save_csv, reference_avg, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')
        return reference_avg

    def save_shifted_reference(self, file_name, array):
        save_csv = os.path.join(self.result_folder, "AVG_shifted_reference" + file_name + ".txt")
        np.savetxt(save_csv, array, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

    def plot_together(self, array, name, figure_number, picture_name):
        plt.figure(figure_number)
        plt.plot(array, label = name)
        plt.title(picture_name)
        save_pic = os.path.join(self.result_folder, picture_name + name + ".png")
        plt.savefig(save_pic, bbox_inches="tight", dpi=500)


    def main(self):
        for counter, x in enumerate (self.folder_list):
            print(x)
            self.name = folder_list[counter]
            self.change_folder_name()
            self.separate_alternating_stack_lists()
            shifted_even = self.process_image_sequence(self.bin_path_name_even, self.shift_path_name_even, self.list_even, self.name_even)
            avg_even = self.average_over_sequence(shifted_even, self.name_even)
            self.plot_together(avg_even, self.name_even, 13, "PlotTogether")
            shifted_odd = self.process_image_sequence(self.bin_path_name_odd, self.shift_path_name_odd, self.list_odd,
                                        self.name_odd)
            avg_odd = self.average_over_sequence(shifted_odd, self.name_odd)

            self.plot_together(avg_odd, self.name_odd, 13, "PlotTogether_"+self.name)

            print("min position index in even", np.argmin(avg_even[1000:1800]))
            reference = [np.argmin(avg_even[1000:1800])+1000]
            Shift_to_Each_Ohter = PxShiftOnArrays(avg_even, avg_odd, reference, "fft", 111)
            shifted_odd = Shift_to_Each_Ohter.px_shift_both()
            self.save_shifted_reference(self.name_odd, shifted_odd)

            self.plot_together(-np.log(shifted_odd/avg_even), "transient_signal", 22, "Transient_signal " + self.name )



def scale_integrated_counts(self, laser_integration_time ):
    per_second_correction = 1000 / laser_integration_time # [ms]
    #todo needs to be connected to integrated array

#Todo give the main data folder your subfolders are inside
path_general = "data/20230309"
folder_list = basic_file_app.get_folder_list(path_general)
folder_list = basic_file_app.filter_list_by_string(folder_list, "20230309_NiO")
print(folder_list)

'create background array from avg picture '
path_background = "data/20230309/dark/AVG_20230309_dunkelbildNiO_O_edge_.tif"
# For acceleration of calculation the avg-background picture should be given NOT a FOLDER
name_background = "AVG_20230309_dunkelbildNiO_O_edge_.tif"
background = basic_image_app.read_image(path_background)

roi_list = [0,108, 2048, 390]
reference_point_list = [1386]
First_test = BatchOverFolderListWithAlternatingSequences(path_general, folder_list, roi_list, reference_point_list, background)
First_test.main()

plt.show()

#toDo remove static array size in self.result_shifted_spectra...
#toDo the fft method over a wider range or a different auto correlation method - is not working properly

