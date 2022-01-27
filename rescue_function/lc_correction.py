import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from scipy.ndimage import median_filter
from scipy.stats import iqr
import streamlit as st
from analysis_functionality.tools.streamlit_wide_mode import wide_mode
from foldometer.tools.region_manipulation import get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from copy import deepcopy
from sklearn.neighbors import KNeighborsClassifier


#____________________________________________ Initialisation ___________________________________________________________
folderProject = "D:/projects/ubiquitin_extrusion"
folderData = folderProject + "/" + "wlc_manual_fit"
folderSave = folderProject + "/" + "lc_correction"
folderLcCorrectionTemplate = folderProject + "/" + "Lc_Correction_Template"
if not os.path.exists(folderSave):
    os.mkdir(folderSave)
if not os.path.exists(folderLcCorrectionTemplate):
    os.mkdir(folderLcCorrectionTemplate)
if not os.path.exists(folderSave):
    os.mkdir(folderSave)
if not os.path.exists(folderSave + "/figure"):
    os.mkdir(folderSave + "/figure")
wide_mode()

names = [nane[:-4] for nane in os.listdir(folderData) if not "Power Spectrum" in nane]
name = st.sidebar.selectbox("Select file", names)
data = pd.read_csv(folderData + "/" + name + ".csv")
parameters = pd.read_csv(folderProject + "/wlc_manual_fit.csv")
parameter = parameters.loc[parameters["fileName"] == name].iloc[[-1]]
rulersDefault = st.sidebar.text_input("rulers", parameter["rulers"].item())
rulers = [float(length) for length in rulersDefault.replace("]", "").replace("[", "").replace(" ", "").split(",")]

#_________________________________ sidebar plot _________________________________________________
if os.path.exists(folderLcCorrectionTemplate +"/"+"no_unfolding_pulling.csv"):
    dataCsv = pd.read_csv(folderLcCorrectionTemplate+"/"+"no_unfolding_pulling.csv")

    extensionCsv = wlc_series_accurate(dataCsv["forceX"], \
                                                 parameter["contourLengthDNA"].item(), \
                                                 parameter["persistenceLengthDNA"].item(), \
                                                 parameter["stretchModulusDNA"].item(), \
                                                 dataCsv["proteinLc"], \
                                                 parameter["persistenceLengthProtein"].item(), \
                                                 )

    plt.plot(extensionCsv, dataCsv["forceX"], linewidth="0.21")
    forceArray = np.arange(0.5, 60, 0.2)
    for length in rulers:
        plt.plot(wlc_series_accurate(forceArray, \
                 parameter["contourLengthDNA"].item(), \
                 parameter["persistenceLengthDNA"].item(), \
                 parameter["stretchModulusDNA"].item(), \
                 length, \
                 parameter["persistenceLengthProtein"].item(), \
                 ), forceArray, color="gray", zorder=0)
    st.sidebar.pyplot()
else:
    st.sidebar.pyplot()

if os.path.exists(folderLcCorrectionTemplate+"/"+"no_unfolding_pulling.csv"):
    plt.plot(dataCsv["proteinLc"], dataCsv["forceX"], linewidth="0.21")
    plt.xlim((-20, rulers[-1]+20))
    plt.ylim((0, 70))
    st.sidebar.pyplot()
else:
    st.sidebar.pyplot()


