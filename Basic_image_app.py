import matplotlib.pyplot as plt
import numpy as np
import os
import imageio




def read_image(file):
    return plt.imread(file)

def read_32bit_tiff(file):
    return imageio.imread(file)


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

    def average_stack(self):
        for x in self.file_list:
            x = str(self.file_path + '/' + x)
            picture_x = read_32bit_tiff(x)
            self.result = self.result + picture_x

        self.result = self.result / (len(self.file_list))
        return self.result


class SingleImageOpen:
    def __init__(self, file_name, file_path):
        self.file_name = file_name
        self.file_path = file_path
        self.picture_array = np.empty([])



    def return_single_image(self):
        self.picture_array = read_32bit_tiff(str(self.file_path + '/' + self.file_name))
        return self.picture_array








testimage = SingleImageOpen("202100707_NiOLTm3150_50ms00090.tiff", "data/test_raw/")
#plt.imshow(testimage)
#plt.show()