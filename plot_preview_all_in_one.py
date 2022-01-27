import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from os import listdir
import os
from foldometer.tools.region_manipulation import get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting
import seaborn as sns
from analysis_functionality.tools.str_analysis import int_to_000str, str_extension_remove
from analysis_functionality.wlc_manual_fit.load import get_calibration_from_power_spectrum
from foldometer.ixo.lumicks_c_trap import process_lumicks_data, process_lumicks_data_old
from analysis_functionality.tools.str_analysis import str_extension_remove
import streamlit as st


# __________________________________________________ Inputs ____________________________________________________________
folderProject = 'S:/projects/Luca/dmMBP'
folderData = folderProject + "/csv_raw_data"
folderFigure = folderProject + "/plot_preview_all_in_one"
folderDiscard = folderProject + "/discard"

contourLengthDNAinBp = [1000, 2600, 5000, 10000]
contourLengthDNAlist = [bp*0.3 for bp in contourLengthDNAinBp]

xmax = 5000

replaceOlderAnalysis = False


# _________________________________________ Find files to analyse ______________________________________________________
if replaceOlderAnalysis:
    names = [name for name in listdir(folderData) if not "Spectrum" in name]
else:
    if os.path.exists(folderFigure):
        names = [name for name in listdir(folderData) if (not "Spectrum" in name) and (not name in listdir(folderFigure))]
    else:
        names = [name for name in listdir(folderData) if not "Spectrum" in name]


# __________________________________________________ plot preview ______________________________________________________
st.title("plot_preview_all_in_one")
if not os.path.exists(folderFigure):
    os.mkdir(folderFigure)

figs = [plt.figure(figsize=(16, 9)) for i in range(100)]
indexFig = 0


plt.figure(figs[indexFig].number)
timeExperiment = 0
experimentName_1 = names[0][0:8] + "_" + " ".join(names[0].split(" ")[1:-1])
maxExtension = 0
print(str(len(names)) + " to analyse")
if os.path.exists(folderDiscard):
    nameList = [name for name in names if name not in [file[:-4] for file in os.listdir(folderDiscard)]]
else:
    nameList = names
for name in nameList:
    print(name)
    experimentName = name[0:8] + "_" + " ".join(name.split(" ")[1:-1])
    if experimentName != experimentName_1:
        forceArray = np.arange(0.5, 60, 0.2)
        for contourLengthDNA in contourLengthDNAlist:
            plt.plot(wlc_series_accurate(forceArray, contourLengthDNA, 44.4, 720, 0, 0.75), forceArray, color="k",
                     zorder=2)
        plt.xlim((0, 5000))
        plt.ylim((-5, 70))

        plt.xlabel("Extension (nm)", fontsize=18)
        plt.ylabel("Force (pN)", fontsize=18)
        plt.tick_params(axis='x', labelsize=14)
        plt.tick_params(axis='y', labelsize=14)
        # plt.title(experimentName_1 + "\n" + str(int(timeExperiment)) + " s")
        timeExperiment = 0

        if not os.path.exists(folderFigure):
            os.mkdir(folderFigure)
        plt.savefig(folderFigure + "/" + experimentName_1 + ".png")
        plt.savefig(folderFigure + "/" + experimentName_1 + ".pdf")
        st.pyplot(figs[indexFig])
        indexFig+=1

        plt.figure(figs[indexFig].number)

    rawData = pd.read_csv(folderData + "/" + name)
    thermalCalibration = get_calibration_from_power_spectrum(folderData, str_extension_remove(name))
    data = process_lumicks_data_old(rawData, thermalCalibration)

    maskForce = data["forceX"]>=5
    timeExperiment += data["time"].diff().mean() * np.sum(maskForce)
    if data["surfaceSepX"].max() >= maxExtension:
        maxExtension = data["surfaceSepX"].max()

    plt.plot(data["surfaceSepX"], data["forceX"], zorder=0)

    experimentName_1 = experimentName

forceArray = np.arange(0.5, 60, 0.2)
for contourLengthDNA in contourLengthDNAlist:
    plt.plot(wlc_series_accurate(forceArray, contourLengthDNA, 44.4, 720, 0, 0.75), forceArray, color="k", zorder=2)

# plt.xlim((0, xmax))
plt.ylim((-5, 70))
plt.xlim((0, 5000))
plt.xlabel("Extension (nm)", fontsize=18)
plt.ylabel("Force (pN)", fontsize=18)
plt.tick_params(axis='x', labelsize=14)
plt.tick_params(axis='y', labelsize=14)
plt.title(experimentName_1 + "\n" + str(int(timeExperiment)) + " s")

if not os.path.exists(folderFigure):
    os.mkdir(folderFigure)
plt.savefig(folderFigure + "/" + experimentName_1 + ".png")
plt.savefig(folderFigure + "/" + experimentName_1 + ".pdf")

st.header(experimentName_1 + "\n" + str(int(timeExperiment)) + " s")
st.pyplot(figs[indexFig])
indexFig+=1
# plt.figure(figsize=(16, 9))
