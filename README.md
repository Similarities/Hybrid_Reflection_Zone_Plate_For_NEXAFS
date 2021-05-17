# Reflection Zone Plate evaluation

RZP serve as novel high efficient and high resolving spectral dispersive device, in this case in reflection geometry. 
Resolution, angle etc. depends on the imprinted fresnel structure on the surface of the RZP. Commonly the
detection angle and position of RZP is keept constant. Because of this there might be more than one 
structure on the RZP, reachable with a motorized RZP holder and enabling different spectral ranges.

Two approaches for spectral calibration: :
-

1. by fit via identifying lines in the image and name corresponding energy: "sprectral_calibration_xxx_fit.py"
2. Via a geometrical (analytical function that is fed with some parameters of the RZP): "spectral_calibration_analytical.py"

Spectral calibration comes with the following tools:
- 
- stray light correction (for provided stray light/ background  images), mean value over roi
- background subtraction (image calculation), adjusted to a compared roi between background image and measurement image
- extract roi on image 

- integration to get line-out
- intensity constant scaling (e.g. to convert measurent time to per second)
- px-shift correction using find minimum in specified range
- spectral calibration according to method (analytical with input parameter)
- conversion nm to eV
- integration of calibration lines (if provided) in plots
- save function (result array,  plots)
- batch process over folder images
- plot filter data on result image

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

Spectral resolution:
- 
- FWHM with linear interpolation of selected spectral ranges. This is needed, as usually the input data of a recorded spectral 
line consists on too little data points. 
- batch compatible for different spectral lines and over stack of input data
- uses scypi package

Packages used: 
- 
- numpy
- matplotlib
- scipy.interpolate
- math
- python 3.7 / 3.8




