from foldometer.tools.region_manipulation import get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting, get_cycle_region_time_sorted
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import streamlit as st
from scipy.signal import savgol_filter
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
from analysis_functionality.tools.str_analysis import int_to_000str, str_extension_remove
from analysis_functionality.tools.str_analysis import compact_file_name

folderProject = 'D:/projects/ubiquitin_20211125'
def all_figure(folderProject=folderProject):
    st.title("Click on 'Make figure' on the left sidebar !")
    folderProject = st.text_input("folderProject:", folderProject)
    folderData = folderProject + "/" + "wlc_manual_fit"
    folderFigure = folderProject + "/" + "all_figure"
    # rulersDefault = [0, 130, 140, 150, 160, 170, 180, 190, 200, 1500]
    rulersDefault = None

    st.set_option('deprecation.showPyplotGlobalUse', False)


    if not os.path.exists(folderFigure):
        os.mkdir(folderFigure)

    allNames = [name[:-4] for name in os.listdir(folderData) if ".csv" in name]

    from analysis_functionality.tools.str_analysis import int_to_000str

    st.sidebar.header("Select data:")

    if st.sidebar.checkbox("select_data", False):
        dates = [name[:8] for name in allNames]
        experiments = [name[16:name.find("#")-1] for name in allNames]
        strExperiment = ""
        for date in set(dates):
            strExperiment += date + ", "
        strExperiment = strExperiment[:-1]
        keywordsListStr = st.text_input("Select all fileName containing one of those str.", strExperiment)
        keywordsList = keywordsListStr.replace(" ","").split(",")

        names = [name for name in allNames if any([keyword in name for keyword in keywordsList])]
        names = set(names)

        allNamesCompact = [compact_file_name(name) for name in names]
        namesCompact = st.multiselect("Select data ("+str(len(allNamesCompact))+"):", allNamesCompact, allNamesCompact)
        names = [name for (name, nameCompact) in zip(names, allNamesCompact) if nameCompact in namesCompact]
    else:
        names = allNames

    st.sidebar.header("------------ Click Here: ------------")
    isMakeFigure = st.sidebar.button("------------ Make figure ------------")

    st.sidebar.subheader("All the molecule")
    FORCE_EXTENSION = st.sidebar.checkbox("Force_Extension", True)
    FORCE_LC = st.sidebar.checkbox("Force_Lc", False)
    LC_TIME = st.sidebar.checkbox("Lc_Time", False)
    LC_FORCE_TIME = st.sidebar.checkbox("Lc+Force_Time", False)

    st.sidebar.subheader("Split cycle")
    SPLITCYCLE_FORCE_EXTENSION = st.sidebar.checkbox("Force_Extension_SplitCycle", False)
    SPLITCYCLE_FORCE_LC = st.sidebar.checkbox("Force_Lc_SplitCycle", True)
    SPLITCYCLE_LC_TIME = st.sidebar.checkbox("Lc_Time_SplitCycle", False)
    SPLITCYCLE_LC_FORCE_TIME = st.sidebar.checkbox("Lc+Force_Time_SplitCycle", False)

    st.sidebar.subheader("Dynamic figures")
    st.sidebar.text("more than 10 dynamic figures might crah. Use select_data")
    DYNAMIC_LC_TIME = st.sidebar.checkbox("Dynamic_Lc_Time", False)

    st.sidebar.subheader("Your figures")
    KATHY_PRECIOUS = st.sidebar.checkbox("Kathy's PRECIOUS", False)

    figs, axs = ([None for i in range(100000)], [None for i in range(100000)])
    iFig = 0
    if isMakeFigure:
        parameters = pd.read_csv(folderProject + "/wlc_manual_fit.csv")
        for (iName ,name) in enumerate(names):
            st.header(name)
            data = pd.read_csv(folderData+"/"+name+".csv")
            parameter = parameters.loc[parameters["fileName"] == name].iloc[[-1]]
            if rulersDefault==None:
                rulersStr = parameters["rulers"].loc[parameters["fileName"] == name].iloc[-1]
                rulers = [float(length) for length in rulersStr.replace("]","").replace("[","").replace(" ","").split(",")]
            else:
                rulers = rulersDefault

            cycles = get_cycle_region_time_sorted(data)  # list of dico 'retracting' 'stationary' 'pulling' 'nextRetracting'

            if FORCE_EXTENSION:
                figs[iFig], axs[iFig] = plt.subplots()
                st.subheader("FORCE_EXTENSION")
                forceArray = np.arange(0.5, 60, 0.2)
                for length in rulers:
                    plt.plot(wlc_series_accurate(forceArray, \
                                                 parameter["contourLengthDNA"].item(), \
                                                 parameter["persistenceLengthDNA"].item(), \
                                                 parameter["stretchModulusDNA"].item(), \
                                                 length, \
                                                 parameter["persistenceLengthProtein"].item(), \
                                                 ), forceArray, color="gray", zorder=0)

                st.subheader("All the molecule")

                pullingCycles = len(data["pullingCycle"].unique())
                palettes = {"pulling": sns.color_palette("PuBu_d", pullingCycles), \
                            "retracting": sns.color_palette("YlOrRd_d", pullingCycles), \
                            "stationary": sns.color_palette("Greens_d", pullingCycles)}
                for cycle in cycles:
                    (pullingCycle, region, mask) = cycle
                    plt.plot(data["surfaceSepX"].loc[mask], data["forceX"].loc[mask], "lightgrey", linewidth=0.5, zorder=0)
                    if np.sum(mask)>=51:
                        plt.plot(savgol_filter(data["surfaceSepX"].loc[mask], 51, 1), savgol_filter(data["forceX"].loc[mask], 51, 1), "k", linewidth=0.5, color=palettes[region][pullingCycle], label=str(pullingCycle)+" "+region, zorder=1)

                #legend
                handles, labels = plt.gca().get_legend_handles_labels()
                valuesHandles = []
                labelsHandles = []
                for (handle, label) in zip(handles, labels):
                    if "pulling" in label:
                        valuesHandles.append(handle)
                        labelsHandles.append(label)
                for (handle, label) in zip(handles, labels):
                    if "retracting" in label:
                        valuesHandles.append(handle)
                        labelsHandles.append(label)
                for (handle, label) in zip(handles, labels):
                    if "stationary" in label:
                        valuesHandles.append(handle)
                        labelsHandles.append(label)
                # plt.legend(valuesHandles, labelsHandles)
                plt.xlabel("Extension (nm)")
                plt.ylabel("Force (pN)")

                if not os.path.exists(folderFigure+"/"+"FORCE_EXTENSION"):
                    os.mkdir(folderFigure+"/"+"FORCE_EXTENSION")
                plt.savefig(folderFigure+"/"+"FORCE_EXTENSION"+"/"+name+".png")
                st.pyplot(figs[iFig])
                iFig += 1


            if FORCE_LC:
                figs[iFig], axs[iFig] = plt.subplots()
                st.subheader("FORCE_LC")
                nbPullingCycle = np.max([pullingCycle for (pullingCycle, region, mask) in cycles]) +1
                palettes = {"pulling": sns.color_palette("PuBu_d", nbPullingCycle), \
                            "retracting": sns.color_palette("YlOrRd_d", nbPullingCycle), \
                            "stationary": sns.color_palette("Greens_d", nbPullingCycle)}
                for cycle in cycles:
                    (pullingCycle, region, mask) = cycle
                    maskForce = data["forceX"] >= 2
                    plt.plot(data["proteinLc"].loc[mask], data["forceX"].loc[mask], "lightgrey", linewidth=0.5, zorder=0)
                    if len(data["proteinLc"].loc[maskForce*mask])>=51:
                        plt.plot(savgol_filter(data["proteinLc"].loc[maskForce*mask], 51, 1),
                             savgol_filter(data["forceX"].loc[maskForce*mask], 51, 1), linewidth=0.5,
                             color=palettes[region][pullingCycle], label=region+" "+str(pullingCycle), zorder=1)
                for ruler in rulers:
                    plt.plot([ruler, ruler], [0,60], color="grey")
                plt.xlim((-20, rulers[-1]+20))

                handles, labels = plt.gca().get_legend_handles_labels()
                valuesHandles = []
                labelsHandles = []
                for (handle, label) in zip(handles, labels):
                    if "pulling" in label:
                        valuesHandles.append(handle)
                        labelsHandles.append(label)
                for (handle, label) in zip(handles, labels):
                    if "retracting" in label:
                        valuesHandles.append(handle)
                        labelsHandles.append(label)
                for (handle, label) in zip(handles, labels):
                    if "stationary" in label:
                        valuesHandles.append(handle)
                        labelsHandles.append(label)
                # plt.legend(valuesHandles, labelsHandles)
                plt.xlabel("Protein contour length Lc (nm)")
                plt.ylabel("Force (pN)")

                if not os.path.exists(folderFigure+"/"+"FORCE_LC"):
                    os.mkdir(folderFigure+"/"+"FORCE_LC")
                plt.savefig(folderFigure+"/"+"FORCE_LC"+"/"+name+".png")
                st.pyplot(figs[iFig])
                iFig += 1


            if LC_TIME:
                figs[iFig], axs[iFig] = plt.subplots()
                st.subheader("LC_TIME")
                maskForce = data["forceX"] >= 3
                plt.plot(data["time"], data["proteinLc"], color="silver")
                if np.sum(maskForce)>51:
                    plt.plot(data["time"].loc[maskForce] , savgol_filter(data["proteinLc"].loc[maskForce],51,1), color="firebrick")
                plt.ylim(-20, (rulers[-1])+20)
                plt.xlabel("Time (s)")
                plt.ylabel("Protein contour length Lc (nm)")

                if not os.path.exists(folderFigure + "/" + "LC_TIME"):
                    os.mkdir(folderFigure + "/" + "LC_TIME")
                plt.savefig(folderFigure + "/" + "LC_TIME" + "/" + name + ".png")
                st.pyplot(figs[iFig])
                iFig += 1


            if LC_FORCE_TIME:
                figs[iFig], axs[iFig] = plt.subplots()
                st.subheader("LC_FORCE_TIME")
                plt.subplot(211)
                plt.plot(data["time"], data["forceX"])
                plt.xticks([])
                plt.ylabel("Force (pN)")
                plt.subplot(212)
                maskForce = data["forceX"] >= 3
                plt.plot(data["time"], data["proteinLc"], color="silver")
                plt.plot(data["time"].loc[maskForce] , savgol_filter(data["proteinLc"].loc[maskForce],51,1), color="firebrick")
                plt.ylim(-20, (rulers[-1])+20)
                plt.xlabel("Time (s)")
                plt.ylabel("Protein contour length Lc (nm)")

                if not os.path.exists(folderFigure + "/" + "LC_TIME"):
                    os.mkdir(folderFigure + "/" + "LC_TIME")
                plt.savefig(folderFigure + "/" + "LC_TIME" + "/" + name + ".png")
                st.pyplot(figs[iFig])
                iFig += 1


            cycles = get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting(data)  # list of dico 'retracting' 'stationary' 'pulling' 'nextRetracting'
            pullingCycles = len(data["pullingCycle"].unique())
            palettes = {"pulling": sns.color_palette("PuBu_d", pullingCycles), \
                        "retracting": sns.color_palette("YlOrRd_d", pullingCycles), \
                        "stationary": sns.color_palette("Greens_d", pullingCycles)}


            if SPLITCYCLE_FORCE_EXTENSION:
                st.subheader("SPLITCYCLE_FORCE_EXTENSION")
                for (cycleNumber, cycle) in enumerate(cycles):
                    figs[iFig], axs[iFig] = plt.subplots()
                    plt.plot(data["surfaceSepX"].loc[cycle["retracting"][2]], data["forceX"].loc[cycle["retracting"][2]], color="r", label="Previous retracting "+str(cycle["retracting"][0]))
                    plt.plot(data["surfaceSepX"].loc[cycle["stationary"][2]], data["forceX"].loc[cycle["stationary"][2]], color="g", label="Stationary "+str(cycle["stationary"][0]))
                    plt.plot(data["surfaceSepX"].loc[cycle["pulling"][2]], data["forceX"].loc[cycle["pulling"][2]], color="b", label="Pulling "+str(cycle["pulling"][0]))
                    plt.plot(data["surfaceSepX"].loc[cycle["nextRetracting"][2]], data["forceX"].loc[cycle["nextRetracting"][2]], color="purple", label="Next retracting "+str(cycle["nextRetracting"][0]))

                    handles, labels = plt.gca().get_legend_handles_labels()
                    valuesHandles = []
                    labelsHandles = []
                    for (handle, label) in zip(handles, labels):
                        if "-1" not in label:
                            valuesHandles.append(handle)
                            labelsHandles.append(label)
                    plt.legend(valuesHandles, labelsHandles)
                    plt.xlabel("Extension (nm)")
                    plt.ylabel("Force (pN)")

                    forceArray = np.arange(0.5, 60, 0.2)
                    for length in rulers:
                        plt.plot(wlc_series_accurate(forceArray, \
                                                     parameter["contourLengthDNA"].item(), \
                                                     parameter["persistenceLengthDNA"].item(), \
                                                     parameter["stretchModulusDNA"].item(), \
                                                     length, \
                                                     parameter["persistenceLengthProtein"].item(), \
                                                     ), forceArray, color="gray", zorder=0)

                    if not os.path.exists(folderFigure + "/" + "SPLITCYCLE_FORCE_EXTENSION"):
                        os.mkdir(folderFigure + "/" + "SPLITCYCLE_FORCE_EXTENSION")
                    plt.savefig(folderFigure + "/" + "SPLITCYCLE_FORCE_EXTENSION" + "/" + name + "_" +  int_to_000str(cycleNumber) + ".png")
                    st.pyplot(figs[iFig])
                    iFig += 1


            if SPLITCYCLE_FORCE_LC:
                st.subheader("SPLITCYCLE_FORCE_LC")
                for cycle in cycles:
                    figs[iFig], axs[iFig] = plt.subplots()
                    for length in rulers:
                        plt.plot([length, length], [0, 60], color="gray", zorder=0)
                    (pullingCycleRetracting, regionRetracting, maskRetracting) = cycle["retracting"]
                    maskForce = data["forceX"]>=2
                    # mask = maskRetracting * maxForceForPreviousRetracting
                    plt.plot(data["proteinLc"].loc[maskRetracting], data["forceX"].loc[maskRetracting], \
                             color="r", label=regionRetracting + " " + str(pullingCycleRetracting))
                    (pullingCycleStationary, regionStationary, maskStationary) = cycle["stationary"]
                    plt.plot(data["proteinLc"].loc[maskStationary], data["forceX"].loc[maskStationary], \
                             color="g", label=regionStationary + " " + str(pullingCycleStationary))
                    (pullingCyclePulling, regionPulling, maskPulling) = cycle["pulling"]
                    plt.plot(data["proteinLc"].loc[maskPulling], data["forceX"].loc[maskPulling], \
                             color="b", label=regionPulling + " " + str(pullingCyclePulling))
                    (pullingCycleNextRetracting, regionNextRetracting, maskNextRetracting) = cycle["nextRetracting"]
                    # mask = maskRetracting * maskForceNextRetracting
                    plt.plot(data["proteinLc"].loc[maskNextRetracting], data["forceX"].loc[maskNextRetracting], \
                             color="m", label=regionNextRetracting + " " + str(pullingCycleNextRetracting))
                    maskCycle = maskPulling+maskNextRetracting+maskStationary
                    if sum(maskCycle*maskForce)>=51:
                        plt.plot(savgol_filter(data["proteinLc"].loc[maskCycle*maskForce],51,1), savgol_filter(data["forceX"].loc[maskCycle*maskForce],51,1), \
                             color="k", label=regionNextRetracting + " " + str(pullingCycleNextRetracting))

                    plt.xlim((rulers[0] - 50, rulers[-1] + 50))
                    plt.legend(loc="upper left")
                    plt.xlabel("Protein contour length Lc (nm)")
                    plt.ylabel("Force (pN)")
                    plt.tick_params(axis='x', labelsize=14)
                    plt.tick_params(axis='y', labelsize=14)

                    if not os.path.exists(folderFigure + "/" + "SPLITCYCLE_FORCE_LC"):
                        os.mkdir(folderFigure + "/" + "SPLITCYCLE_FORCE_LC")
                    plt.savefig(folderFigure + "/" + "SPLITCYCLE_FORCE_LC" + "/" + name + "_" +  int_to_000str(pullingCyclePulling) + ".png")
                    st.pyplot(figs[iFig])
                    iFig += 1


            if SPLITCYCLE_LC_TIME:
                st.subheader("SPLITCYCLE_LC_TIME")
                for cycle in cycles:
                    figs[iFig], axs[iFig] = plt.subplots()
                    (pullingCycleRetracting, regionRetracting, maskRetracting) = cycle["retracting"]
                    maskForce = data["forceX"]>=2
                    (pullingCycleRetracting, regionRetracting, maskRetracting) = cycle["retracting"]
                    (pullingCyclePulling, regionPulling, maskPulling) = cycle["pulling"]
                    (pullingCycleStationary, regionStationary, maskStationary) = cycle["stationary"]
                    (pullingCycleNextRetracting, regionNextRetracting, maskNextRetracting) = cycle["nextRetracting"]
                    maskCycle = maskPulling+maskNextRetracting+maskStationary
                    maskForce = data["forceX"]>=2
                    plt.plot(data["time"].loc[maskCycle], data["proteinLc"].loc[maskCycle], \
                             color="silver")
                    if sum(maskCycle*maskForce)>=51:
                        plt.plot(savgol_filter(data["time"].loc[maskCycle*maskForce],51,1), savgol_filter(data["proteinLc"].loc[maskCycle*maskForce],51,1), \
                             color="k", label=regionNextRetracting + " " + str(pullingCycleNextRetracting))


                    for length in rulers:
                        plt.plot((data["time"].loc[maskPulling].min(), data["time"].loc[maskPulling].max()), [length, length], color="gray", zorder=0)
                    plt.ylim((-20, rulers[-1]+20))
                    plt.tick_params(axis='x', labelsize=14)
                    plt.tick_params(axis='y', labelsize=14)
                    plt.xlabel("Time (s)")
                    plt.ylabel("Protein contour length Lc (nm)")

                    if not os.path.exists(folderFigure + "/" + "SPLITCYCLE_LC_TIME"):
                        os.mkdir(folderFigure + "/" + "SPLITCYCLE_LC_TIME")
                    plt.savefig(folderFigure + "/" + "SPLITCYCLE_LC_TIME" + "/" + name + "_" +  int_to_000str(pullingCyclePulling) + ".png")
                    st.pyplot(figs[iFig])
                    iFig += 1


            if SPLITCYCLE_LC_FORCE_TIME:
                st.subheader("SPLITCYCLE_LC_FORCE_TIME")
                for cycle in cycles:
                    figs[iFig], axs[iFig] = plt.subplots()
                    (pullingCycleRetracting, regionRetracting, maskRetracting) = cycle["retracting"]
                    (pullingCyclePulling, regionPulling, maskPulling) = cycle["pulling"]
                    (pullingCycleStationary, regionStationary, maskStationary) = cycle["stationary"]
                    (pullingCycleNextRetracting, regionNextRetracting, maskNextRetracting) = cycle["nextRetracting"]
                    maskCycle = maskPulling+maskNextRetracting+maskStationary
                    ax1 = plt.subplot(411)
                    plt.plot(data["time"].loc[maskCycle], data["forceX"].loc[maskCycle])
                    plt.xticks([])
                    plt.ylabel("Force (pN)")

                    ax2 = plt.subplot(4,1,(2,4))
                    maskForce = data["forceX"]>=2
                    plt.plot(data["time"].loc[maskCycle], data["proteinLc"].loc[maskCycle], \
                             color="silver", zorder=0)
                    if sum(maskCycle*maskForce)>=51:
                        plt.plot(savgol_filter(data["time"].loc[maskCycle*maskForce],51,1), savgol_filter(data["proteinLc"].loc[maskCycle*maskForce],51,1), \
                             color="k", label=regionNextRetracting + " " + str(pullingCycleNextRetracting), zorder=2)
                    plt.xlim((data["time"].loc[maskCycle].min(), data["time"].loc[maskCycle].max()))

                    for length in rulers:
                        plt.plot((data["time"].loc[maskCycle].min(), data["time"].loc[maskCycle].max()), [length, length], color="b", zorder=1)
                    plt.ylim((-20, rulers[-1]+20))
                    plt.tick_params(axis='x', labelsize=14)
                    plt.tick_params(axis='y', labelsize=14)
                    plt.xlabel("Time (s)")
                    plt.ylabel("Protein contour length Lc (nm)")

                    if not os.path.exists(folderFigure + "/" + "SPLITCYCLE_LC_FORCE_TIME"):
                        os.mkdir(folderFigure + "/" + "SPLITCYCLE_LC_FORCE_TIME")
                    plt.savefig(folderFigure + "/" + "SPLITCYCLE_LC_FORCE_TIME" + "/" + name + "_" +  int_to_000str(pullingCyclePulling) + ".png")
                    st.pyplot(figs[iFig])
                    iFig += 1

            if KATHY_PRECIOUS:
                figs[iFig], axs[iFig] = plt.subplots()
                minTimePoint = data['time'].min()
                maxTimePoint = data['time'].max()
                order = 1
                window = 51
                savgol = lambda x: savgol_filter(x, window, order)
                force = (data["PSD2ForceX"] - data["PSD1ForceX"]) / 2
                fig, ax1 = plt.subplots()
                ax1.plot(data["time"], data["proteinLc"], 'grey', zorder=0, linewidth=0.5)
                ax1.plot(data["time"], savgol(data["proteinLc"].interpolate("linear")), 'k', zorder=2, linewidth=0.5)  # 348ABD
                ax1.set_ylabel("Protein Contour Length (nm)", color='#348ABD')
                ax2 = ax1.twinx()
                ax2.plot(data["time"], force, '#E24A33', zorder=0, linewidth=0.5)
                ax2.set_ylabel("PSD2Force (pN)", color='#E24A33')
                ax2.set_xlabel("Time (s)")
                ax1.set_ylim(-10, rulers[-1]+10)
                ax2.set_ylim(-10, 70)
                ax2.set_xlim(minTimePoint, maxTimePoint)
                fig.tight_layout()
                plt.hlines(83.3, 0, max(data["time"]), colors='k', linestyles='dashdot',
                           label='Estimated protein contour length')
                plt.grid()

                if not os.path.exists(folderFigure + "/" + "KATHY_PRECIOUS"):
                    os.mkdir(folderFigure + "/" + "KATHY_PRECIOUS")
                plt.savefig(folderFigure + "/" + "KATHY_PRECIOUS" + "/" + name + ".png")
                plt.savefig(folderFigure + "/" + "KATHY_PRECIOUS" + "/" + name + ".pdf")
                st.pyplot(figs[iFig])
                iFig += 1

            from bokeh.plotting import figure
            from bokeh.models import Range1d

            if DYNAMIC_LC_TIME:
                figs[iFig], axs[iFig] = plt.subplots()
                if "figDynLcTime" in locals():
                    makeTheFigList = False
                else:
                    makeTheFigList = True
                if makeTheFigList:
                    figDynLcTime = [None for i in range(len(names))]

                maskForce = data["forceX"] >= 2

                figDynLcTime[iName] = figure(title=name, x_axis_label='Time (s)',
                                             y_axis_label='Protein contour Length (nm)')
                figDynLcTime[iName].line(data["time"], data["proteinLc"], legend_label='Trend', line_width=2,
                                         color="lightGrey")
                figDynLcTime[iName].line(data["time"].loc[maskForce],
                                         savgol_filter(data["proteinLc"].loc[maskForce], 51, 1), legend_label='Trend',
                                         line_width=2, color="red")
                figDynLcTime[iName].y_range = Range1d(-30, rulers[-1] + 30)

                st.bokeh_chart(figDynLcTime[iName])
                # st.text(figDynLcTime[iName])
                st.pyplot(figs[iFig])
                iFig += 1
        st.balloons()
    return

if __name__ == '__main__':
    all_figure()
