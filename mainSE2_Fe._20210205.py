import matplotlib.pyplot as plt
import numpy as np
import Basic_Image_App


def load_2_d_array(file, column_1):
    data = np.loadtxt(file, skiprows=3, usecols=(column_1,))
    return data


# make sure the image-array (picture, background) is in 32bit
class ImagePreProcessing:

    def __init__(self, picture, picture_name, background, background_name):
        self.filename = picture_name
        self.picture = picture
        self.background = background
        self.background_name = background_name
        # x1, y1, x2, y2
        self.back_roi = ([905, 1748, 1521, 1918])
        self.binned_roi_y = np.empty([])
        self.x_axis = np.empty([])


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

    def background_substraction(self):
        for counter, x in enumerate(self.picture[0, ::]):
            self.picture[::, counter] = self.picture[::, counter] - self.background[::, counter]
        self.picture[self.picture < 0] = 0
        return self.picture

    def bin_in_y(self, roi_list):
        self.binned_roi_y = np.sum(self.picture[roi_list[1]:roi_list[-1], roi_list[0]: roi_list[2]], axis=0)
        self.x_axis = np.arange(0, roi_list[2] - roi_list[0])
        plt.figure(3)
        plt.imshow(self.picture[roi_list[1]:roi_list[-1], roi_list[0]: roi_list[2]])
        plt.colorbar()
        return self.binned_roi_y, self.x_axis

    def calibrate_x_axis(self, fit_coefficients):
        self.x_axis = np.linspace(0, 2048, 2048)
        for counter, value in enumerate(self.x_axis):
            self.x_axis[counter] = (fit_coefficients[0] * value ** 2) + fit_coefficients[1] * value + fit_coefficients[
                2]
        plt.figure(6)
        plt.plot(self.x_axis, self.binned_roi_y, label = self.filename[:-4], marker=".")
        plt.xlabel("nm")
        plt.ylabel('counts')
        return self.x_axis, self.binned_roi_y

    def plot_calibration_nm(self, lines):
        for x in lines:
            plt.figure(6)
            plt.vlines(x, ymin=0, ymax=1E7)

    def plot_calibration_eV(self, lines):
        for x in lines:
            x = self.convert_nm_to_electron_volt(x)
            plt.figure(7)
            plt.vlines(x, ymin= 0, ymax= 0.2E7, linewidth = 0.5)

    def plot_result_eV(self):
        self.x_axis[:] = self.convert_nm_to_electron_volt(self.x_axis[:])
        plt.figure(7)
        plt.plot(self.x_axis, self.binned_roi_y, label=self.filename[:-4], marker=".", ms=3)
        plt.xlabel('eV')
        plt.ylabel('counts')
        plt.legend()
        return self.x_axis

    def convert_nm_to_electron_volt(self, value_nm):
        planck_constant = 4.135667516 * 1E-15
        c = 299792458
        return planck_constant * c / (value_nm * 1E-9)

    def spectral_range(self):
        print(np.amax(self.x_axis), np.amin(self.x_axis), 'spectral range')


    def prepare_header(self, description):
        # insert header line and change index
        result = np.column_stack((self.x_axis, self.binned_roi_y))
        self.spectral_range()
        header_names = (['eV', 'counts'])
        names = (['file'+str(self.filename), 'back:'+str(self.background_name)])
        parameter_info = (
            ['description:', description])
        return np.vstack((parameter_info, names, header_names, result))

    def save_data(self, description):
        result = self.prepare_header(description)
        print('...saving:', self.filename[:-4] + description)
        plt.figure(7)
        plt.savefig(self.filename[:-4] + description + ".png", bbox_inches="tight", dpi=500)
        np.savetxt(self.filename[:-4] + '_calibrated' + ".txt", result, delimiter=' ',
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



class calibration_fit:
    def __init__(self, reference_points):
        self.reference_points = reference_points
        #print(reference_points)
        self.poly_coefficients = self.fit_refernce_points()
        self.poly_reciproce = self.fit_reciproce()
        #print(self.poly_coefficients, 'coefficients')

    def fit_refernce_points(self):
        return np.polyfit(self.reference_points[:, 1], self.reference_points[:, 0], 2)

    def fit_reciproce(self):
        return np.polyfit(self.reference_points[:, 0], self.reference_points[:, 1], 2)

    def give_fit(self):
        return self.poly_coefficients

    def compare_fit(self):
        x_axis = np.linspace(np.min(self.reference_points[:, 1]), np.max(self.reference_points[:, 1]), 400)
        fit_y = np.linspace(np.min(self.reference_points[:, 1]), np.max(self.reference_points[:, 1]), 400)
        for counter, value in enumerate(x_axis):
            fit_y[counter] = self.poly_coefficients[-1] + self.poly_coefficients[1] * x_axis[counter] + \
                             self.poly_coefficients[0] * x_axis[counter] ** 2

        plt.figure(5)
        plt.scatter(self.reference_points[:, 1], self.reference_points[:, 0])
        plt.plot(x_axis, fit_y)
        plt.plot()




path_background = "20210205/StrayLight_1x945ms_2s"
name_background = path_background
path_picture = "20210205/test"
#name_picture = "210205_PM012509.tif"

roi_list = ([0, 220, 2048, 1432])

reference = np.zeros([7, 2])
reference[:, 0] = load_2_d_array("Fe_lines_S2.txt", 1)
reference[:, 1] = load_2_d_array("Fe_lines_S2.txt", 2)

emission_lines = np.zeros([7,2])
emission_lines[:,0] = load_2_d_array("Fe_lines_S2.txt", 1)

S3_FE_reference = calibration_fit(reference)
S3_FE_reference.compare_fit()
my_fit_coefficients = S3_FE_reference.give_fit()


#create input pictures

file_list_background = Basic_Image_App.get_file_list(path_background)
batch_background = Basic_Image_App.ImageStackMeanValue(file_list_background, path_background)
my_background = batch_background.average_stack()


def batch_folder_in_single_picture():
    my_pictures = Basic_Image_App.get_file_list(path_picture)
    print(my_pictures)
    for x in my_pictures:
        open_picture = Basic_Image_App.SingleImageOpen(x, path_picture)
        my_picture = open_picture.return_single_image()
        Test = ImagePreProcessing(my_picture, x, my_background, name_background[:-4])
        # Test.view_control()
        Test.reference_scaling()
        Test.background_substraction()
        Test.bin_in_y(roi_list)
        Test.calibrate_x_axis(my_fit_coefficients)
        #Test.plot_calibration(background[:, 0])
        Test.plot_result_eV()
        Test.plot_calibration_eV(emission_lines[:, 0])
        Test.save_data('testS2')



batch_folder_in_single_picture()
plt.show()


