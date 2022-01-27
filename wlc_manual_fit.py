import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from analysis_functionality.widget_streamlit_start_environnement.widget_streamlit_start_environnement import start_environnement
from analysis_functionality.widget_streamlit_start_environnement._m1_save_widget_output import save_widget_output
from analysis_functionality.widget_streamlit_start_environnement._m2_print_action_inventory import print_action_inventory
from analysis_functionality.python_list_output.parameters_read import parameter_read
from analysis_functionality.wlc_manual_fit.wlc_parameters import make_dna_parameter, select_parameters
from analysis_functionality.wlc_manual_fit.autofit import find_fully_unfolded_point, estimate_extension_offset
from analysis_functionality.wlc_manual_fit.graph import plot_select_region, plot_fExt_wlc, plot_fLc_wlc
from analysis_functionality.wlc_manual_fit.user_input import select_region_of_interest
from analysis_functionality.tools.str_analysis import str_extension_remove, str_extension_select
from analysis_functionality.wlc_manual_fit.load import get_calibration_from_power_spectrum
from analysis_functionality.tools.streamlit_wide_mode import wide_mode

from foldometer.ixo.lumicks_c_trap import process_lumicks_data
from foldometer.analysis.region_classification import assign_regions
from foldometer.analysis.wlc_curve_fit import protein_contour_length_accurate
from streamlit import caching
from copy import deepcopy
from os import listdir
import os
import numpy as np

folderProject = 'S:/projects/Luca/dmMBP'

