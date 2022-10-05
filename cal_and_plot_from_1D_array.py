import matplotlib.pyplot as plt
import numpy as np
import basic_file_app
import px_shift_on_picture_array_rolling
import os
import calibration_analytical_from_1Darray



class PxShiftOnArrays:
    def __init__(self, avg_picture, avg_reference, reference_point, method, plot_number):
        self.avg_picture = avg_picture
        self.avg_reference = avg_reference
        self.reference_point = reference_point
        self.method = method
        self.plot_number = plot_number

    def set_new_arrays(self, array_picture, array_reference):
        self.avg_picture = array_picture
        self.avg_reference = array_reference
        return self.avg_reference, self.avg_picture

    def px_shift_both(self):
        evaluate_shift = px_shift_on_picture_array_rolling.PixelShift(self.avg_picture, self.reference_point,
                                                                      self.method)
        self.avg_reference, shift = evaluate_shift.evaluate_shift_for_input_array(self.avg_reference, self.plot_number)
        #plt.show()
        return self.avg_reference



    def x_binning(self, array_in):
        binned_spectra = np.zeros([int(round(len(array_in/2),0))+1])
        for counter, value in enumerate(array_in):
            if counter %2 == 0:
                binned_spectra[int(round(counter/2,0))] = array_in[counter-1]+array_in[counter]
        plt.figure(1111)
        plt.plot(binned_spectra)
        return binned_spectra

    def set_reference_point(self, reference):
        self.reference_point = reference
        return self.reference_point








path1_1 = "TwoFolder20220926_resultFFTshifted_on_StackBdark/AvgBTiN_50ms_03.txt"
path_1 = "data/TwoFolder20220926_resultFFTshifted_on_StackBdark/AvgBW_50ms_02.txt"


name1 = "TiN on Si "
array_1 = basic_file_app.load_1d_array(path_1, 0, 1)
array1_1 = basic_file_app.load_1d_array(path1_1, 0,1)
shift_it = PxShiftOnArrays(array_1, array1_1, [1647], "min", 4)
#ToDo: if you want to norm one of the spectras to the other here give a range for max evaluation (choose a peak)
#my_shifte_reference = shift_it.norm_to_maximum_in_range(1725, 1740)
array1_1 = shift_it.px_shift_both()
#array_1 = shift_it.x_binning(array_1)
#array1_1 = shift_it.x_binning(array1_1)
shift_it.set_new_arrays(array_1, array1_1)

my_od1 = -np.log((array1_1[:]) / (array_1[:]))

" calibrate first set of data:"
calibration_file = "calibration_files/20220926_calibration_S2.txt"

calibration= basic_file_app.load_all_columns_from_file(calibration_file, 0)
my_calibration = calibration_analytical_from_1Darray.CalibrateArray(calibration, "data")
my_calibration.set_input_array(my_od1, "AvgBTiN_50ms.txt", True)
#my_calibration.main()
#calibration[3] = calibration[3] -0.005
#my_calibration.change_calibration_parameter(calibration)
my_calibratedod1 = my_calibration.main()





path_2 = "data/TwoFolder20220914_resultFFTshifted_on_StackBdark/AvgBW_100ms_02.txt"
path_2_1 = "data/TwoFolder20220914_resultFFTshifted_on_StackBdark/AvgBTi_100ms_03.txt"

name2 = "Ti on Si"
array_2 = basic_file_app.load_1d_array(path_2, 0, 1)
array_2_1 = basic_file_app.load_1d_array(path_2_1, 0, 1)
shift_it.set_new_arrays(array_2, array_2_1)
array_2_1 = shift_it.px_shift_both()
#array_2 = shift_it.x_binning(array_2)
#array_2_1 = shift_it.x_binning(array_2_1)

shift_it.set_new_arrays(array_2, array_2_1)

my_od2 = -np.log((array_2_1[:]) / (array_2[:]))


calibration_file_2 = "calibration_files/20220914_calibration_S2.txt"
calibration_2 = basic_file_app.load_1d_array(calibration_file_2, 0,0)
my_calibration.change_calibration_parameter(calibration_2)
my_calibration.set_input_array(my_od2, "AvgBTi_100ms", True)

#my_calibratedod2 = my_calibration.main()
#calibration_2[3] = calibration_2[3] -0.005
#my_calibration.change_calibration_parameter(calibration_2)
my_calibratedod2 = my_calibration.main()

'reference_lines on calibration plot of calibration_analytical_from_1Darray.py'
plt.figure(2)
plt.axvline(x = 398.4, color = 'b' )
plt.axvline(x = 401., color = 'b' )
plt.axvline(x = 409, color = 'b' )
plt.axvline(x = 452.7, color = 'c' )
plt.axvline(x = 458.4, color = 'c' )
plt.axvline(x = 460.1, color = 'c' )

plt.axvline(x = 540, color = 'r' )
plt.axvline(x = 532.9, color = 'r' )
plt.axvline(x = 535.4, color = 'r' )
plt.legend()



plt.figure(112)
plt.title("Nexafs Ti and TiN on Si")

plt.plot(my_calibratedod1[:,0], my_calibratedod1[:,1]-0.11, label = name1, alpha = 0.5, marker = ".", markersize = "0.5", color = "m" )

plt.plot(my_calibratedod2[:,0], my_calibratedod2[:,1]-1.165, label = name2, alpha = 0.5, marker = ".", markersize = "0.5", color="b")
plt.xlabel("energy [eV]")
plt.ylabel("ODD")
plt.xlim(375, 519)
plt.legend()

save_pic = os.path.join("data", "20220914_26_Ti_TiN_nexfas"+ ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)

plt.legend()






plt.show()