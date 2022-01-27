import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os
from foldometer.tools.region_manipulation import get_cycle_region_time_sorted
from scipy.interpolate import interp1d
from foldometer.analysis.region_classification import assign_regions
import scipy.optimize as optimization
from scipy.signal import savgol_filter

folderProject = "D:/projects/Luca"
folderData = folderProject + "/" + "csv_raw_data"
folderSave = folderProject + "/" + "csv_raw_data_drift"

if not os.path.exists(folderSave):
    os.mkdir(folderSave)

names = [name[:-4] for name in os.listdir(folderData) if not "Power Spectrum" in name]
# nbData = len(names)
# iData = st.sidebar.number_input("Data Number", 0,nbData, 0, 1)
# name = names[iData]
# st.sidebar.text(name)
for name in names:
    data = pd.read_csv(folderData + "/" + name + ".csv")
    if not 'pullingCycle' in data:
        data = assign_regions(data, correctRegion=True)
    data["drift"] = None
    maskForce = (data["forceX"]>=33) * (data["forceX"]<=37)

    sortedCycleRegion = get_cycle_region_time_sorted(data)
    extensionTarget = None
    previousExtensionRegion = None
    for (i, (pullingCycle, region, maskRegion)) in enumerate(sortedCycleRegion):
        if region == "stationary":
            continue

        # extensionRegion = st.number_input("ExtensionRegion "+str(i),None,None,data["surfaceSepX"].loc[maskRegion*maskForce].mean())
        extensionRegion = data["surfaceSepX"].loc[maskRegion*maskForce].mean()

        #first run
        if (extensionTarget is None) and (extensionRegion==extensionRegion):
            extensionTarget = extensionRegion
            previousExtensionRegion = extensionRegion
            # extensionTarget = st.sidebar.number_input("unfolded state target", None, None, extensionRegion)
            data["drift"].loc[maskRegion] = 0
            maskRef = maskRegion
            continue
        if (extensionRegion==extensionRegion) and (np.abs(extensionRegion-previousExtensionRegion) <= 5):
            data["drift"].loc[maskRegion] = extensionTarget - extensionRegion
            previousExtensionRegion = extensionRegion
            # fig, ax = plt.subplots()
            # plt.plot(data["surfaceSepX"].loc[maskRef], data["forceX"].loc[maskRef], "lightgrey")
            # plt.plot(data["surfaceSepX"].loc[maskRegion], data["forceX"].loc[maskRegion])
            # st.pyplot(fig)

    maskNotNan = (data["drift"] == data["drift"])
    # st.text(len(np.array(data["time"].loc[maskNotNan])))
    # m, b = np.polyfit(np.array(data["time"].loc[maskNotNan]), np.array(data["drift"].loc[maskNotNan]), 1)
    def func(x,a,b):
        return a + b*x
    sigma = 0.1
    w, _ = optimization.curve_fit(func, data["time"].loc[maskNotNan], data["drift"].loc[maskNotNan], [1.,1.])


    plt.plot(data["time"], data["drift"])
    plt.plot(data["time"], w[1] * data["time"] + w[0])
    plt.xlabel("time (s)")
    plt.ylabel("Drift (nm)")
    plt.savefig(folderSave+"/"+name+".png")

    data["driftSmoof"] = w[1] * data["time"] + w[0]

    data["surfaceSepX"] = data["surfaceSepX"] + data["driftSmoof"]
    columns = [column for column in data.columns if (not "Unnamed" in column) and (not "drift" in column)]
    data[columns].to_csv(folderSave+"/"+name+".csv")
