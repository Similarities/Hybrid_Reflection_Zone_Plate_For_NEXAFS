import matplotlib.pyplot as plt
import basic_file_app
import numpy as np
import os
import px_shift_on_picture_array_rolling

PP = basic_file_app.load_1d_array("AVG20220815_ZnOIIIevenThres/avg20220815_ZnOIIIevenThreshold.txt", 0, 1)
UP = basic_file_app.load_1d_array("AVG20220815_ZnOIIIevenThres/avg20220815_ZnOIIIoddThreshold.txt", 0,1)


shift_avg = px_shift_on_picture_array_rolling.PixelShift( PP,[145], "min")
Pis = shift_avg.evaluate_shift_for_input_array(UP, 11)
#shift_shifted = px_shift_on_picture_array_rolling.PixelShift(pii, [102], "min")
#piii = shift_shifted.evaluate_shift_for_input_array(piii,111)

plt.figure(100)
plt.plot(-np.log(PP/UP), label = "ODD avg shift on single not on avg")
plt.plot(-np.log(PP/Pis), label = "ODD avg shift on single and on avg")
plt.title("ODD ZnO even odd 419 III")
plt.xlabel("px")
plt.ylabel("i.a.u.")
#plt.xlim(50,2000)
plt.ylim(-0.01, 0.01)
plt.legend()

def create_result_directory(name):
    if os.path.isdir(name):
        pass
    else:
        os.mkdir(name)

create_result_directory("Comparison_avg_stack")
save_pic = os.path.join("Comparison_avg_stack", "ODDZnO_419III_vs"+ ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)
plt.show()