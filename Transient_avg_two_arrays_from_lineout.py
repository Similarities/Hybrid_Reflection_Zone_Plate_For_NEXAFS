import matplotlib.pyplot as plt
import numpy as np
import basic_file_app
import px_shift_on_picture_array_rolling
import os
import time







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

path_lineout_array_1= "data/20221101/pp_TiN_300s_10ms_8mJ_460delayIntegratedSingleEvenB/pp_TiN_300s_10ms_8mJ_460delay_1_ALL_binned_y.txt"
path_lineout_array_2= "data/20221101/pp_TiN_300s_10ms_8mJ_460delayIntegratedSingleBODD/pp_TiN_300s_10ms_8mJ_460delay_1_ALL_binned_y.txt"
name_picture = "TiN10ms_460_even"
name_reference = name_picture[:-4] +"odd"



#even_lineout_array = basic_file_app.load_all_columns_from_file(path_lineout_array_1,0)
#odd_lineout_array = basic_file_app.load_all_columns_from_file(path_lineout_array_2, 0)






# ToDo. set roi range spectrum and roi range background
# DEFINE ROI for EVAL and BACKGROUND
# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 57, 2000, 188])
back_roi = ([0, 0, 0, 0])

# ToDo change result folder binned spectra name
# RESULT-PATH


# ToDo change result avg and od folder
result_folder = name_picture[:-4]+ "AVG_not_Shifted"
create_result_directory(result_folder)









average_image = basic_file_app.AvgOverAxis1(path_lineout_array_1, 0)
image_avg = average_image.average_stack()
# image_avg = image_avg - my_background_lineout[:-4]
np.savetxt(result_folder + "/AvgB" + name_picture + ".txt", image_avg, delimiter='',
           header='string', comments='',
           fmt='%s')

avg_for_reference = basic_file_app.AvgOverAxis1(path_lineout_array_2, 0)
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


reference_point_list = [1688]

shift_it = PxShiftOnArrays(image_avg, reference_avg, reference_point_list, "min", 4)
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
