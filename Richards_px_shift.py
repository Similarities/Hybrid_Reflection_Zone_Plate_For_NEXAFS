# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 17:59:46 2022

@author: Richard && modded by Similarities
"""
from scipy import signal
from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt
import basic_file_app


class PixelShiftByCorrelationAndDeviation:
    def __init__(self, window_size, start_position, reference_array, mode, correlation_method, general_method):
        self.window_size = window_size
        self.start_position = start_position
        self.reference_array = reference_array
        self.shifted_spectra= []
        self.shifted_spectra.append(self.reference_array)
        self.plot_result(self.reference_array, "ref", 33, "original")
        self.plot_result(self.reference_array, "ref", 43, "shifted")
        self.general_method = general_method #choose "deviation" for correlation or "something" for using the spectrum
        self.mode = mode #"same" - comes from package
        self.correlation_method = correlation_method # True: correlation of correlation, False: correlation only
        self.reference_corr, self.reference_corr_of_corr = self.calc_corr_spectrum_start()
        self.shift_list = []
        self.shifted_spectrum = []

    def main(self, array_in):
        self.plot_result(array_in, "unshifted", 33, "unshifted")
        if self.general_method == "deviation":
            self.reference_array = self.ableitung_central(self.reference_array)
            array_in_corr = self.ableitung_central(array_in)

        if self.correlation_method == True:
            max_corr_start = np.argmax(self.reference_corr_of_corr)
        else:
            max_corr_start = np.argmax(self.reference_corr)  # Maximum correlation
        # of "spectrum_start" with itself, if "corr_corr" = True it is the correlation of
        # the correlation

        spectrum_correlation = self.correlation_spectra(array_in_corr)
        # correlation of the spectrum with the start spectrum
        #maximum_corr_spectrum = max_corr_start - (self.start_position)- (np.argmax(spectrum_correlation)) #- self.start_position
        maximum_corr_spectrum =(np.argmax(spectrum_correlation))
        print("shift is:", maximum_corr_spectrum, "max corr start", max_corr_start, "argmax", np.argmax(spectrum_correlation))
        self.shift_it(maximum_corr_spectrum, array_in)
        return self.shifted_spectrum



    def shift_it(self, shift, array_in):
        self.shifted_spectrum = np.roll(array_in, shift)
        self.shift_list.append(shift)
        self.shifted_spectra.append(self.shifted_spectrum)


    def plot_result(self, array, name, figure_number, title):
        plt.figure(figure_number)
        plt.plot(array, label= name)
        plt.title(title)
        #plt.legend()
        plt.xlim(self.start_position-300, self.start_position+300)

    def return_result_shift(self):
        return self.shift_list

    def ableitung_central(self, x):
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

    def calc_corr_spectrum_start(self):
        '''
        ----------
        Returns
        -------
        corr_spectrum_start : 1d array
                  calculates correlation of reference spectrum (1D array) with itself, used
                  for px shift later on other arrays

        corr_corr_spectrum_start : 1d array
            Correlation of "corr_spectrum_start" with itself
        '''

        corr_spectrum_start = signal.correlate(self.reference_array[self.start_position:self.start_position+self.window_size], self.reference_array[self.start_position:self.start_position+self.window_size], mode=self.mode)

        if self.correlation_method == True:
            print("here we go for double correlation")
            corr_corr_spectrum_start = signal.correlate(corr_spectrum_start, corr_spectrum_start, mode=self.mode)
        else:
            corr_corr_spectrum_start = -1
        return corr_spectrum_start, corr_corr_spectrum_start

    def correlation_spectra(self, spectrum):
        '''
        Parameters
        ----------
        takes reference spectrum in

        spectrum : 1d array
            Spectrum which is shifted on reference spectrum. Typically only the
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
        spectrum = spectrum[self.start_position: self.start_position+self.window_size]

        corr_spectrum = signal.correlate(self.reference_array, spectrum, mode=self.mode)
        if self.correlation_method is False:
            pass
        else:
            corr_spectrum = signal.correlate(self.reference_corr, corr_spectrum, mode=self.mode)
        return corr_spectrum

    def fit_linear(self, spectrum):
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
        #ToDo what is shift shift ? and where da fuck is now the usual spectrum
        length = len(self.reference_array)
        s = spectrum[self.start_position:self.start_position+self.window_size]
        abweichung_list = []
        range_shift = length - self.window_size
        for shift in range(range_shift):
            abweichung = np.sum((s - self.reference_array[shift:shift + self.window_size]) ** 2)
            abweichung_list.append(abweichung)
        return abweichung_list