# _________________________________ Select No unfolding high force data _________________________________________________
if st.sidebar.checkbox("Select no unfolding region"):
    cycles = get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting(data)
    region_name = ["retracting", "stationary", "pulling", "nextRetracting"]

    column_names = ["dataName", "cycleNumber", "region", "deltaLc", "forceBefore", "forceAfter", "lcBefore", "lcAfter", "maxSustainableForce"]
    listUnfolding = []
    threshold = None
    for (i, cycle) in enumerate(cycles):
        (pullingCycle, _0, maskRetracting) = cycle["retracting"]
        (pullingCycle, _1, maskStationary) = cycle["stationary"]
        (pullingCycle, _2, maskPulling) = cycle["pulling"]
        (pullingCycle, _3, maskNextRetracting) = cycle["nextRetracting"]
        maskCycle = maskStationary + maskPulling + maskNextRetracting

        parameters = pd.read_csv(folderProject + "/wlc_manual_fit.csv")
        parameter = parameters.loc[parameters["fileName"] == name].iloc[[-1]]

        tmin = data["time"].loc[maskCycle].min()
        tmax = data["time"].loc[maskCycle].max()
        (tminSelect, tmaxSelect) = st.slider("Label", tmin, tmax, (tmin, tmax))
        maskTime = (data["time"]>=tminSelect)*(data["time"]<=tmaxSelect)

        maskForce = data["forceX"]>=2
        ax1 = plt.subplot(111)
        plt.xlabel("Time (s)")
        plt.ylabel("Protein contour length (nm)")
        if maskCycle.any():
            ax1.plot(data["time"].loc[maskCycle], data["proteinLc"].loc[maskCycle], color="lightgrey", zorder=0)

            ax2 = ax1.twinx()
            ax2.plot(data["time"].loc[maskCycle], data["forceX"].loc[maskCycle], color="b", zorder=0)
        if (maskCycle*maskForce).any():
            ax1.plot(data["time"].loc[maskCycle*maskForce], savgol_filter(data["proteinLc"].loc[maskCycle*maskForce],51,1), color="b", zorder=2)
        if (maskCycle*maskForce*maskTime).any():
            ax1.plot(data["time"].loc[maskCycle*maskForce*maskTime], savgol_filter(data["proteinLc"].loc[maskCycle*maskForce*maskTime],51,1), color="r", zorder=3)
        if maskCycle.any():
            forceArray = np.arange(0.5, 60, 0.2)
            for length in rulers:
                ax1.plot([data["time"].loc[maskCycle].min(), data["time"].loc[maskCycle].max()], [length, length], "k", zorder=1)
            ax1.set_xlim((tmin, tmax))
            ax1.set_ylim((-20, rulers[-1]+20))
            ax2.set_ylim((-5, 70))
            st.pyplot()

        if st.button(str(i)+" - No unfolding at force>=40:", False):
            st.text("Added To no_unfolding_pulling.csv, Done !")
            dataTemp = deepcopy(data[[column for column in data.columns if not column=="proteinLc"]])
            dataTemp["proteinLc"] = np.nan
            dataTemp["proteinLc"] = data["proteinLc"] - data["proteinLc"].loc[(data["forceX"]>=18)*(data["forceX"]<=22)].mean()
            if not os.path.exists(folderLcCorrectionTemplate+"/"+"no_unfolding_pulling.csv"):
                dataTemp.loc[maskCycle].to_csv(folderLcCorrectionTemplate+"/"+"no_unfolding_pulling.csv")
            else:
                dataCsv = pd.read_csv(folderLcCorrectionTemplate+"/"+"no_unfolding_pulling.csv")
                pd.concat([dataCsv, dataTemp.loc[maskCycle*maskTime]]).to_csv(folderLcCorrectionTemplate + "/" + "no_unfolding_pulling.csv")
        else:
            st.text("Waitting")


#_________________________________ Select No unfolding high force data _________________________________________________
if st.sidebar.checkbox("Save the correction template"):
    data = pd.read_csv(folderLcCorrectionTemplate+"/"+"no_unfolding_pulling.csv")
    minForce = st.number_input("min Force=",-1000.,1000.,30.)
    maxLc = st.number_input("max protein Lc=",-1000.,1000.,60.)
    mask = (data["forceX"]>=minForce)*(data["proteinLc"]<=maxLc)

    deltaTime = data["time"].diff().mean()
    win_size = int(1/deltaTime)
    fit = np.polyfit(np.array(data["proteinLc"].loc[mask]), np.array(data["forceX"].loc[mask]), deg=2)
    res = np.zeros(len(data["proteinLc"].loc[mask]))
    res[win_size-1:] = np.polynomial.polynomial.polyval(win_size, fit[::-1])

    forceArray = np.arange(0.5, 60, 0.2)
    plt.plot(data["proteinLc"], data["forceX"],  zorder=2)
    plt.plot(data["proteinLc"].loc[mask], data["forceX"].loc[mask],  zorder=3, color="orange")

    plt.plot([maxLc,maxLc], [0,60], "k",  zorder=1)
    plt.plot([-20,maxLc], [minForce,minForce], "k",  zorder=1)
    plt.xlim((-20, 150))
    plt.ylim((0,70))
    st.pyplot()

    dataSort = deepcopy(data.loc[mask])
    dataSort = dataSort.sort_values("forceX")
    dataSort.reset_index(drop=True, inplace=True)


    LcPointLow = data["proteinLc"].loc[mask].iloc[:100].mean()
    forcePointLow = data["forceX"].loc[mask].iloc[:100].mean()

    LcPointHigh = data["proteinLc"].loc[mask].iloc[-100:].mean()
    forcePointHigh = data["forceX"].loc[mask].iloc[-100:].mean()

    st.sidebar.latex("\\Delta Lc(force) = L_A*e^{\\frac{force - f offset}{fc}}")
    st.sidebar.text("La is fitted")
    Lcoffset = st.sidebar.number_input("- Lcoffset", -1000.0, 1000.0, 0.0, step=1.0)
    fc = st.sidebar.number_input("fc", -1000.0, 1000.0, 10.0, step=1.0)
    La = LcPointHigh / (np.exp((forcePointHigh)/fc))

    def function_fit_Lc(force, La, fc, Lcoffset):
        return La * np.exp((force)/fc) + Lcoffset

    def function_fit_force(Lc, La, fc, Lcoffset):
        return fc * np.log(Lc-Lcoffset/La)

    forceArray = np.linspace(0, 70, 7000)
    plt.plot(function_fit_Lc(forceArray, La, fc, Lcoffset), forceArray, color="k", zorder=4)
    plt.plot(data["proteinLc"], data["forceX"],  zorder=2)
    plt.plot(data["proteinLc"].loc[mask], data["forceX"].loc[mask],  zorder=3, color="orange")
    plt.plot([maxLc,maxLc], [0,60], "k",  zorder=1)
    plt.plot([-20,maxLc], [minForce,minForce], "k",  zorder=1)
    plt.xlim((-20, 150))
    plt.ylim((0,70))
    st.sidebar.success("Save")
    if st.sidebar.button("Save exp_curve_parameters.csv"):
        dico = {"La": [La],
                "fc": [fc],
                "Lcoffset": [Lcoffset]}

        dfCorrectCurveParameters = pd.DataFrame(dico)
        dfCorrectCurveParameters.to_csv(folderLcCorrectionTemplate + "/" + "exp_curve_parameters" + ".csv")
        plt.savefig(folderLcCorrectionTemplate + "/" + "fit_wlc_deviation" + ".png")
    st.pyplot()

    st.text("La="+str(La))
    st.text("fc="+str(fc))
    st.text("Lcoffset="+str(Lcoffset))


