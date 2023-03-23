import numpy as np
import matplotlib.pyplot as plt
import basic_file_app
import Richards_px_shift



my_lineouts= basic_file_app.load_all_columns_from_file("Integrated_Even20230309_NiO_II_O_edge_695_1/20230309_NiO_II_O_edge_69ALL_binned_y.txt", skiprows=0)
my_reference = my_lineouts[:,1]
my_lineouts = my_lineouts[:,:5]
print(my_lineouts.shape[1])

ShiftIt = Richards_px_shift.PixelShiftByCorrelationAndDeviation(30, 1420,
                                                                        my_reference, mode="same",
                                                                        correlation_method=True,
                                                                        general_method="deviation")


for x in range(0, my_lineouts.shape[1]):
    single_binned_spectra = my_lineouts[:, x]

    shift = ShiftIt.main(single_binned_spectra)


my_shifted_lineouts, my_shift_list = ShiftIt.return_result_spectra()


plt.figure(1)
plt.plot(my_shifted_lineouts)
print(my_lineouts)
plt.xlim(1420-300, 1420+300)

plt.show()


