import streamlit as st
import numpy as np
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from foldometer.tools.region_manipulation import get_cycle_region_time_sorted, clean_mask_one_block

def find_fully_unfolded_point(data, tStart, tEnd, targetForce=35, minForce=10):
    if data["forceX"].max()<=targetForce:
        targetForce = data["forceX"].max()
    sortedCycleRegion = get_cycle_region_time_sorted(data)
    extMax = 0
    targetTimePoint = data.head(1)
    for (pullingCycle, region, maskRegion) in sortedCycleRegion:
        i = (data["forceX"].loc[maskRegion]-targetForce).abs().idxmin()
        if i is np.nan:
            i=0
        ext = data["surfaceSepX"].loc[i]
        if ext > extMax:
            if data["forceX"].loc[i]>=minForce:
                extMax = ext
                idxExtMax = i

    try:
        timePreTarget = data["time"].iloc[idxExtMax]
        maskRegionTargetPoint = (data["time"] >= timePreTarget-0.1) * (data["time"] <= timePreTarget+0.1)
        extTargetPoint = data["surfaceSepX"].loc[maskRegionTargetPoint].median()
        idxTargetTimePoint = np.where(data["surfaceSepX"] == extTargetPoint)[0][0]
    except:
        idxTargetTimePoint = None
        st.text("Extension fit failed")
    return idxTargetTimePoint

# idxTargetTimePoint = find_fully_unfolded_point(data, tStart, tEnd)

def estimate_extension_offset(data, idxTargetTimePoint, paramsWLC, ruler):
    (extensionData, forceData) = (data["surfaceSepX"].iloc[idxTargetTimePoint], data["forceX"].iloc[idxTargetTimePoint])

    forceWlc = forceData
    extensionWlc = np.mean(wlc_series_accurate(forceWlc,\
                            contourLengthDNA=paramsWLC["contourLengthDNA"],\
                            persistenceLengthDNA=paramsWLC["persistenceLengthDNA"],\
                            stretchModulusDNA=paramsWLC["stretchModulusDNA"],\
                            contourLengthProtein=ruler,\
                            persistenceLengthProtein=paramsWLC["persistenceLengthProtein"]))
    return -(extensionData - extensionWlc)
