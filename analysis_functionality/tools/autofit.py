import streamlit as st
import numpy as np
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from foldometer.tools.region_manipulation import get_cycle_region_time_sorted, clean_mask_one_block
from foldometer.analysis.event_classification import identify_unfolding_events

def find_fully_unfolded_point(data, tStart, tEnd, targetForce=35, minForce=10):
    manualTarget = st.checkbox("Do you want to manually chose the target point for auto fit of extension ?")
    if manualTarget:
        targetTimePoint = st.slider("Select a time point to auto fit extension", tStart, tEnd, tEnd*0.9)
        targetTimePoint = data["time"].loc[targetTimePoint].item()
    else:
        sortedCycleRegion = get_cycle_region_time_sorted(data)
        extMax = 0
        for (pullingCycle, region, maskRegion) in sortedCycleRegion:
            i = (data["forceX"].loc[maskRegion]-targetForce).abs().idxmin()
            ext = data["surfaceSepX"].loc[i]
            if ext > extMax:
                if data["forceX"].loc[i]>=minForce:
                    extMax = ext
                    targetTimePoint = data.loc[i]
    return targetTimePoint

def estimate_extension_offset(data, targetTimePoint, paramsWLC, ruler):
    (extensionData, forceData) = (np.array(targetTimePoint["surfaceSepX"]), \
                                  np.array(targetTimePoint["forceX"]))
    forceWlc = np.array(forceData)
    extensionWlc = np.mean(wlc_series_accurate(forceWlc,\
                contourLengthDNA=paramsWLC["contourLengthDNA"],\
                persistenceLengthDNA=paramsWLC["persistenceLengthDNA"],\
                stretchModulusDNA=paramsWLC["stretchModulusDNA"],\
                contourLengthProtein=ruler,\
                persistenceLengthProtein=paramsWLC["persistenceLengthProtein"]))
    return -(extensionData - extensionWlc)

def find_unfolding_and_perturbation(rawData, thermalCalibration, paramsWlc):
    unfoldingThreshold = int(st.text_input("unfoldingThreshold", 1))
    forceThreshold = int(st.text_input("forceThreshold", 5))
    rollingWindow = int(st.text_input("rollingWindow", 5))
    unfoldingWindow = int(st.text_input("unfoldingWindow", 15))
    unfoldingWindow = identify_unfolding_events(dataParent, axis="x", forceChannel="force", window=15, STDthreshold=0.8, forceThreshold=5)
    st.text(unfoldingWindow)
    autoThermalCalibration = thermalCalibration
    autoParamsWlc = paramsWlc
    return (autoThermalCalibration, autoParamsWlc)