st.sidebar.header("Correct all data")
if st.sidebar.button("Correct all data"):
    folderSave = folderProject + "/" + "lc_correction"
    pathCorrection = folderLcCorrectionTemplate+"/exp_curve_parameters.csv"

    names = [name for name in os.listdir(folderData) if not "Spectrum" in name]

    def function_fit_Lc(force, La, fc, Lcoffset):
        return La * np.exp((force)/fc) + Lcoffset
    def function_fit_force(Lc, La, fc, Lcoffset):
        return fc * np.log(Lc-Lcoffset/La)


    st.header("Saving")
    st.text("Nb data: "+str(len(names)))
    for (i,name) in enumerate(names):
        st.text(str(i)+" : "+name)
        data = pd.read_csv(folderData + "/" + name)
        maskForce = data["forceX"] >= 5
        dataCorrection = deepcopy(data)
        dfCorrectCurveParameters = pd.read_csv(folderLcCorrectionTemplate + "/" + "exp_curve_parameters" + ".csv")

        forceDeviationZeros = function_fit_force(0, dfCorrectCurveParameters["La"].item(),
                                                  dfCorrectCurveParameters["fc"].item(),
                                                  dfCorrectCurveParameters["Lcoffset"].item())

        maskCorrectDeviation = data["forceX"] >= forceDeviationZeros
        lcDeviation = function_fit_Lc(data["forceX"].loc[maskCorrectDeviation],
                                    dfCorrectCurveParameters["La"].head(1).item(),
                                    dfCorrectCurveParameters["fc"].head(1).item(),
                                    dfCorrectCurveParameters["Lcoffset"].head(1).item())
        dataCorrection["proteinLc"].loc[maskCorrectDeviation] -= lcDeviation
        dataCorrection["surfaceSepX"] = wlc_series_accurate(dataCorrection["forceX"], \
                                             parameter["contourLengthDNA"].item(), \
                                             parameter["persistenceLengthDNA"].item(), \
                                             parameter["stretchModulusDNA"].item(), \
                                             dataCorrection["proteinLc"], \
                                             parameter["persistenceLengthProtein"].item(), \
                                             )

        ax1 = plt.subplot(4, 1, 1)
        plt.plot(dataCorrection["time"], dataCorrection["forceX"], "b")
        plt.ylabel("Force (pN)")
        ax1.set_xticklabels([])

        ax2 = plt.subplot(4, 1, (2, 4))
        ax1.get_shared_x_axes().join(ax1, ax2)
        plt.plot(dataCorrection["time"], dataCorrection["proteinLc"], "grey")
        plt.plot(dataCorrection["time"].loc[maskForce],
                 savgol_filter(dataCorrection["proteinLc"].loc[maskForce], 51, 1), "r")
        plt.xlabel("Time (s)")
        plt.ylabel("Protein length (nm)")
        plt.ylim((-20, 400))
        plt.savefig(folderSave + "/figure" + "/" + name[:-4] + "_time-Lc" + ".png")
        plt.close()

        plt.plot(dataCorrection["surfaceSepX"].loc[maskForce],savgol_filter(dataCorrection["forceX"].loc[maskForce], 51, 1), "r")
        plt.xlabel("Time (s)")
        plt.ylabel("Protein length (nm)")
        plt.ylim((-5, 70))
        plt.savefig(folderSave + "/figure" + "/" + name[:-4] + "_force-ext" + ".png")
        plt.close()

        dataCorrection.to_csv(folderSave + "/" + name[:-4] + ".csv")
    st.text("finish")


