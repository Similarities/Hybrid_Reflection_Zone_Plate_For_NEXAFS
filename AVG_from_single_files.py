import basic_file_app
import numpy as np
import matplotlib.pyplot as plt
import os


path = "data/20220818_ZnO_pp_409_01IntegratedSingleEven/20220818_ZnO_pp_409_01_1ALL_binned_y.txt"
path2 = "data/20220818_ZnO_pp_409_01IntegratedSingleOdd/20220818_ZnO_pp_409_01_1ALL_binned_y.txt"

stack1 = basic_file_app.load_all_columns_from_file(path,0)
stack2 = basic_file_app.load_all_columns_from_file(path,0)

plt.plot(stack1, label = "1")
plt.plot(stack2, lable = "2")
plt.show()