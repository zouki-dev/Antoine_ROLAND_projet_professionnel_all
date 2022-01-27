import streamlit as st
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.ndimage import median_filter
from scipy.spatial.distance import cdist
from scipy.interpolate import *
from scipy.optimize import fmin_cobyla
from foldometer.tools.region_manipulation import get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting

from analysis_functionality.step_analysis.adjacent_sliding_windows_median_difference import adjacent_sliding_windows_median_difference
from scipy.optimize import curve_fit
from analysis_functionality.tools.str_analysis import int_to_000str
from copy import deepcopy
from analysis_functionality.tools.streamlit_wide_mode import wide_mode
from analysis_functionality.tools.str_analysis import str_extension_remove, compact_file_name

folderProject = 'S:/projects/Luca/dmMBP'
def step_analysis(folderProject=folderProject):
    folderData = folderProject + "/wlc_manual_fit"
    folderSave = folderProject + "/step_analysis"
    print("step_analysis")
    st.set_option('deprecation.showPyplotGlobalUse', False)

    if not os.path.exists(folderSave):
        os.mkdir(folderSave)
    # wide_mode()


    fileNameList = [os.path.splitext(fileName)[0] for fileName in os.listdir(folderData) if not "Power Spectrum" in fileName]
    fileNameShortList = [compact_file_name(fileName) for fileName in fileNameList if not "Power Spectrum" in fileName]
    fileNameTemp = st.sidebar.selectbox("Select your file", fileNameShortList)
    name = [name for (name, nameShort) in zip(fileNameList, fileNameShortList) if nameShort==fileNameTemp][0]

    SAVE = st.sidebar.button("Save")
    data = pd.read_csv(folderData + "/" + name + ".csv")

    if data["surfaceSepX"].mean()>2500:
        bpDNA = st.sidebar.number_input("bpDNA", None, None, 9000.)
    else:
        bpDNA = st.sidebar.number_input("bpDNA", None, None, 5000.)

    st.sidebar.header("Parameters to cut out steps")
    minDistance = st.sidebar.number_input("Minimum distance", 0, 100000, int((3200*bpDNA/10000)*0.95), step=50)
    maxForce = st.sidebar.number_input("Maximum force", 0, 100000, 60)
    maxDistance = st.sidebar.number_input("Maximum distance", 0, 100000, int((3700*bpDNA/10000)*1.025), step=10)
    maxTime = st.sidebar.number_input("Maximum time", 0, 100000, int(np.round(data["time"].max())), step=10)
    st.sidebar.header("Threshold")
    N_SIGMA_THRESHOLD = st.sidebar.number_input("Threshold: number of sigma", 0., 100000., 5., step=0.25)
    THRESHOLD_OFFSET = st.sidebar.number_input("THRESHOLD_OFFSET", 0., 100000., 3., step=0.2)
    WINDOW_SIZE = st.sidebar.number_input("WINDOW_SIZE", None,None, 31, step=1)

    maskMinDistance = data["surfaceSepX"] >= minDistance
    maskMaxForce = data["forceX"] <= maxDistance
    maskMaxDistance = data["surfaceSepX"] <= maxDistance
    maskMaxTime = data["time"] <= maxTime
    maskCondition = maskMaxForce * maskMinDistance * maskMaxDistance * maskMaxTime

    plt.plot(data["surfaceSepX"], savgol_filter(data["forceX"], 51, 1))
    plt.plot([minDistance, minDistance], [0, data["forceX"].max()], color="k")
    plt.plot([maxDistance, maxDistance], [0, data["forceX"].max()], color="k")
    plt.plot([minDistance, maxDistance], [maxForce, maxForce], color="k")
    st.pyplot()



    time = np.array(data["time"])
    Lc = np.array(data["proteinLc"])
    force = np.array(data["forceX"])
    diffLc = data["proteinLc"].diff()

    # plt.plot(data["proteinLc"])
    # plt.ylim((-200, 200))
    # st.pyplot()

    Lc_savgol = pd.DataFrame(savgol_filter(data["proteinLc"].loc[maskMinDistance], 51, 1))  # Savitzky-Golay filter
    # time_resample =
    # Lc_resample = data["proteinLc"].resample("Timedelta")

    diffLc_med_sliding_windows = adjacent_sliding_windows_median_difference(Lc)

    #------------------------------------Median filter----------------------------------------------------------------------
    def standard_deviation_estimation(f, aa=15, bb=-2.2):
        return aa / (f + bb)

    @st.cache(suppress_st_warning=True)
    def minimization_function(std_f_force_array, a, b):
        force = range(len(std_f_force_array))
        std_model = standard_deviation_estimation(force, a, b)
        return ((std_f_force_array - std_model) ** 2).mean()

    @st.cache(suppress_st_warning=True)
    def threshold_estimation(Lc, force):
        sizeWindow = WINDOW_SIZE
        Lc_median_filter = median_filter(Lc, size=sizeWindow)
        median_diff = Lc_median_filter[sizeWindow:] - Lc_median_filter[:-sizeWindow]  # median_diff_temp = Lc_median_filter[sizeWindow:] - Lc_median_filter[:-sizeWindow]
        # median_diff_tenp2 = np.concatenate([median_diff_temp[:sizeWindow] - median_diff_temp[sizeWindow:sizeWindow*2], median_diff_temp[:-sizeWindow] - median_diff_temp[sizeWindow:]])
        # median_diff = [(np.median(median_diff_tenp2[i-25:i]) - np.median(median_diff_tenp2[i+1:i+26])) * np.exp(-0.05*(np.median(median_diff_tenp2[i-25:i]) + np.median(median_diff_tenp2[i+1:i+26]))**2) for (i,y) in enumerate(median_diff_tenp2)]
        diffLc_median_filter = pd.DataFrame(np.concatenate([np.zeros(int(sizeWindow/2)), median_diff, np.zeros(int(sizeWindow/2)+1)]))

        ##---------------------------------threshold estimation---------------------------------------------------------------
        # The noise depend of the force. The threshold should depend of the force
        df = pd.DataFrame({"diffLc_median_filter": np.concatenate([np.zeros(int(sizeWindow/2)), median_diff, np.zeros(int(sizeWindow/2)+1)]),
                            "forceRound": [np.round(f, 0) for f in force]
                           })

        std_f_force = df.groupby(['forceRound']).std()
        std_f_force_array = [std_f_force.iloc[i - int(df["forceRound"].min())] for i in range(int(df["forceRound"].max()))]
        df["std_f_force"] = [std_f_force["diffLc_median_filter"].iloc[int(np.round(f, 0)) - int(df["forceRound"].min())].item() for f in force]
    #     return (diffLc_median_filter, df, std_f_force_array)
    # (diffLc_median_filter, df, std_f_force_array) = threshold_estimation(Lc, force)

        maskThresholdEstimation = (df["forceRound"]<=40) * (df["std_f_force"]<=200)

        plt.figure(figsize=(10,4))

        y = np.array(df["forceRound"].loc[maskMinDistance*maskThresholdEstimation])
        x = np.array(df["std_f_force"].loc[maskMinDistance*maskThresholdEstimation])

        maskNan = df["forceRound"].notna() * df["std_f_force"].notna()
        popt, pcov = curve_fit(minimization_function, xdata=df["forceRound"].loc[maskMinDistance*maskNan], ydata=df["std_f_force"].loc[maskMinDistance*maskNan], p0=[15, -2.2])
        [a, b] = popt

        return (diffLc_median_filter, a, b, df) # use a and b in standard_deviation_estimation(f, a=a, b=b) to get the treshold in function of Force

    (diffLc_median_filter, aa, bb, df) = threshold_estimation(Lc, force)
    forceStd = np.linspace(0, 70, 1000)
    thresholdStd = standard_deviation_estimation(forceStd, aa, bb)

    plt.plot(thresholdStd, forceStd,"r")
    plt.plot(df["std_f_force"].loc[maskMinDistance], df["forceRound"].loc[maskMinDistance], "b")
    plt.xlabel("Standard deviation (nm)")
    plt.ylabel("Force (pN)")
    plt.xlim((0,100))
    plt.ylim((0,40))
    st.pyplot()

    cycles = get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting(data)
    region_name = ["retracting", "stationary", "pulling", "nextRetracting"]

    column_names = ["dataName", "cycleNumber", "region", "deltaLc", "forceBefore", "forceAfter", "lcBefore", "lcAfter", "maxSustainableForce", "time"]
    listUnfolding = []
    threshold = None
    for (i, cycle) in enumerate(cycles):
        st.text("Cycle: "+str(i))
        (pullingCycle, _0, maskRetracting) = cycle["retracting"]
        (pullingCycle, _1, maskStationary) = cycle["stationary"]
        (pullingCycle, _2, maskPulling) = cycle["pulling"]
        (pullingCycle, _3, maskNextRetracting) = cycle["nextRetracting"]

        mask = (maskPulling + maskNextRetracting) * maskMinDistance
        maskConditionZoom = np.array(pd.DataFrame(maskCondition).loc[mask])
        if len(data["time"].loc[mask]) <= 51:
            continue

        threshold = standard_deviation_estimation(pd.DataFrame(savgol_filter(data["forceX"], 201, 1)).loc[mask], aa, bb) * N_SIGMA_THRESHOLD + THRESHOLD_OFFSET
        maskDetection = (diffLc_median_filter.loc[mask].abs() - threshold >= 0)


        plt.figure(figsize=(8,10))
        plt.subplot(411)
        plt.plot(data["time"].loc[mask], data["forceX"].loc[mask])
        plt.ylim((0, data["forceX"].loc[maskMinDistance].max()))
        plt.ylabel("Force (pN)")

        plt.subplot(412)
        plt.plot(data["time"].loc[mask], data["proteinLc"].loc[mask], color="lightgrey", zorder=0)
        plt.plot(data["time"].loc[mask], savgol_filter(data["proteinLc"].loc[mask], 51, 1), color="k", alpha=0.7, zorder=2)
        plt.ylim((data["proteinLc"].loc[maskMinDistance].min(), data["proteinLc"].loc[maskMinDistance].max()))
        plt.ylabel("Lc (nm)")

        indexDetection = np.where(maskDetection * maskConditionZoom)[0]
        # st.text(np.where(maskDetection * maskConditionZoom)[0])
        # st.text(indexDetection)
        if indexDetection != []:
            i_1 = -1
            indexUnfolding = []
            listIndexUnfolding = []
            for index in indexDetection:
                if index == i_1 + 1:
                    indexUnfolding.append(index)
                else:
                    listIndexUnfolding.append(deepcopy(indexUnfolding))
                    indexUnfolding = []
                    indexUnfolding.append(index)
                i_1 = index
            listIndexUnfolding.append(deepcopy(indexUnfolding))
            listIndexUnfolding = listIndexUnfolding[1:]


            wentInTheForLoop = False
            for IndexUnfolding in listIndexUnfolding:
                wentInTheForLoop = True
                maskUnfolding = [False for i in range(np.sum(mask))]
                st.text(IndexUnfolding)
                maskUnfolding[IndexUnfolding] = True
                plt.plot(data["time"].loc[mask].loc[maskUnfolding], data["proteinLc"].loc[mask].loc[maskUnfolding], "lightcoral", zorder=1)



                maskBeforeUnfolding = np.zeros(len(data["time"].loc[mask]), dtype=bool)
                maskBeforeUnfolding[min(IndexUnfolding)-100:min(IndexUnfolding)] = True

                maskAfterUnfolding = np.zeros(len(data["time"].loc[mask]), dtype=bool)
                maskAfterUnfolding[max(IndexUnfolding):max(IndexUnfolding)+100] = True

                forceBefore = data["forceX"].loc[mask].loc[maskBeforeUnfolding].mean()
                lcBefore = data["proteinLc"].loc[mask].loc[maskBeforeUnfolding].mean()
                forceAfter = data["forceX"].loc[mask].loc[maskAfterUnfolding].mean()
                lcAfter = data["proteinLc"].loc[mask].loc[maskAfterUnfolding].mean()
                deltaLc = lcAfter - lcBefore
                region = data["region"].loc[mask].loc[maskUnfolding].head(1).item()
                time = data["time"].loc[mask].loc[maskBeforeUnfolding].mean()

                if region == "pulling":
                    maxSustainableForce = forceBefore
                elif region == "retracting":
                    maxSustainableForce = data["forceX"].loc[mask].max()
                else:
                    maxSustainableForce = forceBefore

                # unfolding = {"dataName": name,
                #              "cycleNumber": i,
                #              "region": region,
                #              "deltaLc": deltaLc,
                #              "forceBefore": forceBefore,
                #              "forceAfter": forceAfter,
                #              "lcBefore": lcBefore,
                #              "lcAfter": lcAfter,
                #              "maxSustainableForce": maxSustainableForce}
                unfolding = [name, i, region, deltaLc, forceBefore, forceAfter, lcBefore, lcAfter, maxSustainableForce, time]
                listUnfolding.append(unfolding)


        else: # if it didnt go once in the loop for it needs to create a line in dfUnfolding to account for the cycle
            forceMean = data["forceX"].loc[mask].max()
            lcMean = data["proteinLc"].loc[mask].loc[(data["forceX"]>=15)*(data["forceX"]<=30)].mean()
                # noUnfolding = {"dataName": name,
                #              "cycleNumber": i,
                #              "region": "pulling",
                #              "deltaLc": 0,
                #              "forceBefore": forceMean,
                #              "forceAfter": forceMean,
                #              "lcBefore": lcMean,
                #              "lcAfter": lcMean,
                #              "maxSustainableForce": forceMean}
            noUnfolding = [name, i, "pulling", 0, forceMean, forceMean, lcMean, lcMean, forceMean]
            listUnfolding.append(noUnfolding)

        plt.subplot(413)
        plt.plot(np.array(data["time"].loc[mask]), np.array(threshold), "r")
        plt.plot(np.array(data["time"].loc[mask]), np.array(-threshold), "r")
        plt.plot(np.array(data["time"].loc[mask]), np.array(diffLc_median_filter.loc[mask]), "yellowgreen")
        plt.ylim(( float(diffLc_median_filter.loc[maskMinDistance].min()), float(diffLc_median_filter.loc[maskMinDistance].max()) ))
        plt.ylabel("median filter diff (nm)")

        plt.subplot(414)
        plt.plot(np.array(data["time"].loc[mask]), np.array(maskDetection * maskConditionZoom), color="r")
        plt.ylim((-0.1, 1.1))
        plt.xlabel("Time (s)")
        plt.ylabel("Step Detected (bool)")



        if SAVE:
            if not os.path.exists(folderSave+"/figure"):
                os.mkdir(folderSave+"/figure")
            plt.savefig(folderSave+"/figure"+"/"+name+"_"+int_to_000str(i)+".png")

        st.pyplot()


    dfUnfolding = pd.DataFrame(listUnfolding, columns=column_names)
    allUnfolding = []
    st.sidebar.header("Select unfolding events")
    num = 0
    for cycleNumber in dfUnfolding["cycleNumber"].unique():
        st.sidebar.text("cycle: "+str(cycleNumber))
        mask = dfUnfolding["cycleNumber"] == cycleNumber
        for index, unfolding in dfUnfolding.loc[mask].iterrows():
            bool = st.sidebar.checkbox(str(num)+" "+str(round(unfolding["time"], 2))+"s    " + str(round(unfolding["forceBefore"], 2))+"pN    " + str(round(unfolding["deltaLc"], 2))+"nm", True)
            num += 1
            if bool:
                allUnfolding.append(unfolding)
    dfAllUnfolding = pd.DataFrame(allUnfolding)
    st.dataframe(dfAllUnfolding)
    if SAVE:
        dfAllUnfolding.to_csv(folderSave + "/" + name + ".csv")
        st.balloons()

if __name__ == '__main__':
    step_analysis()
