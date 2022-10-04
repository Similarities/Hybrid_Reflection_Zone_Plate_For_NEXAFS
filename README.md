# Hybrid Reflection Zone Plate Evaluation
! work in progress not yet finished !

RZP serve as novel high efficient and high resolving spectral dispersive optic for Soft-Xray range, in this case in reflection geometry. 
Resolution, angle etc. depends on the imprinted fresnel structure on the surface of the RZP. As diffractive optic the RZP can be used for spectroscopy
and in this case here for NEXAFS (near edge X-ray absorption fine structure, see: https://en.wikipedia.org/wiki/X-ray_absorption_near_edge_structure). Soft-Xray photons can be generated via a laser plasma source, when an intense
laser is focused on solid material, or via high harmonic generation for gaseous targets. 
This script is meant to evaluate novel hybrid RZP optics: RZP with a bent substrate - enabling a wide spectrally focused range in
the soft-Xray. The spectral range depends on the RZP structural parameter and commonly a RZP optic consists of different
structures for different energy ranges. The novel hybrid RZP enables a high efficiency with retaining one dimension for
imaging purposes and a spectrally focused range with a high resolution of up to 200eV. This script results from a R&D project with NOB optics Berlin
more information about the optics can be found here: https://www.nanooptics-berlin.com/reflection-zone-plates .
The RZP optic was used with a CMOS (see: https://en.wikipedia.org/wiki/Active-pixel_sensor) detection device allowing data aquisition of up to 100 images per second (single laser
shot aquisition with 100Hz laser repetion rate with roi < 1000 px in y, 2048px in x). In comparison to Nexafs at synchrotron - the laser plasma source (and HHG)
enables instantaneous the aquisition of a full Nexafs spectrum within one measurement and spectrally generates high photon fluxes 
in the range 150eV- 1500eV (LPP, HHG < 600eV commonly). In combination with the Cmos detector
and the needs of statistical accuracy - a large amount (some 1000) images at 
16bit tiff are aquired. Hence, the evaluation method here was optimized (within some limits) to handle such image stacks. 
As the laser based Soft-Xray source is suffering from shot - to - shot pointing, post-processing methods are important in order reach
the highest possible resolution. 

This script is work in progress, but covers the whole package for the Nexafs evaluation using hybrid RZP optics:
- stack evaluation for picture and reference picture 
- alternating stack evaluation for e.g. pump- probe methods (integration ... )
- background substraction methods
- different pointing correction methods within stacks and between two stacks (e.g. pumped to non pumped)
- avg evalution on stack
- calibration via fits (needs then reference positions in the stack)
- calibration via analytical methods (needs smaller adjustment of the angle parameter)
- some additional helpfull methods (threshold filter on picture array)



Single Picture Evaluation:
- 
- background subtraction, adjusted to a compared roi between background image and measurement image
- extract roi on image 
- hot pixel removal (threshold filter on picture)
- integration to get line-out over defined ROI
- intensity constant scaling (e.g. to convert measurement time to per second)
- save function (result array,  plots)

In Stack and Stack to Stack Evaluation :
- 
- features: calculates on 64 bit on integrated signals, 32bit on pictures 
- batch processing single picture evaluation with one or two stacks, or alternating picture series stacks
- px-shift correction using find minimum in specified range (pointing correction)
- px-shift via fft-method on defined range
- comparison to not px-shifted results
- creates after px-shift correction avg of stack(s)
- Nexafs (-ln(counts(image)/counts(reference))) for given input - this corresponds to ODD calculation
- px shift correction between to stacks
- save functions of single integrated signals non px shift corrected and separately px shift corrected lines outs
- saves avg results and pictures
- save shift-list for diagnostic purposes
- x binning option (2px binning so far)

Calibration Evaluation: 
- 
Two approaches for spectral calibration: 

1. by fit via identifying lines in the image and name corresponding energy: "sprectral_calibration_xxx_fit.py"
2. Via a geometrical (analytical function that is fed with some parameters of the RZP): "spectral_calibration_analytical.py"
- conversion nm to eV
- integration of calibration lines (if provided) in plots
- save function (result array,  plots)
- parameter files needed (px-size, fit points in px or parameter of RZP structure and angles for analytical, see below)

Additional Content:
- 
- plot filter data on result image
- statistics on processed files 
- calibration from counts to Nphoton/s sr @ 0.1% bandwidth units for given calibration files of detector, filters and diffractive optics
- Evaluation for spectral resolution: FWHM with linear interpolation of selected spectral ranges. This is needed, as usually the input data of a recorded spectral 
line consists on too little data points. 
- higher order for spectral calibration (check)






Helping tools for interpreting the quality of the calibration :
-
If the source stays constant, as the RZP and detector, there should be no change in the parameter if one switches from 
one structure to another, except for the RZP structure size. Small deviations might reflect deviations in either source, 
RZP structure size. In order to test this for consistency: 
1. "Higher orders" from a high energy structure, appearing at lambda* order on another structure  -> using similar parameters this should be consistent
    With this we can as well identify higher orders (if the data from different sprectral ranges is provided)
2. check deviations of the alignment with the "alignment structure " tool: the alignment structure is the same for every RZP structure and by this should deviate if the angle on the RZP has changed over the measurement
3. (in progress:) statistical shot to shot deviation evaluation and averaging for provided stack of images (stability in counts and position)
4. "counter_to_photon_number "approximation for the number photons per s and sr @ 0.1 bandwidth from calibrated spectrum for provided calibration files
5. linear interpolation of calibration files (sub sampling)



Packages used: 
- 
- numpy
- matplotlib
- scipy.interpolate
- scipy fftpack
- scipy signal
- math
- python 3.7 / 3.8 / 3.9
- os
- imageio


To Do - how to use this script:
- 
for batch purpose with one folder and alternating pictures use: "Stack_integration_avg_alternating.py" or "Stack_integration_with_px_shift_two_arrays_alternating.py"

for batch purpose with two folders: "Stack_integration_with_shift_two_folders.py"

- set your input directories and files 
- set your avg - background tif file for background substraction
- name your result folder and names of the evaluated data for "picture" and "reference"
- set picture roi 
- set background roi if referenced background method is chosen
- set your aquisition time
- choose background method
- choose / enable threshold filter
- set reference point for px- shift 
- set method for px-shift (still in the script... )
- set / change the range for the px-shift method
- change the plot titles...
- check if px-shift correction does what it should - probably check if roi is correct etc.

Script delivers up to your integrated lineouts (in y) with counts to counts/s and px shift correction or not, and avg calculation
of it. Up to here: not calibration is done.

For calibration choose: "calibration_analytical_from_1Darray.py"
- give it a calibration file
- choose your csv or txt file to be opened and calibrated
- set paraemters for ranges in angle beta (optional)
- give result folder ...


Px Shift Correction via Minimum or Maximum:
- 
This is a robust method if your signal has a distinct minimum or maximum and sufficient little noise. This method
searches within a given range around a given reference point the minimum and compares and corrects all pictures on the 
minimum position of the first picture. Works fast if range is small and signal is not noisy. For noisy signal the method
fails and typically artifacts, like too deep spiked minimums results in the avg - of  - stack of picture results.

Px Shift Correction via FFT:
- 
Method works better for noisy signals but only up to limit of above the noise threshold signals. The range for
this methods should as well be small for noisy signals, otherwise this method can work for longer ranges. 
upcoming: correlate on the fft correlation - that needs more calculation power but could enhance the results


Quasi Benchmarking:
- 
on Intel I7 8.th generation the methods were optimized such, that 2048x2048 16 bit .tif file processing should 
not be longer than 300ms - most of the array calculations are on 32bit (picture arrays) and on 64bit for integrated signals.
The bottleneck is the io-processes (opening, closing, saving), followed by calculations on picture 
arrays. The stack batch processes need access to all the single picture of a stack data (like pictures or integrated line outs), 
by this we spam the memory. To limit it: avoid doing too much calculations on single picture arrays. 
This results in consecutive step orders for methods: open image, take roi of image, integrate over y, then subtract
integrated signal with background integrated signal ... and so on. 
Or saving to many single csv / txt files: single picture of stack data is saved for the whole stack in one file, separated by
columns.
