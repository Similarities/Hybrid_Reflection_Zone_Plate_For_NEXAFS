import matplotlib.pyplot as plt
import numpy as np
import os


#import imageio
# import cv2


def read_image(file):
    x = plt.imread(file)
    plt.close(file)
    return x



def read_32bit_tiff(file):
    return imageio.imread(file)


#def read_cv2_tiff(file):
    img = cv2.imread(file)


def threshold_low_pass_cleaner(picture_array, threshold):
    picture_array[picture_array > threshold] = np.mean(picture_array[:, :])
    # plt.imshow(picture_array)
    # plt.show()
    return picture_array


def get_file_list(path_picture):
    tif_files = []
    counter = 0
    for file in os.listdir(path_picture):
        # print(file)
        try:
            if file.endswith(".tif"):
                tif_files.append(str(file))
                counter = counter + 1
            else:
                print("only other files found")
        except Exception as e:
            raise e
    return tif_files


def even_odd_lists(list):
    even_liste = []
    odd_liste = []
    for counter, value in enumerate(list):
        if counter % 2 == 0:
            even_liste.append(list[counter])
        else:
            odd_liste.append(list[counter])

    # print("even", even_liste)
    # print("odd", odd_liste)
    return even_liste, odd_liste

def even_odd_lists_string_sort(list):
    even_liste = []
    odd_liste = []
    counter = 0
    for x in list:
        print(x[-5:-4])
        if int(x[-5:-4]) % 2 == 0:
            even_liste.append(x)
        else:
            odd_liste.append(x)

    #print("even", even_liste)
    #print("odd", odd_liste)
    return even_liste, odd_liste

# toDo implement in Test
def test_for_doubles_in_list(list1, list2):
    for x in enumerate(list1):
        if x in enumerate(list2):
            print(x, "doubles")


def convert_32_bit(picture):
    return np.float32(picture)

def open_and_sum_image(picture):
    return np.sum(read_image(picture), axis = 0)


class ImageStackMeanValue:

    def __init__(self, file_list, file_path):
        self.file_list = file_list
        self.file_path = file_path
        self.result = np.zeros([])
        self.result = np.float64(self.result)

    def average_stack(self):
        for x in self.file_list:
            x = str(self.file_path + '/' + x)
            print(x)
            picture_x = read_image(x)
            self.result = np.float64(self.result + picture_x)
            picture_x = []
            self.overflow_64bit()

        self.result = (self.result / (len(self.file_list) + 1))
        return self.result

    def background_substration(self, background_array):
        self.result = self.result - background_array
        return self.result

    def integrate_mean_image(self):
        return np.sum(self.result, axis=0)

    # ToDo: make via np.mean - > avoid overflow
    def overflow_64bit(self):
        if (np.max(self.result) / (2 ** 64)) >= 1:
            print("64bit overflow in avg image!", np.max(self.result))


class SingleImageOpen:
    def __init__(self, file_name, file_path):
        self.file_name = file_name
        self.file_path = file_path
        self.picture_array = np.empty([])

    def return_single_image(self):
        self.picture_array = read_image(str(self.file_path + '/' + self.file_name))
        # print(self.picture_array.dtype, "type of picture array")
        return self.picture_array

# plt.imshow(testimage)
# plt.show()
