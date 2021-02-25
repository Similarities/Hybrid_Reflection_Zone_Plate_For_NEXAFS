import matplotlib.pyplot as plt
import numpy as np
import Basic_Image_App
import Basic_File_App
import math
import plotFilter


class CompareAlignmentStructure:
    def __init__(self, path1):
        self.name = path1[0:2]
        self.array_1, self.name_1 = self.load_image(path1)
        self.line_out = np.empty([])


    def load_image(self, path_file):
        array = Basic_Image_App.read_image(path_file)
        array = Basic_Image_App.convert_32_bit(array)
        return array, path_file[0:3]

    def extract_roi(self, roi_list):
        array_sub = self.array_1[roi_list[2]:roi_list[3], roi_list[0]:roi_list[1]]
        plt.figure(0)
        plt.imshow(array_sub)
        self.array_1 = array_sub
        return self.array_1

    def sum_over_y(self):
        self.line_out = np.sum(self.array_1, axis = 0)
        x_axis = np.arange(0, 2048)
        return self.line_out, x_axis


    def scale_and_plot_lineout(self, scale):
        self.line_out, x_axis = self.sum_over_y()
        self.scale_counts(scale)
        plt.figure(2)
        plt.plot(x_axis, self.line_out, label = self.name + "x:" + str(scale), alpha = 0.7)
        plt.xlabel = "px"
        plt.ylabel = "counts"
        plt.legend()

    def scale_counts(self, scaling):
        self.line_out = Basic_File_App.constant_array_scaling(self.line_out, scaling)
        return self.line_out




file_1 = "S1/210205_PM023034.tif"
roi_1 = np.array([0, 2052, 135, 160])

file_2 = "S2/210205_PM021419.tif"
roi_2 = np.array([0, 2052, 130, 200])

file_3 = "S3/210205_PM012548.tif"
roi_3 =  np.array([0, 2052, 140, 170])

S3_structure = CompareAlignmentStructure(file_3)
S3_structure.extract_roi(roi_3)
S3_structure.scale_and_plot_lineout(0.6)

S2_structure = CompareAlignmentStructure(file_2)
S2_structure.extract_roi(roi_2)
S2_structure.scale_and_plot_lineout(1)

S1_structure = CompareAlignmentStructure(file_1)
S1_structure.extract_roi(roi_1)
S1_structure.scale_and_plot_lineout(1)

plt.figure(2)
plt.savefig('compare_alignment_structures'+".png", bbox_inches="tight", dpi=500)

plt.show()

