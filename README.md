# Reflection_Zone_Plate_evaluation


Two approaches for spectral calibration: 

1. by fit via identifying lines in the image and name corresponding energy: "sprectral_calibration_xxx_fit.py"
2. Via a geometrical (analytical function that is fed with some parameters of the RZP): "spectral_calibration_analytical.py"


Helping tool:
Check spectral calibration consistency with 
1. higher orders from a high energy structure, appearing at lambda* order on another structure  -> using similar parameters this should be consistent
2. check deviations of the alignment with the "alignment structure " tool: the alignment structure is the same for every RZP structure and by this should deviate if the angle on the RZP has changed over the measurement. Note: even if this is not the case, a tiny difference might stay: source drift etc. which could be seen in the fit- beamwaist of alignment structure (=toDO).

