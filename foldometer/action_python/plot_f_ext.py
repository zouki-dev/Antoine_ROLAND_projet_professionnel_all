import foldometer as fm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
import os
from matplotlib.figure import Figure
import pickle
from os import listdir
from os.path import isfile, join
import os
from foldometer.tools.region_manipulation import get_cycle_region_time_sorted
import seaborn as sns

folderProject = "D:/project/ubiquitin"
folderData = folderProject + "/fitted_data"
folderFigure = folderProject + "/figure_f_ext"

rulers = [0, 240, 240+78*0.35]

names = listdir(folderData)


parameters = pd.read_csv(folderProject + "/wlc_fit_analysis.csv")
for name in names:
    parameter = parameters.loc[parameters["fileName"] == name]
    data = pd.read_csv(folderData + "/" + name)

    plt.figure(figsize=(16, 9))
    # fig, ax = plt.subplots(111, figsize=(16, 9))
    cycleRegion = get_cycle_region_time_sorted(data)
    pullingCycles = len(data["pullingCycle"].unique())
    palettes = {"pulling": sns.color_palette("PuBu_d", pullingCycles),\
                "retracting": sns.color_palette("YlOrRd_d", pullingCycles),\
                "stationary": sns.color_palette("Greens_d", pullingCycles)}

    for (pullingCycle, region, mask) in cycleRegion:
        plt.plot(data["surfaceSepX"].loc[mask], data["forceX"].loc[mask],\
                 color=palettes[region][pullingCycle], label=region + " " + str(pullingCycle))

    forceArray = np.arange(0.5, 60, 0.2)
    for length in rulers:
        plt.plot(wlc_series_accurate(forceArray,\
                                     parameter["contourLengthDNA"].item(),\
                                     parameter["persistenceLengthDNA"].item(),\
                                     parameter["stretchModulusDNA"].item(),\
                                     length,\
                                     parameter["persistenceLengthProtein"].item(),\
                                     ), forceArray, color="gray", zorder=0)

    plt.xlabel("Extension (nm)", fontsize=18)
    plt.ylabel("Force (pN)", fontsize=18)
    plt.tick_params(axis='x', labelsize=14)
    plt.tick_params(axis='y', labelsize=14)
    plt.title(name)
    if True: #label list maker
        handles, labels = plt.gca().get_legend_handles_labels()
        labelPulling = []
        indexPulling = []
        labelRetracting = []
        indexRetraction = []
        labelStationary = []
        indexStationary = []
        for i in range(len(labels)):
            label = labels[i]
            if label.find("pulling")>=0:
                labelPulling.append(label)
                indexPulling.append(i)
            if label.find("retracting")>=0:
                labelRetracting.append(label)
                indexRetraction.append(i)
            if label.find("stationary")>=0:
                labelStationary.append(label)
                indexStationary.append(i)
        indexSorted = indexPulling + indexRetraction + indexStationary
        labelSorted = [labels[i] for i in indexSorted]
        handlesSorted = [handles[i] for i in indexSorted]
        legend = plt.legend(handlesSorted, labelSorted)#, loc="upper left",)
        legend.get_frame().set_facecolor('white')

    if not os.path.exists(folderFigure):
        os.mkdir(folderFigure)
    plt.savefig(folderFigure + "/" + name + ".png")
    plt.savefig(folderFigure + "/" + name + ".pdf")