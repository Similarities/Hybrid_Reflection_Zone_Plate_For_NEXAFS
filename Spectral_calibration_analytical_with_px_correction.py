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

    def __init__(self, picture, picture_name, background, background_name, roi_list, back_roi):
        self.filename = picture_name
        self.picture = picture
        self.background = background
        self.background_name = background_name
        # x1, y1, x2, y2
        self.back_roi = back_roi
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
        self.picture[self.picture < 0] = 1
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

    def save_sum_of_y(self, new_dir):
        result = np.stack((self.x_axis_nm, self.binned_roi_y), axis=1)
        save_name = os.path.join(new_dir, self.filename[:-9] + '_binned_y' + ".txt")
        np.savetxt(save_name , result, delimiter=' ',
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
    def __init__(self, path, reference_point_list, new_dir):
        self.path = path
        self.file_list = basic_image_app.get_file_list(path_picture)
        self.reference_points = reference_point_list
        self.new_dir = new_dir



    #addon (in pre-processing)
    def threshold_cleaner(self, picture, threshold):
        picture[picture > threshold] = 0
        #plt.imshow(picture)
        #plt.show()
        return picture

    def pre_process_stack(self):
        for x in self.file_list:
            open_picture = basic_image_app.SingleImageOpen(x, path_picture)
            my_picture = open_picture.return_single_image()
            my_picture = self.threshold_cleaner(my_picture, 3000)
            PreProcess = ImagePreProcessing(my_picture, x, my_background, name_background[:-4], roi_list, back_roi)
            # Test.view_control()
            PreProcess.reference_scaling()
            PreProcess.background_subtraction()
            PreProcess.bin_in_y()
            PreProcess.scale_array_per_second(per_second_correction)
            PreProcess.save_sum_of_y(self.new_dir)
        print("xxxxxxxxx - all px shifted xxxxxxxxxxxx")

    def px_shift(self):
        self.file_list = basic_file_app.get_file_list(self.new_dir)
        print(len(self.file_list))
        reference = basic_file_app.load_2d_array(self.new_dir + '/' +self.file_list[0], 0, 1, 1)
        #print("new file list", self.file_list)
        for x in self.file_list[1:]:
            image_array = basic_file_app.load_2d_array(self.new_dir + '/' +x, 0, 1, 1)
            ShiftIt = px_shift_on_picture_array.PixelShift(reference, self.reference_points)
            corrected_array = ShiftIt.evaluate_shift_for_input_array(image_array)
            self.overwrite_original(x, corrected_array)

    def overwrite_original(self, file_name, array):
        print("overwriting original file..: ", file_name)
        save_name = os.path.join(self.new_dir, file_name[:-4] + ".txt")
        np.savetxt(save_name, array, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')


class BatchCalibration:
    def __init__(self, calibration_file_path, file_path, directory):
        self.calibration_parameter = basic_file_app.load_1d_array(calibration_file_path, 0, 0)
        print(self.calibration_parameter, 'used calibration_files')
        self.file_path = file_path
        self.directory = directory



    def calibrate_array(self):
        self.file_list = basic_file_app.get_file_list(self.file_path)
        my_calibration = calibration_analytical_from_array.CalibrateArray(self.calibration_parameter, self.directory)

        for x in self.file_list:
            my_array = basic_file_app.load_2d_array(self.file_path + x, 0, 1, 2)
            my_calibration.set_input_array(my_array, x)
            my_calibration.main()
            my_calibration.save_data("back: " + path_background + "RZP-structure:___" + rzp_structure_name, roi_list)

    def avg_of_stack(self):
        self.file_list= basic_file_app.get_file_list(self.directory)
        my_avg = basic_file_app.StackMeanValue(self.file_list, self.directory,1, 2, 4)
        my_result = my_avg.get_result()
        plt.figure(10)
        plt.plot(my_result[:,0],-np.log(my_result[:,1])+16, label = "my_avg")
        return my_result






def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else: os.mkdir(name)




path_background = "data/straylight_50ms/"
name_background = path_background
path_picture = "data/LT3250_50ms/"


#DEFINE ROI for EVAL and BACKGROUND
# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 303, 1437, 1632])
back_roi = ([1683, 0, 2048, 2000])

#RESULT-PATH - important for processing

create_result_directory("results_binned_"+str("LT3250_50ms"))
bin_path =  "results_binned_"+str("LT3250_50ms")




# px size in um, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
# is now given via read in txt - should look like this:
#rzp_structure_parameter = np.array([1.350e-02, 2.130e+00, 1.338e+03, 3.714e+00, 2.479e+03, 0.000e+00])

# SCALING PARAMETER FOR counts + HEADER DESCRIPTION
laser_gate_time_data = 50# ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZPA9-S3_" + str(laser_gate_time_data) + "ms"



# BACKGROUND MEAN FROM IMAGE STACK
#file_list_background = basic_image_app.get_file_list(path_background)
#batch_background = basic_image_app.ImageStackMeanValue(file_list_background, path_background)
#my_background = batch_background.average_stack()



#BIN AND PX-SHIFT CORRECTION:

# reference positions (px) for minimum in roi for px shift evaluation
reference_point_list = [615]
# path_binned_array_files to be opened for px-shifted arrays (usually excecution path for this python routine)
#Test = PxCorrectionOnStack(path_picture, reference_point_list,bin_path)
#Test.pre_process_stack()
#Test.px_shift()





# CALIBRATION ON BINNED SPECTRA

calibration_path = "calibration_files/20210707_calibration_RZP.txt"
cal_path = str("cal_")+ bin_path[14:]
create_result_directory(cal_path)
calibration = BatchCalibration(calibration_path, bin_path + "/", cal_path)
calibration.calibrate_array()
my_avg = calibration.avg_of_stack()


mylar_positions = basic_file_app.load_1d_array("calibration_files/NiO_L2_L3.txt", 0,0)

for x in mylar_positions:
    plt.figure(10)
    plt.vlines(x=x, ymin=-20, ymax=160, color = "m")
plt.xlim(840, 890)
plt.ylim(2,4)
plt.show()