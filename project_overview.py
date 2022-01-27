import os
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from analysis_functionality.tools.str_analysis import make_experiment_name
import random
from copy import deepcopy
import seaborn as sns
from foldometer.ixo.lumicks_c_trap import process_lumicks_data
from analysis_functionality.wlc_manual_fit.load import get_calibration_from_power_spectrum

folderTeam = "S:/projects"
folderProject = 'S:/projects/Luca/dmMBP'
def project_overview(folderTeam=folderTeam, folderProject=folderProject):
    proteinLength = st.sidebar.number_input("protein Length", None, None, 150.)

    user = folderProject.split("/")[-2]

    humans = [human for human in os.listdir(folderTeam) if "." not in human]
    human = st.sidebar.selectbox("Who is the human ?", humans, humans.index(user))
    folderProjects = folderTeam + "/" + human

    projectAll = [project for project in os.listdir(folderProjects) if "." not in project]
    projects = st.sidebar.multiselect("What project ?", projectAll, folderProject.split("/")[-1])
    foldersProject = [folderProjects + "/" + project for project in projects]


    FUSE_ANALYSED_PROJECT = st.sidebar.checkbox("Fuse sub projects (Run alone)")
    SHOW_NUMBERS_OF_FILE = st.sidebar.checkbox("Show numbers of file")
    SHOW_NOT_FITTED_DATA = st.sidebar.button("Show not fitted data")

    st.sidebar.header("Histograms on each project selected")

    HIST_Fu_Lc_DeltaLc = st.sidebar.checkbox("Fu - Lc -DeltaLc")
    HIST_Fu_Lc_DeltaLcLinks = st.sidebar.checkbox("Fu - Lc -DeltaLc - links cycle")
    HIST_Fu_DeltaLc = st.sidebar.checkbox("Fu - DeltaLc")
    HIST_UNFOLDING_LENGTH = st.sidebar.checkbox("Unfolding length")

    HIST_REFOLDING_RATE = st.sidebar.checkbox("Refolding rate")
    HIST_REFOLDING_RATE_BEFORE_AFTER = st.sidebar.checkbox("Refolding rate 2d, before - after")
    HIST_REFOLDING_RATE_BEFORE_DELTA = st.sidebar.checkbox("Refolding rate 2d, before - delta")
    if HIST_REFOLDING_RATE:
        st.text("It will take value of only refolding from fully unfolded")
        thresholdUnfolded = st.number_input("Fully unfolded if x >= ?", None, None, proteinLength*0.7)

    st.sidebar.header("Unfolding landscape")
    UNFOLDING_PATTERN = st.sidebar.checkbox("Unfolding pattern")
    STATE_DENSITY_MAP = st.sidebar.checkbox("State density map")

    st.sidebar.header("Compare histogram (run alone)")
    COMPARE_1D = st.sidebar.checkbox("1d hist with several data set")
    COMPARE_2D = st.sidebar.checkbox("2d hist with several data set")


    indexFigure=0
    figs = [None for i in range(10000)]
    axs = [None for i in range(10000)]
    for (folderProject, project) in zip(foldersProject, projects):
        folderStepAnalysis = folderProject + "/" + "step_analysis"
        folderWlc = folderProject + "/" + "wlc_manual_fit"
        folderSave = folderProject + "/" + "project_overview"

        # ____________________________________ create the folder where to save ________________________________________
        if not os.path.exists(folderSave):
            os.mkdir(folderSave)
        if not os.path.exists(folderSave+"/"+project):
            os.mkdir(folderSave+"/"+project)
        st.header("Projects: "+folderProject.split("/")[-1])

        # ________________________________________________ File counting ________________________________________________
        try:
            filesWlcFit = os.listdir(folderWlc)
            filesCsvRaw = [filePath for filePath in os.listdir(folderProject+"/csv_raw_data") if "Power Spectrum" not in filePath]
            filesStepAnalysed = [filePath for filePath in os.listdir(folderStepAnalysis) if ".csv" in filePath]
            filesRaw = list()
            for (dirpath, dirnames, filenames) in os.walk(folderProject+"/raw_data"):
                filesRaw += [os.path.join(dirpath, file) for file in filenames if (".tdms" in file or ".h5" in file) and "Power Spectrum" not in file and "fluo" not in dirpath and not "_index" in file]
            nbRawFile = len(filesRaw)
            nbFiles = len(filesWlcFit)
            nbCsvRawFile = len(filesRaw)
            nbStepAnalyis = len(filesStepAnalysed)

            if SHOW_NUMBERS_OF_FILE:
                st.text("There are "+str(nbRawFile)+" in raw_data")
                st.text("There are "+str(nbCsvRawFile)+" in csv_raw_data")
                st.text("There are "+str(nbFiles)+" in wlc_manual_fit")
                st.text("There are "+str(nbFiles)+" in step_analysis")
        except:
            st.warning(folderWlc +" doesn't exist or" +"\n"+folderStepAnalysis +" doesn't exist")

        # ____________________________________ Read all step_analysis/XXXX_data.csv ________________________________________
        # csvFiles = [fileName[:-4] for fileName in os.listdir(folderProject) if ".csv" in fileName]
        # folders = [base for base in os.listdir(folderProject) if os.path.isdir(folderProject+"/"+base)]

        namesAll = [name[:-4] for name in os.listdir(folderStepAnalysis) if ".csv" in name]
        experiments = list(np.unique([make_experiment_name(name) for name in namesAll]))
        if SHOW_NUMBERS_OF_FILE:
            experimentsSelected = st.multiselect("Select a subsection of the data (nb exp = "+str(len(experiments))+")", experiments, default=experiments)
        else:
            experimentsSelected = experiments
        experimentDay = np.unique([experiment[:8] for experiment in experimentsSelected])
        experimentName = np.unique([experiment[9:] for experiment in experimentsSelected])

        names = [name for name in namesAll if name[:8] in experimentDay and name[16:-9] in experimentName]

        unfoldingCyclesList = None
        for name in names:
            if unfoldingCyclesList is None:
                unfoldingCyclesList = pd.read_csv(folderStepAnalysis+"/"+name+".csv")
            else:
                pd.concat([unfoldingCyclesList,pd.read_csv(folderStepAnalysis+"/"+name+".csv")])
        columns = ['dataName', 'cycleNumber', 'region', 'deltaLc', 'forceBefore', 'forceAfter', 'lcBefore', 'lcAfter', 'maxSustainableForce', 'time']
        unfoldingCyclesList = unfoldingCyclesList[columns]
        nbCycles = len(unfoldingCyclesList)




        # ____________________________________ Buttons actions ________________________________________
        if SHOW_NUMBERS_OF_FILE:
            st.text("There are "+str(nbCycles)+" cycle state in the csv of step_analysis")


        if SHOW_NOT_FITTED_DATA:
            namesCsv = [name[:-4] for name in os.listdir(folderProject+"/"+"csv_raw_data") if "Power Spectrum" not in name]
            namesNotFitted = [name for name in namesCsv if name not in names]
            for name in namesNotFitted:
                st.text(name)
                data = pd.read_csv(folderProject+"/"+"csv_raw_data"+"/"+name+".csv")
                thermalCalibration = get_calibration_from_power_spectrum(folderProject+"/"+"csv_raw_data", name)
                dataProcess = process_lumicks_data(data, thermalCalibration)

                figs[indexFigure], axs[indexFigure] = plt.subplots()
                plt.plot(dataProcess["surfaceSepX"], dataProcess["forceX"])
                st.pyplot(figs[indexFigure])
                indexFigure+=1


        if HIST_Fu_Lc_DeltaLc:
            df = unfoldingCyclesList
            mask = df["deltaLc"]>0
            maxLc = np.max(unfoldingCyclesList["lcAfter"])
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            sc = plt.scatter(np.array(df["lcBefore"].loc[mask]), np.array(df["maxSustainableForce"].loc[mask]), s=df["deltaLc"].loc[mask]+1, alpha=0.5)
            plt.legend(*sc.legend_elements("sizes", num=6))
            plt.xlabel("Contour length (nm)")
            plt.ylabel("Unfolding force (pN)")
            plt.ylim((0,67))
            xmin = st.number_input("xmin", None, None, 0)
            xmax = st.number_input("xmax", None, None, df["lcBefore"].loc[mask].max()+10)
            plt.xlim((xmin, xmax))
            plt.savefig(folderSave+"/"+project+"/"+"lcBefore_UnfoldingForce_UnfoldingLength"+".png")
            st.pyplot(figs[indexFigure])
            st.text("Nb pulling = "+str(np.sum(mask)))
            indexFigure+=1

        if HIST_Fu_Lc_DeltaLcLinks:
            dfAll = unfoldingCyclesList
            dfGroupBy = dfAll.groupby(['cycleNumber'])
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            mask = (dfAll["deltaLc"]>=0)
            maxLc = np.max(unfoldingCyclesList["lcAfter"])
            sc = plt.scatter(np.array(dfAll["lcBefore"].loc[mask]), np.array(dfAll["maxSustainableForce"].loc[mask]), s=dfAll["deltaLc"].loc[mask]+1, alpha=0.5)
            plt.legend(*sc.legend_elements("sizes", num=6))
            # plt.legend(*sc.legend_elements("sizes", num=6))
            for cycleNumber,df in dfGroupBy:
                plt.plot(df["lcBefore"].loc[mask], df["maxSustainableForce"].loc[mask])
            plt.xlabel("Contour length (nm)")
            plt.ylabel("Unfolding force (pN)")
            plt.ylim((0,67))
            xmin = st.number_input("xmin ", None, None, 0)
            xmax = st.number_input("xmax ", None, None, dfAll["lcBefore"].loc[mask].max()+10)
            plt.xlim((xmin, xmax))
            plt.savefig(folderSave+"/"+project+"/"+"lcBefore_UnfoldingForce_UnfoldingLength"+".png")
            st.pyplot(figs[indexFigure])
            st.text("Nb pulling = "+str(np.sum(mask)))
            indexFigure+=1


        if HIST_Fu_DeltaLc:
            df = unfoldingCyclesList
            mask = (df["region"]=="pulling")
            maxLc = np.max(unfoldingCyclesList["lcAfter"])
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            sc = plt.scatter(np.array(df["lcBefore"].loc[mask]), np.array(df["maxSustainableForce"].loc[mask]))
            plt.xlabel("Unfolding Length (nm)")
            plt.ylabel("Unfolding Force (pN)")
            plt.ylim((0,67))
            plt.savefig(folderSave+"/"+project+"/"+"unfoldingLength_UnfoldingForce"+".png")
            st.pyplot(figs[indexFigure])
            st.text("Nb pulling = "+str(np.sum(mask)))
            indexFigure+=1


        if HIST_UNFOLDING_LENGTH:
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            mask = unfoldingCyclesList["deltaLc"]>=0
            out = plt.hist(unfoldingCyclesList["deltaLc"].loc[mask], color="lightgray", zorder=0)
            nbInBins = [int(i) for i in out[0]]
            startBins = [int(i) for i in out[1]]
            deltaLcList = list(np.sort(unfoldingCyclesList["deltaLc"].loc[mask]))
            for nbInBin in nbInBins:
                deltaLcTemp = deepcopy(deltaLcList[:nbInBin])
                random.shuffle(deltaLcTemp)
                for i in range(nbInBin):
                    plt.scatter(deltaLcTemp.pop(0), i+0.5, marker="x", zorder=1, color="k")
                    deltaLcList.pop(0)
            plt.xlabel("Unfolding Length (nm)")
            plt.savefig(folderSave+"/"+project+"/"+"unfolding_length_hist"+".png")
            st.pyplot(figs[indexFigure])
            indexFigure+=1


        if HIST_REFOLDING_RATE:
            previousCycleNumber = 0
            count = 0
            previousUnfolding = None
            refoldingLength = []
            for i,unfolding in unfoldingCyclesList.iterrows():
                if unfolding["cycleNumber"] != previousCycleNumber and previousUnfolding["cycleNumber"]<unfolding["cycleNumber"]:
                    if previousUnfolding["lcAfter"] >= thresholdUnfolded:
                        refoldingLength.append(unfolding["lcBefore"])
                        count += 1
                previousUnfolding = unfolding
                previousCycleNumber = unfolding["cycleNumber"]
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            plt.hist(refoldingLength, color="lightgray", zorder=0)
            plt.xlabel("Refolding Length (nm)")
            plt.savefig(folderSave+"/"+project+"/"+"refolding_rate_hist"+".png")
            st.pyplot(figs[indexFigure])
            st.text("Nb data = "+str(count))
            indexFigure+=1


        if HIST_REFOLDING_RATE_BEFORE_AFTER:
            previousCycleNumber = 0
            count = 0
            previousUnfolding = None
            lcPulling = []
            lcRetract = []
            for i,unfolding in unfoldingCyclesList.iterrows():
                if unfolding["cycleNumber"] != previousCycleNumber and previousUnfolding["cycleNumber"]<unfolding["cycleNumber"]:
                    lcPulling.append(unfolding["lcBefore"])
                    lcRetract.append(previousUnfolding["lcAfter"])
                previousUnfolding = unfolding
                previousCycleNumber = unfolding["cycleNumber"]
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            plt.scatter(lcRetract, lcPulling, marker="x", color="k", zorder=0)
            plt.plot([0,proteinLength], [0,proteinLength], color="r")
            plt.xlim((0,proteinLength))
            plt.ylim((0,proteinLength))
            plt.xlabel("Lc before refolding (nm)")
            plt.ylabel("Lc after refolding (nm)")
            plt.savefig(folderSave+"/"+project+"/"+"refolding_rate_lcBefore_lcAfter"+".png")
            st.pyplot(figs[indexFigure])
            indexFigure+=1


        if HIST_REFOLDING_RATE_BEFORE_DELTA:
            previousCycleNumber = 0
            count = 0
            previousUnfolding = None
            lcDelta = []
            lcRetract = []
            for i,unfolding in unfoldingCyclesList.iterrows():
                if unfolding["cycleNumber"] != previousCycleNumber and previousUnfolding["cycleNumber"]<unfolding["cycleNumber"]:
                    lcDelta.append(previousUnfolding["lcAfter"] - unfolding["lcBefore"])
                    lcRetract.append(previousUnfolding["lcAfter"])
                previousUnfolding = unfolding
                previousCycleNumber = unfolding["cycleNumber"]
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            plt.scatter(lcRetract, lcDelta, marker="x", color="k", zorder=0)
            plt.xlim((0,proteinLength))
            # plt.ylim((0,proteinLength))
            plt.xlabel("Lc before refolding (nm)")
            plt.ylabel("Delta Lc (nm)")
            plt.savefig(folderSave+"/"+project+"/"+"refolding_rate_lcBefore_deltaLc"+".png")
            st.pyplot(figs[indexFigure])
            indexFigure+=1

        if UNFOLDING_PATTERN:
            previousCycleNumber = 0
            colors = sns.color_palette(None, nbCycles)
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            for name in unfoldingCyclesList["dataName"].unique():
                maskName = unfoldingCyclesList["dataName"]==name
                for cycleNumber in unfoldingCyclesList["cycleNumber"].loc[maskName]:
                    maskCycle = unfoldingCyclesList["cycleNumber"]==cycleNumber
                    cycles = unfoldingCyclesList.loc[maskName*maskCycle]
                    previousUnfolding = None
                    previousForce = 0
                    previousLc = cycles.head(1)["lcAfter"]
                    for (index,unfolding) in cycles.iterrows():
                        plt.plot([previousLc, unfolding["lcBefore"]], [previousForce, unfolding["forceBefore"]], color=colors[0])
                        previousLc = unfolding["lcBefore"]
                        previousForce = unfolding["forceBefore"]
                        plt.plot([previousLc, unfolding["lcAfter"]], [previousForce, unfolding["forceAfter"]], color=colors[0])
                        previousLc = unfolding["lcAfter"]
                        previousForce = unfolding["forceAfter"]
                        previousUnfolding = unfolding
                    colors.pop(0)
                previousCycleNumber = unfoldingCyclesList["cycleNumber"]
            plt.xlabel(("Contour Length (nm)"))
            plt.ylabel(("Force (pN)"))
            plt.xlim((0,proteinLength*1.2))
            plt.savefig(folderSave+"/"+project+"/"+"unfolding_pattern"+".png")
            st.pyplot(figs[indexFigure])
            indexFigure+=1


        if STATE_DENSITY_MAP:
            dfAll = pd.DataFrame()
            for name in [name[:-4] for name in os.listdir(folderProject+"/wlc_manual_fit") if "Power Spectrum" not in name]:
                dfAll = pd.concat([dfAll, pd.read_csv(folderProject+"/"+"wlc_manual_fit"+"/"+name+".csv")])
            maskForce = dfAll["forceX"]>=5
            maskPulling = dfAll["region"] == "pulling"
            dfAll = dfAll[["proteinLc","forceX"]].loc[maskForce*maskPulling]
            figs[indexFigure], axs[indexFigure] = plt.subplots()
            plt.hist2d(dfAll["proteinLc"], dfAll["forceX"], bins=20, range=[[0,proteinLength], [0,70]])
            plt.xlabel("Contour Length (nm)")
            plt.ylabel("Force (pN)")
            plt.savefig(folderSave+"/"+project+"/"+"state_density_map"+".png")
            st.pyplot(figs[indexFigure])
            indexFigure+=1


    if COMPARE_1D==True:
        nbDataSet = st.number_input("How many data set do you want to compare ?", None, None, 2)
        exp1 = st.multiselect("Selection 1", experiments)
        exp2 = st.multiselect("Selection 2", experiments)
        names1 = [name for name in names if (name[:8] in [exp[:8] for exp in exp1]) and (name[16:-9] in [exp[9:] for exp in exp1])]
        names2 = [name for name in names if (name[:8] in [exp[:8] for exp in exp2]) and (name[16:-9] in [exp[9:] for exp in exp2])]


if __name__ == '__main__':
    project_overview()
