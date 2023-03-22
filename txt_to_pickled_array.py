import numpy as np
import basic_file_app
import pickle

' file with lineouts as lines - .txt'

def open_txt_pickle_save_pickle(path, file_name, skip_rows, save_name):
    my_array = basic_file_app.load_all_columns_from_file(path + "/" + file_name, 0)
    my_array = np.array(my_array)
    pickle.dump(my_array, open(path+ "/ " + save_name + ".bin", "wb"))


def open_pickled_array(path, file_name):
    #with open(path + "/" + file_name, "rb") as f:
       #return pickle.load(f)
    my_array = pickle.load(path + "/" + file_name)
    return my_array



my_file = "pp_TiN_300s_10ms_8mJ_425delay_1_ALL_binned_y.txt"

my_path = "data/20221101/pp_TiN_300s_10ms_8mJ_425delayIntegratedSingleEvenB"
my_pickled_file = 0

open_txt_pickle_save_pickle(my_path, my_file, 0, my_file[:-4] )
my_bin_file = basic_file_app.get_bin_files(my_path)
print(my_bin_file)
open_pickled_array(my_path, my_bin_file)





