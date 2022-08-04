import matplotlib.pyplot as plt
import basic_file_app
import numpy as np
import os

PP = basic_file_app.load_1d_array("OD_result/ODDZnO_ppII429nBZnO_ppIII429nB.txt", 0, 1)


plt.figure(100)
plt.plot(PP, label = "ODD ZnO pp III II no back")

plt.xlabel("px")
plt.ylabel("i.a.u.")
#plt.xlim(500,800)
plt.legend()
save_pic = os.path.join("OD_result", "ODD_ZnO_IIandIIIpumped"+ ".png")
plt.savefig(save_pic, bbox_inches="tight", dpi=500)
plt.show()