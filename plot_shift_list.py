import numpy as np
import matplotlib.pyplot as plt
import os
import basic_file_app
import basic_image_app


shift_409pp = basic_file_app.load_1d_array("data/20220818Alternating_Result/20220818_ZnO_pp_409_01IntegratedSinglenoBShiftedOdd/Shiftlist.txt", 0, 1)
name_1 = "409"
shift_419pp = basic_file_app.load_1d_array("data/20220818Alternating_Result/20220818_ZnO_pp_419_01IntegratedSinglenoBShiftedOdd/Shiftlist.txt", 0, 1)
name_2 = "419"
shift_429pp = basic_file_app.load_1d_array("data/20220818Alternating_Result/20220818_ZnO_pp_429_01IntegratedSinglenoBShiftedOdd/Shiftlist.txt", 0, 1)
name_3 = "429"


#distribution_fuction pxshift
def count_number_of_events(liste, name, symbol, color):


    y_pos = np.zeros([int(np.max(liste))+1])
    y_neg = np.zeros([int(np.min(liste)*-1)+1])

    liste.astype(int)
    for x in liste:
        if x >= 0:
            x=int(x)
            y_pos[x] = y_pos[x] + 1
            print(x, y_pos[x])
        else:

            x=int(x)

            y_neg[x] = y_neg[x] + 1
            print(x, y_neg[x])


    x_axis_pos = np.linspace(len(y_pos), 0, len(y_pos))
    x_axis_neg = np.linspace(-1, -len(y_neg), len(y_neg))


    plt.figure(2)
    plt.title("pointing distribution")
    plt.scatter(x = x_axis_pos, y = y_pos,  label = name, alpha = 0.5, marker= symbol, color = color)
    plt.scatter(x = x_axis_neg, y = y_neg, alpha = 0.5, marker = symbol, color = color)
    plt.xlabel("px")
    plt.ylabel("counted events of shift")
    plt.legend()



count_number_of_events(shift_429pp, "429", "*", "b")
count_number_of_events(shift_419pp, "419","+", "m")
count_number_of_events(shift_409pp, "409",".", "y")
save_pic = os.path.join("data/20220818Alternating_Result", "Nexafs_alternating_ZnO20220818_shiftdistribution_noBack"+ ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)

plt.show()