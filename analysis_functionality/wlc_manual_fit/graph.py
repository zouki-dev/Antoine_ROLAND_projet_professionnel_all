import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate


def plot_select_region(allRawData, rawData, tStart, tEnd):
    fig, ax = plt.subplots()
    ax.plot(allRawData["time"], allRawData["forceX"], color="b", zorder=0)
    ax.plot(rawData["time"], rawData["forceX"], color="r", zorder=1)
    plt.xlabel("Time (s)")
    plt.ylabel("Force (pN)")
    st.pyplot(fig)
    return




def plot_fExt_wlc(data, paramsWlc, rulers, alpha=0.2):
    def make_region_mask(data):
        return [data["region"] == "pulling", data["region"] == "retracting",
                data["region"] == "stationary"]
    [maskPulling, maskRetracting, maskStationary] = make_region_mask(data)
    fig1, chart1 = plt.subplots()
    chart1.scatter(data["surfaceSepX"].loc[maskPulling], data["forceX"].loc[maskPulling], color="b", s=0.1, alpha=alpha)
    chart1.scatter(data["surfaceSepX"].loc[maskRetracting], data["forceX"].loc[maskRetracting], color="r", s=0.1, alpha=alpha)
    chart1.scatter(data["surfaceSepX"].loc[maskStationary], data["forceX"].loc[maskStationary], color="g", s=0.1, alpha=alpha)
    forceArray = np.arange(0.5, 60, 0.2)
    for ruler in rulers:
        extension = wlc_series_accurate(forceArray,\
                    contourLengthDNA=paramsWlc["contourLengthDNA"],\
                    persistenceLengthDNA=paramsWlc["persistenceLengthDNA"],\
                    stretchModulusDNA=paramsWlc["stretchModulusDNA"],\
                    contourLengthProtein=ruler,\
                    persistenceLengthProtein=paramsWlc["persistenceLengthProtein"])
        chart1.plot(extension, forceArray, color="gray", linewidth=1)

    plt.xlabel('Extension (nm)')
    plt.ylabel('Force (pN)')
    # plt.xlim([2200., 3800.])
    plt.show()
    st.pyplot(fig1)
    return

from scipy.signal import savgol_filter
def plot_fLc_wlc(data, paramsWlc, rulers):
    def make_region_mask(data):
        return [data["region"] == "pulling", data["region"] == "retracting",
                data["region"] == "stationary"]
    [maskPulling, maskRetracting, maskStationary] = make_region_mask(data)
    maskForce = data["forceX"]>=2
    fig2, chart2 = plt.subplots()
    chart2.scatter(data["proteinLc"].loc[maskPulling], data["forceX"].loc[maskPulling], color="b", s=0.1, alpha=0.2, zorder=1)
    chart2.scatter(data["proteinLc"].loc[maskRetracting], data["forceX"].loc[maskRetracting], color="r", s=0.1, alpha=0.2, zorder=1)
    chart2.scatter(data["proteinLc"].loc[maskStationary], data["forceX"].loc[maskStationary], color="g", s=0.1, alpha=0.1, zorder=1)
    for ruler in rulers:
        chart2.plot([ruler, ruler], [0,70], color="k", linewidth=1, zorder=0)
    plt.xlabel('Contour length Lc (nN)')
    plt.ylabel('Force (pN)')
    plt.xlim((rulers[0]-50, rulers[-1]+50))
    plt.grid(st.checkbox("Grid on", True))
    st.pyplot(fig2)
    return