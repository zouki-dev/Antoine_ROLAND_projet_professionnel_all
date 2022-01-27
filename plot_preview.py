import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from os import listdir
import os
from analysis_functionality.wlc_manual_fit.load import get_calibration_from_power_spectrum
from foldometer.ixo.lumicks_c_trap import process_lumicks_data_old
from analysis_functionality.tools.str_analysis import str_extension_remove
import streamlit as st

# __________________________________________________ Inputs ____________________________________________________________
folderProject = 'S:/projects/Luca/dmMBP'

def plot_preview(folderProject=folderProject):
    folderData = folderProject + "/csv_raw_data"
    folderFigure = folderProject + "/plot_preview"
    folderDiscard = folderProject + "/discard"

    rulers = [0]
    contourLengthDNA = st.sidebar.number_input("DNA contour length", None, None, 10000) * 0.3

    replaceOlderAnalysis = False

    if not os.path.exists(folderFigure):
        os.mkdir(folderFigure)

    # _________________________________________ Find files to analyse ______________________________________________________
    if replaceOlderAnalysis:
        names = [name for name in listdir(folderData) if not "Spectrum" in name]
    else:
        names = [name for name in listdir(folderData) if (not "Spectrum" in name) and (not name in listdir(folderFigure))]


    # __________________________________________________ plot preview ____________________________________________________________
    print("rulers: " + str(rulers))
    print(len(names))
    if os.path.exists(folderDiscard):
        nameList = [name for name in names if name not in [file[:-4] for file in os.listdir(folderDiscard)]]
    else:
        nameList = names
    for (i, name) in enumerate(nameList):
        print(str(i) + " :  " + folderData + "/" + name)
        if os.stat(folderData + "/" + name).st_size >= 50000:
            rawData = pd.read_csv(folderData + "/" + name)

            thermalCalibration = get_calibration_from_power_spectrum(folderData, str_extension_remove(name))
            data = process_lumicks_data_old(rawData, thermalCalibration)

            fig = plt.figure(figsize=(16, 9))
            forceArray = np.arange(0.5, 60, 0.2)
            for length in rulers:
                plt.plot(wlc_series_accurate(forceArray, contourLengthDNA, 44.4, 720, length, 0.75), forceArray, color="gray")

            # maskTime = data["time"] >= 1460
            # plt.plot(data["surfaceSepX"].loc[maskTime], data["forceX"].loc[maskTime], color="b")
            plt.plot(data["surfaceSepX"], data["forceX"], color="b")

            plt.xlabel("Extension (nm)", fontsize=18)
            plt.ylabel("Force (pN)", fontsize=18)
            plt.tick_params(axis='x', labelsize=14)
            plt.tick_params(axis='y', labelsize=14)
            plt.title(name)

            if not os.path.exists(folderFigure):
                os.mkdir(folderFigure)
            plt.savefig(folderFigure + "/" + str_extension_remove(name) + ".png")
            plt.savefig(folderFigure + "/" + str_extension_remove(name) + ".pdf")
            st.pyplot(fig)
            plt.close()
    print("Finish !")



if __name__ == '__main__':
    plot_preview()