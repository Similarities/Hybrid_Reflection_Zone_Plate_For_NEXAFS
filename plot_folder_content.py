import matplotlib.pyplot as plt
import basic_file_app
import numpy as np
import px_shift_on_picture_array_rolling
import os


def plot_them_all(path, column_x, column_y, skip_rows):
    file_list = basic_file_app.get_file_list(path)
    for x in file_list:
        array = basic_file_app.load_2d_array(path + '/' + x, column_x, column_y, skip_rows)

        plt.figure(1)
        plt.plot(array[:, 0], -np.log(array[:, 1]) + 14, marker=".", markersize=3)
        plt.xlabel("eV")
        plt.ylabel("-log(signal) - const")
        plt.legend()

    plt.show()


def plot_avg_of_folder(path, column_x, column_y, skip_rows, file_list):
    make_avg = basic_file_app.StackMeanValue(file_list, path, column_x, column_y, skip_rows)
    my_avg_y = make_avg.return_result()
    my_avg_y[:,1] = np.log(1/my_avg_y[:,1])
    plt.figure(1)
    plt.plot(my_avg_y[:, 0], my_avg_y[:, 1], marker=".", markersize=3)
    plt.xlabel("eV")
    plt.ylabel("-log(signal) - const")
    plt.legend()


    array_y_all = make_avg.return_y_stack()
    print(len(array_y_all))
    array_x = my_avg_y[:, 0]
    return array_x, array_y_all, my_avg_y


def norm_od_to_one_and_save(array_in, savename, dir, diff):
    array_work = array_in
    array_work[:,1] = array_work[:,1]-diff
    maximum = np.max(array_work[:, 1])
    array_work[:, 1] = array_work[:, 1]/ maximum
    print(maximum)
    save_name = os.path.join(dir, "Normed" + savename[:-4] + ".txt")
    np.savetxt(save_name, array_work, delimiter=' ')
    return array_work

path1 = "data/RSI_Paper_To_NAS/20210714/selection_shots/cal__LT3200_20_msS3best"
file_list1 = basic_file_app.get_file_list(path1)
path2 = "data/RSI_Paper_To_NAS/20210714/selection_shots/cal__LT3200_50ms/40x"
path3 = "data/RSI_Paper_To_NAS/20210714/selection_shots/cal__LT3200_100ms/20x"

array_x, array_y_all, avg_y_20ms = plot_avg_of_folder(path1, 1, 2, 6, file_list1)
file_list2 = basic_file_app.get_file_list(path2)
print(file_list2)
array_x2, array_y_all2, avg_y_50ms = plot_avg_of_folder(path2, 1, 2, 6, file_list2)

file_list3 = basic_file_app.get_file_list(path3)
array_x3, array_y_all3, avg_y_100ms = plot_avg_of_folder(path3, 1, 2, 6, file_list3)



normed1 = norm_od_to_one_and_save(avg_y_20ms, "cal__LT3180_20ms_avg_", "data", -13.70)
normed2 = norm_od_to_one_and_save(avg_y_50ms, "cal__LT3180_50ms_avg_", "data",-13.5)
normed3 = norm_od_to_one_and_save(avg_y_100ms, "cal__LT3180_100ms_avg_", "data",-13.4)
##
plt.figure(111)
plt.plot(array_x3, normed3[:,1], label="10 shots NiO")
plt.plot(array_x2, normed2[:,1], label="5 shots NiO")
plt.plot(array_x, normed1[:,1], label="2 shots NiO")
plt.ylabel("absorption [i.u.a.]")
plt.xlabel("energy in eV")
plt.legend()
plt.xlim(840, 890)
save_pic = os.path.join("data", "plotNiO31200_20210707" + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)
plt.show()

# plt.ylim(-1, 2.5)


