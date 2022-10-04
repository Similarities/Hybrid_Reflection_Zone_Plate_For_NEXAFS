import matplotlib.pyplot as plt
import basic_file_app
import numpy as np
import os



all_lineouts = basic_file_app.load_all_columns_from_file("data/20220818Alternating_Result/20220818_ZnO_pp_409_01IntegratedSingleBShiftedOdd/Shifted_spectra20220818_ZnO_pp_409_01_1_.txt",1)
all_lineouts = np.transpose(all_lineouts)
x=np.zeros([])
for counter, value in  enumerate (all_lineouts[20:40]):
    x = value
    plt.plot(x)
x = x/len(all_lineouts)
plt.plot(x)
plt.plot(np.mean(all_lineouts, axis = 0))


plt.show()