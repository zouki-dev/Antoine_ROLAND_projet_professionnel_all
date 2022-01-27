import streamlit as st
import numpy as np
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from foldometer.tools.region_manipulation import get_cycle_region_time_sorted, clean_mask_one_block

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
    (extensionData, forceData) = (targetTimePoint["surfaceSepX"], targetTimePoint["forceX"])

    forceWlc = forceData
    extensionWlc = np.mean(wlc_series_accurate(forceWlc,\
                            contourLengthDNA=paramsWLC["contourLengthDNA"],\
                            persistenceLengthDNA=paramsWLC["persistenceLengthDNA"],\
                            stretchModulusDNA=paramsWLC["stretchModulusDNA"],\
                            contourLengthProtein=ruler,\
                            persistenceLengthProtein=paramsWLC["persistenceLengthProtein"]))
    return -(extensionData - extensionWlc)
