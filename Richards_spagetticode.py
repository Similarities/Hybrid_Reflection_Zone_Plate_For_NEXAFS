# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 17:59:46 2022

@author: Richard
"""
from scipy import signal
from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt
import basic_file_app


def gaus1d(I, xc, FWHM, x):
    w = FWHM / np.sqrt(np.log(4))
    return I / (w * np.sqrt(np.pi / 2)) * np.exp(-2 * (x - xc) ** 2 / w ** 2)


def ableitung_central(x):
    '''


    Parameters
    ----------
    x : 1d array
        Array to take derivation of

    Returns
    -------
    dyc : 1d array
        Derivation of x

    '''

    dyc = [0.0] * len(x)
    dyc[0] = (x[0] - x[1]) / 1
    for i in range(1, len(x) - 1):
        dyc[i] = (x[i + 1] - x[i - 1]) / (2)
    dyc[-1] = (x[-1] - x[-2]) / (1)
    dyc = np.array(dyc)
    return dyc


def calc_corr_spectrum_start(spectrum_start, corr_corr=False):
    '''


    Parameters
    ----------
    spectrum_start : 1d array
        Spectrum on which all other spectra are shifted on. Normally the first
        spectrum of the measurement series or some kind of representative spectrum.

    corr_corr : Boolean
        If "True" the correlation of the correlation is used

    Returns
    -------
    corr_spectrum_start : 1d array
        Correlation of "spectrum_start" with itself, later used for single spectra shift

    corr_corr_spectrum_start : 1d array
        Correlation of "corr_spectrum_start" with itself

    '''

    corr_spectrum_start = signal.correlate(spectrum_start, spectrum_start, mode=mode)
    if corr_corr == True:
        corr_corr_spectrum_start = signal.correlate(corr_spectrum_start, corr_spectrum_start, mode=mode)
    else:
        corr_corr_spectrum_start = -1
    return corr_spectrum_start, corr_corr_spectrum_start


def correlation_spectra(spectrum_start, spectrum, spectrum_part1, spectrum_part_2, corr_spectrum_start,
                        corr_corr=False):
    '''


    Parameters
    ----------
    spectrum_start : 1d array
        Spectrum on which all other spectra are shifted on. Normally the first
        spectrum of the measurement series or some kind of representative spectrum

    spectrum : 1d array
        Spectrum which is shifted on the spectrum_start. Typically only the
        absorption edge region is used, defined by "spectrum_part1" and
        "spectrum_part2"

    spectrum_part1: integer
        start index for spectrum, to select only the absorption edge region

    spectrum_part_2: integer
         stop index for spectrum, to select only the absorption edge region

    corr_spectrum_start : 1d array

    corr_corr : Bolean
        Calculates the correlation of the correlation


    Returns
    -------
    corr_spectrum : 1d array
        Correlation of the current "spectrum" with "spectrum_start"

    '''
    spectrum = spectrum[spectrum_part1:spectrum_part_2]

    corr_spectrum = signal.correlate(spectrum_start, spectrum, mode=mode)
    if corr_corr is False:
        pass
    else:
        corr_spectrum = signal.correlate(corr_spectrum_start, corr_spectrum, mode=mode)
    return corr_spectrum


# @jit
def fit_linear(spectrum, spectrum_start, spectrum_part1, spectrum_part_2):
    '''
    Idea is to calculate the quadratic deviation from "spectrum" an "spectrum_start"
    spectrum_part1 and spectrum_part_2 decides which part of the spectrum is used
    spectrum_start has the window length given by spectrum_part1 and spectrum_part_2.
    This window is shifted in 1 px steps over the whole "spectrum_start" spectrum
    and for every window position the sum of the quadratic deviation is calculated
    between "spectrum" and "spectrum_start". The Minimum deviation is the best shift.

    Parameters
    ----------
    spectrum_start : 1d array
        Spectrum on which all other spectra are shifted on. Normally the first
        spectrum of the measurement series or some kind of representative spectrum

    spectrum : 1d array
        Spectrum which is shifted on the spectrum_start. Typically only the
        absorption edge region is used, defined by "spectrum_part1" and
        "spectrum_part2"

    spectrum_part1: integer
        start index for spectrum, to select only the absorption edge region

    spectrum_part_2: integer
         stop index for spectrum, to select only the absorption edge region

    Returns
    -------
    abweichung_list : 1d list
        Sum of the quadratic deviation between spectrum und spectrum_start
        scanned over the length of "spectrum_start"

    '''

    length_window = spectrum_part_2 - spectrum_part1
    length = len(spectrum_start)
    s = spectrum[spectrum_part1:spectrum_part_2]
    abweichung_list = []
    range_shift = length - length_window
    for shift in range(range_shift):
        abweichung = np.sum((s - spectrum_start[shift:shift + length_window]) ** 2)
        abweichung_list.append(abweichung)
    return abweichung_list


spectrum_part1 = 1350
spectrum_part_2 = 1400
spectrumcorr_spectrum = 101
smooth_spectra = 1  # window size of smooth function
order_poly_smooth_spectra = 3  # polynomial order of smooth function
corr_corr = True  # decide if you want correlation of the correlation
Ableitung = True  # sometimes the resuluts are better when the deviation
# from the spectrum is taken
mode = 'same'  # correlation mode
xc = 40  # center gaussian start spectrum
xc_spectrum = 40  # center gaussian other spectra
FWHM = 20  # FWHM gaussian

array_1 = basic_file_app.load_1d_array("data/Result20230309_NiO_II_O_edge_620_1/AVG20230309_NiO_II_O_edge_620_1_even.txt",0,1)
array_2 = basic_file_app.load_1d_array("data/Result20230309_NiO_II_O_edge_620_1/AVG20230309_NiO_II_O_edge_620_1odd.txt",0,1)

spectrum_start = array_1[spectrum_part1:spectrum_part_2]
spectrum = array_2

Figure = plt.figure()
plt.xlabel('x-axis / pixel')
plt.ylabel('Intensity')
plt.title('Spectra')
plt.plot(spectrum_start, label='spectrum start ')
plt.plot(spectrum[spectrum_part1:spectrum_part_2], label='spectrum')
plt.legend()

if Ableitung == True:
    spectrum_start = ableitung_central(spectrum_start)

if Ableitung == True:
    spectrum = ableitung_central(spectrum)

# smooth spectra to decrese noise. Needed for low exposure Images
if smooth_spectra > order_poly_smooth_spectra:
    spectrum_start = savgol_filter(spectrum_start, smooth_spectra, order_poly_smooth_spectra)
else:
    pass

corr_spectrum_start, corr_corr_spectrum_start = calc_corr_spectrum_start(spectrum_start, corr_corr)
# calculate the correlation

if corr_corr == True:
    max_corr_start = np.argmax(corr_corr_spectrum_start)
else:
    max_corr_start = np.argmax(corr_spectrum_start)  # Maximum correlation
# of "spectrum_start" with itself, if "corr_corr" = True it is the correlation of
# the correlation


spectrum_correlation = correlation_spectra(spectrum_start, spectrum, spectrum_part1, spectrum_part_2,
                                           corr_spectrum_start, corr_corr)
# correlation of the spectrum with the start spectrum
maximum_corr_spectrum = max_corr_start - (np.argmax(spectrum_correlation)) - spectrum_part1
print(maximum_corr_spectrum)

Figure = plt.figure()
plt.xlabel('x-axis / pixel')
plt.ylabel('Intensity')
plt.title('Correlation')
plt.plot(corr_spectrum_start, label='corr_spectrum_start ')
plt.plot(spectrum_correlation, label='spectrum_correlation')
plt.legend()

'''calculation of the quadratic deviation from a small spectrum part'''
deviation = fit_linear(spectrum, spectrum_start, spectrum_part1, spectrum_part_2)

Figure = plt.figure()
plt.xlabel('x-axis / pixel')
plt.ylabel('quadratic deviation')
plt.title('sum of quadratic deviation between spectrum and spectrum_start')
plt.plot(deviation)
plt.legend()

plt.figure(10)
plt.plot(array_1, label = "ref")
plt.plot(array_2, label = "spectrum")
array_new = np.roll(array_2, max_corr_start-np.argmax(spectrum_correlation))
print(np.argmax(spectrum_correlation), max_corr_start)
plt.plot(array_new, label = "shifted")
plt.legend()

plt.show()