import matplotlib.pyplot as plt
import numpy as np
import os
import imageio
import cv2





def read_image(file):
    return plt.imread(file)

def read_32bit_tiff(file):
    return imageio.imread(file)

def read_cv2_tiff(file):
    img = cv2.imread(file)



def get_file_list(path_picture):
    tif_files = []
    counter = 0
    for file in os.listdir(path_picture):
        print(file)
        try:
            if file.endswith(".tif"):
                tif_files.append(str(file))
                counter = counter + 1
            else:
                print("only other files found")
        except Exception as e:
            raise e
    return tif_files


def convert_32_bit(picture):
    return np.float32(picture)



class ImageStackMeanValue:

    def __init__(self, file_list, file_path):
        self.file_list = file_list
        self.file_path = file_path
        self.result = np.empty([])
        self.result = convert_32_bit(self.result)

    def average_stack(self):
        for x in self.file_list:
            x = str(self.file_path + '/' + x)
            picture_x = read_image(x)
            self.result = self.result + picture_x

        self.result = self.result / (len(self.file_list))
        return self.result


class SingleImageOpen:
    def __init__(self, file_name, file_path):
        self.file_name = file_name
        self.file_path = file_path
        self.picture_array = np.empty([])



    def return_single_image(self):
        self.picture_array = read_image(str(self.file_path + '/' + self.file_name))
        print(self.picture_array.dtype, "type of picture array")
        return self.picture_array








#plt.imshow(testimage)
#plt.show()