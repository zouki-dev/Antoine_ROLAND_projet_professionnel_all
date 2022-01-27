import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from os import listdir
import os
from foldometer.tools.region_manipulation import get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting
import seaborn as sns
from analysis_functionality.tools.str_analysis import int_to_000str, str_extension_remove

folderProject = "D:/projects/ClpG"
folderData = folderProject + "/wlc_manual_fit"
folderFigure = folderProject + "/split_cycle"

rulers = [0, 120, 130, 140,150]
contourLengthDNA = 5000 * 0.3

maxForceForPreviousRetracting = 30
minForceForNextRetracting = 35



names = listdir(folderData)

parameters = pd.read_csv(folderProject + "/wlc_manual_fit.csv")
for name in names:
    parameter = parameters.loc[parameters["fileName"] == str_extension_remove(name)].iloc[[-1]]
    data = pd.read_csv(folderData + "/" + name)

    maskForcePreviousRetracting = data["forceX"]<=maxForceForPreviousRetracting
    maskForceNextRetracting = data["forceX"]>=minForceForNextRetracting

    # fig, ax = plt.subplots(111, figsize=(16, 9))
    cycles = get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting(data) #list of dico 'retracting' 'stationary' 'pulling' 'nextRetracting'
    pullingCycles = len(data["pullingCycle"].unique())
    palettes = {"pulling": sns.color_palette("PuBu_d", pullingCycles),\
                "retracting": sns.color_palette("YlOrRd_d", pullingCycles),\
                "stationary": sns.color_palette("Greens_d", pullingCycles)}

    for cycle in cycles:
        plt.figure(figsize=(16, 9))
        forceArray = np.arange(0.5, 60, 0.2)
        for length in rulers:
            plt.plot(wlc_series_accurate(forceArray,\
                                         parameter["contourLengthDNA"].item(),\
                                         parameter["persistenceLengthDNA"].item(),\
                                         parameter["stretchModulusDNA"].item(),\
                                         length,\
                                         parameter["persistenceLengthProtein"].item(),\
                                         ), forceArray, color="gray", zorder=0)

        (pullingCycleRetracting, regionRetracting, maskRetracting) = cycle["retracting"]
        # mask = maskRetracting * maxForceForPreviousRetracting
        plt.plot(data["surfaceSepX"].loc[maskRetracting], data["forceX"].loc[maskRetracting],\
                 color="r", label=regionRetracting + " " + str(pullingCycleRetracting))

        (pullingCycleStationary, regionStationary, maskStationary) = cycle["stationary"]
        plt.plot(data["surfaceSepX"].loc[maskStationary], data["forceX"].loc[maskStationary],\
                 color="g", label=regionStationary + " " + str(pullingCycleStationary))

        (pullingCyclePulling, regionPulling, maskPulling) = cycle["pulling"]
        plt.plot(data["surfaceSepX"].loc[maskPulling], data["forceX"].loc[maskPulling],\
                 color="b", label=regionPulling + " " + str(pullingCyclePulling))

        (pullingCycleNextRetracting, regionNextRetracting, maskNextRetracting) = cycle["nextRetracting"]
        # mask = maskRetracting * maskForceNextRetracting
        plt.plot(data["surfaceSepX"].loc[maskNextRetracting], data["forceX"].loc[maskNextRetracting],\
                 color="m", label=regionNextRetracting + " " + str(pullingCycleNextRetracting))


        plt.xlabel("Extension (nm)", fontsize=18)
        plt.ylabel("Force (pN)", fontsize=18)
        plt.legend(loc="upper left")
        plt.tick_params(axis='x', labelsize=14)
        plt.tick_params(axis='y', labelsize=14)
        plt.title(name)

        if not os.path.exists(folderFigure):
            os.mkdir(folderFigure)
        plt.savefig(folderFigure + "/" + str_extension_remove(name) + "-" + str(int_to_000str(pullingCyclePulling)) + ".png")
        plt.savefig(folderFigure + "/" + str_extension_remove(name) + "-" + str(int_to_000str(pullingCyclePulling)) + ".pdf")