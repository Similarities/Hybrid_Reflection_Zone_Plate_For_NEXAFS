import numpy as np


def load_1d_array(file, column_1, skiprows):
    data = np.loadtxt(file, skiprows=skiprows, usecols=(column_1,))
    return data


def stack_arrays(array_1, array_2, axis):
    return np.stack((array_1, array_2), axis=axis)
