import matplotlib.pyplot as plt
import basic_file_app
import numpy as np
import os


pathTi = "data/20220704_RS3_HG175cal/avg/20220704_RS3_HG175cal_avg.txt"
arrayTi = basic_file_app.load_2d_array(pathTi, 0, 2, 5)

pathTiN = "data/20220704_LS2HG_TiN_500ms409/avg/20220704_LS2HG_TiN_500ms409_avg_shorter.txt"
arrayTiN = basic_file_app.load_2d_array(pathTiN, 0, 2, 5)
print(len(arrayTiN))
print(len(arrayTi))

pathTiN2 = "data/20220704_LS2HG_TiN_300ms379/avg/20220704_LS2HG_TiN_300ms379_avg.txt"
arrayTiN2 = basic_file_app.load_2d_array(pathTiN2, 0, 2, 5)

plt.figure(1)
plt.plot(arrayTi[:, 0], (-np.log(arrayTi[:, 1])+2), marker=".", markersize=3, label= "Ti RS3 300ms")
plt.plot(arrayTiN[:, 0], -np.log(arrayTiN[:, 1]), marker=".", markersize=3, label= "Ti LS2 500ms")
plt.plot(arrayTiN2[:, 0], (-np.log(arrayTiN2[:, 1])-0.5), marker=".", markersize=3, label= "Ti LS2 300ms")
plt.xlabel("eV")
plt.ylabel("-log(signal) - const")
plt.xlim(300, 575)
plt.legend()

plt.figure(2)
plt.plot(arrayTi[:,0], -np.log(arrayTiN[:,1]/arrayTi[:,1]), marker=".", markersize=3, label= "Ti RS3 300ms vs TiN LS2 500ms" )
plt.xlabel("eV")
plt.ylabel("ODD")
plt.xlim(300, 575)
plt.legend()


plt.figure(2)
save_pic = os.path.join("20220704_Ti_TiN_OD" + ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)
plt.show()