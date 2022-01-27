import streamlit as st
from analysis_functionality.widget_streamlit_start_environnement.widget_streamlit_start_environnement import start_environnement
from analysis_functionality.widget_streamlit_start_environnement._m1_save_widget_output import save_widget_output
from analysis_functionality.tools.str_analysis import str_extension_remove, str_extension_select
from os import listdir
from analysis_functionality.widget_streamlit_start_environnement._m2_print_action_inventory import print_action_inventory
from analysis_functionality.python_list_output.parameters_read import parameter_read
import streamlit as st
from os import listdir

import os
from matplotlib.figure import Figure
import pickle
from os import listdir
from copy import deepcopy
import csv
from streamlit import caching
from foldometer.ixo.lumicks_c_trap import process_lumicks_data
from foldometer.analysis.region_classification import assign_regions
from foldometer.analysis.wlc_curve_fit import wlc_fit_data, protein_contour_length, protein_contour_length_accurate

from analysis_functionality.python_list_output.parameters_read import parameter_read
from analysis_functionality.wlc_manual_fit.load import get_calibration_from_power_spectrum
from analysis_functionality.wlc_manual_fit.wlc_parameters import make_dna_parameter, select_parameters
from analysis_functionality.wlc_manual_fit.autofit import find_fully_unfolded_point, estimate_extension_offset
from analysis_functionality.wlc_manual_fit.graph import plot_select_region, plot_fExt_wlc, plot_fLc_wlc
from analysis_functionality.wlc_manual_fit.user_input import select_region_of_interest
from bokeh.plotting import figure

folderProject = "D:/projects/DHFR"
folderData = folderProject + "/csv_raw_data"
#------------------------------------------Start streamlit environnement------------------------------------------------
# REQUIRED_INPUTS = "inputs"
# REQUIRED_CSV_RAW_DATA = "csv_raw_data"
[allRawData, allAction, labels, parameters] = start_environnement(__file__parent=__file__, folderProject=folderProject)
# st.text(labels)
# st.text(parameters)
actionName = parameter_read(labels, parameters, "actionName")
fileName = parameter_read(labels, parameters, "fileName")
bpDNA = parameter_read(labels, parameters, "bpDna")
rulers = parameter_read(labels, parameters, "rulers")





# __________________________select region + asign region _________________________________
# (rawDataNoRegion, tStart, tEnd) = select_region_of_interest(allRawData, listLabelDefault, listTimeDefault)
(tStartDefault, tEndDefault) = (allRawData["time"].min(), allRawData["time"].max())




(rawDataNoRegion, tStart, tEnd) = select_region_of_interest(allRawData, tStartDefault, tEndDefault)
rawData = assign_regions(rawDataNoRegion, verbose=False)
tFocus = {"tStart" : tStart,\
          "tEnd" : tEnd}

# st.dataframe(allRawData)
# st.dataframe(rawData)
plot_select_region(allRawData, rawData, tStart, tEnd)
rawData = assign_regions(rawDataNoRegion, verbose=False)



# _________________________________calibration ________________________________________
thermalCalibration = get_calibration_from_power_spectrum(folderData, fileName)
paramsWlc = make_dna_parameter(bpDNA=bpDNA)

windowFactor=20
sampleFreq = rawData["time"].diff().mean()
window = int(sampleFreq // windowFactor)

autoThermalCalibration = thermalCalibration
autoParamsWlc = paramsWlc
(foldometerCalFit, paramsWlcFit, extensionOffsetCorrection, forceOffset, tweezersParametersModification) = select_parameters(autoThermalCalibration, autoParamsWlc)
dataNoOffset = process_lumicks_data(rawData, foldometerCalFit)



# (autoThermalCalibration, autoParamsWlc)  = (rawData, "x", rollingWindow=window)
# _________________________________fix extension ________________________________________
targetPointForExtensionAutoFit = find_fully_unfolded_point(dataNoOffset, tStart, tEnd)

extensionOffsetAuto = estimate_extension_offset(rawData, targetPointForExtensionAutoFit, paramsWlcFit, rulers[-1])
extensionOffset = extensionOffsetAuto + extensionOffsetCorrection

data = deepcopy(dataNoOffset)
data["surfaceSepX"] = data["surfaceSepX"] + extensionOffset
data["forceX"] = data["forceX"] + forceOffset


# _________________________________proteinLc ________________________________________
data["proteinLc"] = protein_contour_length_accurate(data["surfaceSepX"], data["forceX"],\
                                                    persistenceLengthProtein=paramsWlcFit["persistenceLengthProtein"],\
                                                    persistenceLengthDNA=paramsWlcFit["persistenceLengthDNA"],\
                                                    contourLengthDNA=paramsWlcFit["contourLengthDNA"],\
                                                    stretchModulusDNA=paramsWlcFit["stretchModulusDNA"])


#_____________________________________ plot ________________________________________
st.subheader("Fit your force extension data")
plot_fExt_wlc(data, paramsWlcFit, rulers)
plot_fLc_wlc(data, paramsWlcFit, rulers)



# labels.append("wlc_auto_fit_output")
# parameters.append(wlc_auto_fit_output)

#---------------------------------------------Save action output--------------------------------------------------------
save_widget_output(data, allAction, labels, parameters)
print_action_inventory(folderProject, folderData, parameter_read(labels, parameters, "actionName"))