def wlc_manual_fit(folderProject=folderProject):
    st.set_option('deprecation.showPyplotGlobalUse', False)
    folderData = folderProject + "/csv_raw_data"
    folderSave = folderProject + "/wlc_manual_fit"
    rulersDefault = [0.0, 120]
    bpDNADefault = 5000
    ASSIGN_REGION = True


    # ------------------------------------------Start streamlit environnement------------------------------------------------
    st.sidebar.header("Start environnement")

    [allRawData, allAction, labels, parameters] = start_environnement(__file__parent=__file__, folderProject=folderProject, folderData=folderData)
    actionName = parameter_read(labels, parameters, "actionName")
    fileName = parameter_read(labels, parameters, "fileName")
    rulers = [float(length) for length in st.sidebar.text_input("Rulers:", str(rulersDefault)).replace("[","").replace("]","").replace(" ","").split(",")]
    bpDNA = st.sidebar.number_input("bpDNA",None,None, bpDNADefault)


    # __________________________select region + asign region _________________________________
    def find_breaking(data):
        forceDiff = data["forceX"].diff()
        forceBreakingIndicator = data["forceX"].iloc[1:] - 5*np.abs(forceDiff)
        mask = forceBreakingIndicator<=-10
        if mask.any():
            # st.text(data["time"].iloc[np.array(forceBreakingIndicator[mask].index)[-1]-2].item())
            return data["time"].iloc[np.array(forceBreakingIndicator[mask].index)[-1]-2].item()
        else:
            return data["time"].max()
    def find_double_thethers(data):
        maskForceTooHigh = data["forceX"] >= 67
        timeDoubleTether = data["time"].loc[maskForceTooHigh].max() + 0.1

        if timeDoubleTether == timeDoubleTether:
            return timeDoubleTether
        else:
            return 0
    (tStartDefault, tEndDefault) = (find_double_thethers(allRawData), find_breaking(allRawData))

    (rawDataNoRegion, tStart, tEnd) = select_region_of_interest(allRawData, tStartDefault, tEndDefault)
    plot_select_region(allRawData, rawDataNoRegion, tStart, tEnd)

    correctRegion = st.checkbox("assign region", ASSIGN_REGION)
    correctOffset = st.checkbox("Correct Offset", True)
    beadTracking = st.checkbox("Bead tracking", False)

    rawData = assign_regions(rawDataNoRegion, correctRegion=correctRegion)
    tFocus = {"tStart" : tStart,\
              "tEnd" : tEnd}


    # _________________________________calibration ________________________________________
    # thermalCalibration = get_calibration_from_power_spectrum(folderData, fileName)
    with open(folderData + "/" + fileName + " Power Spectrum.csv") as f:
        header = f.readline().strip().split(",")
        header[0] = "index"

    thermalCalibration = pd.read_csv(folderData + "/" + fileName + " Power Spectrum.csv", index_col=0)
    paramsWlc = make_dna_parameter(bpDNA=bpDNA)

    windowFactor = 20
    sampleFreq = rawData["time"].diff().mean()
    window = int(sampleFreq // windowFactor)


    autoParamsWlc = paramsWlc
    (foldometerCalFit, paramsWlcFit, extensionOffsetCorrection, forceOffset, tweezersParametersModification) = select_parameters(thermalCalibration, autoParamsWlc)

    # beadTracking = False
    dataNoOffset = process_lumicks_data(rawData, thermalCalibration, foldometerCalFit, beadTracking=beadTracking)


    # _________________________________fix extension ________________________________________
    targetPointForExtensionAutoFit = find_fully_unfolded_point(dataNoOffset, tStart, tEnd)
    if correctOffset and targetPointForExtensionAutoFit is not None:
        extensionOffsetAuto = estimate_extension_offset(dataNoOffset, targetPointForExtensionAutoFit, paramsWlcFit, rulers[-1])
        extensionOffset = float(extensionOffsetAuto + extensionOffsetCorrection)
    else:
        extensionOffsetAuto = 0
        extensionOffset = float(extensionOffsetAuto + extensionOffsetCorrection)

    data = deepcopy(dataNoOffset)
    data["surfaceSepX"] = data["surfaceSepX"] + extensionOffset
    data["forceX"] = data["forceX"] + forceOffset


    # _________________________________proteinLc ________________________________________
    data["proteinLc"] = protein_contour_length_accurate(data["surfaceSepX"], data["forceX"],\
                                                        persistenceLengthProtein=paramsWlcFit["persistenceLengthProtein"],\
                                                        persistenceLengthDNA=paramsWlcFit["persistenceLengthDNA"],\
                                                        contourLengthDNA=paramsWlcFit["contourLengthDNA"],\
                                                        stretchModulusDNA=paramsWlcFit["stretchModulusDNA"])


    # _____________________________________ plot ________________________________________
    st.subheader("Fit your force extension data")
    plot_fExt_wlc(data, paramsWlcFit, rulers, alpha=0.2)
    st.title("extensionOffset: " + str(extensionOffset))
    plot_fLc_wlc(data, paramsWlcFit, rulers)

    contourLengthDNA = paramsWlcFit["contourLengthDNA"]
    persistenceLengthDNA = paramsWlcFit["persistenceLengthDNA"]
    stretchModulusDNA = paramsWlcFit["stretchModulusDNA"]
    persistenceLengthProtein = paramsWlcFit["persistenceLengthProtein"]

    trapStiffness1 = float(foldometerCalFit["stiffness"].loc["PSD1x"])
    expDiffusion1 = float(foldometerCalFit["diffusionExp"].loc["PSD1x"])
    trapStiffness2 = float(foldometerCalFit["stiffness"].loc["PSD2x"])
    expDiffusion2 = float(foldometerCalFit["diffusionExp"].loc["PSD2x"])




    minLc = float(st.text_input("min Lc:", str(-200)))
    maxLc = float(st.text_input("max Lc:", str(500)))

    minTime = float(st.text_input("min time:", str(0)))
    maxTime = float(st.text_input("max time:", str(data["time"].max())))

    mask = (data["time"]>=minTime)*(data["time"]<=maxTime)*(data["proteinLc"]>=minLc)*(data["proteinLc"]<=maxLc)
    fig, ax = plt.subplots()
    plt.plot(data["time"].loc[mask], data["proteinLc"].loc[mask])
    st.pyplot(fig)

    # _____________________________________ Print and saving preparation ________________________________________
    st.sidebar.header("Saving")
    comments = st.sidebar.text_input("Comments:")

    labels_wlc = ["rulers", "bpDNA", "extensionOffset", "forceOffset", "tStart", "tEnd", "tweezersParametersModification",\
                  "contourLengthDNA", "persistenceLengthDNA", "stretchModulusDNA", "persistenceLengthProtein",\
                  "trapStiffness1", "expDiffusion1", "trapStiffness2", "expDiffusion2", "comments"]
    parameters_wlc = [str(rulers), bpDNA, extensionOffset, forceOffset, tStart, tEnd, tweezersParametersModification,\
                      contourLengthDNA, persistenceLengthDNA, stretchModulusDNA, persistenceLengthProtein,\
                      float(trapStiffness1), float(expDiffusion1), float(trapStiffness2), float(expDiffusion2), comments]

    for (label, parameter) in zip(labels_wlc, parameters_wlc):
        labels.append(label)
        parameters.append(parameter)

    st.text("extensionOffset: " + str(extensionOffset))
    st.text("trapStiffness1: " + str(trapStiffness1))
    st.text("expDiffusion1: " + str(expDiffusion1))
    st.text("trapStiffness2: " + str(trapStiffness2))
    st.text("expDiffusion2: " + str(expDiffusion2))

    # ---------------------------------------------Save action output-------------------------------------------------------
    save_widget_output(data, allRawData, folderSave, labels, parameters)
    print_action_inventory(folderProject, folderData, parameter_read(labels, parameters, "actionName"))
