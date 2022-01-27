import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
import pandas as pd


def plot_select_region(allRawData, rawData, tFocus, WL_input="12", zoomWindow=20):
    plt.plot(allRawData["time"], allRawData["forceX"], color="b")
    plt.plot(rawData["time"], rawData["forceX"], color="r")
    plt.xlabel("Time (s)")
    plt.ylabel("Force (pN)")
    st.pyplot()

    print(tFocus)
    st.text(tFocus["tStart"])
    st.text(tFocus["tEnd"])
    for tIdentifier in tFocus:
        print(tFocus[tIdentifier])
        mask = (allRawData["time"] >= t - zoomWindow/2) * (allRawData["time"] <= t + zoomWindow/2)
        plt.plot(allRawData["time"].loc[mask], allRawData["forceX"].loc[mask], color="b")
        plt.plot(rawData["time"].loc[mask], rawData["forceX"].loc[mask], color="r")
        plt.xlabel("Time (s)")
        plt.ylabel("Force (pN)")
        st.pyplot()
    return




def plot_fExt_wlc(data, paramsWlc, rulers):
    def make_region_mask(data):
        return [data["region"] == "pulling", data["region"] == "retracting",
                data["region"] == "stationary"]
    [maskPulling, maskRetracting, maskStationary] = make_region_mask(data)
    fig1 = plt.figure(1, figsize=(6.4,4.8))
    chart1 = fig1.add_subplot(111)
    chart1.scatter(data["surfaceSepX"].loc[maskPulling], data["forceX"].loc[maskPulling], color="b", s=0.1, alpha=0.2)
    chart1.scatter(data["surfaceSepX"].loc[maskRetracting], data["forceX"].loc[maskRetracting], color="r", s=0.1, alpha=0.2)
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
    st.pyplot()
    return

def plot_fLc_wlc(data, paramsWlc, rulers):
    def make_region_mask(data):
        return [data["region"] == "pulling", data["region"] == "retracting",
                data["region"] == "stationary"]
    [maskPulling, maskRetracting, maskStationary] = make_region_mask(data)
    fig1 = plt.figure(1, figsize=(6.4,4.8))
    chart1 = fig1.add_subplot(111)
    chart1.scatter(data["proteinLc"].loc[maskPulling], data["forceX"].loc[maskPulling], color="b", s=0.1, alpha=0.2)
    chart1.scatter(data["proteinLc"].loc[maskRetracting], data["forceX"].loc[maskRetracting], color="r", s=0.1, alpha=0.2)
    forceArray = np.arange(0.5, 60, 0.2)
    for ruler in rulers:
        chart1.plot([ruler, ruler], [0,70], color="gray", linewidth=1)
    plt.xlabel('Contour length Lc (pN)')
    plt.ylabel('Force (pN)')
    plt.xlim((rulers[0]-50, rulers[-1]+50))
    plt.show()
    st.pyplot()
    return