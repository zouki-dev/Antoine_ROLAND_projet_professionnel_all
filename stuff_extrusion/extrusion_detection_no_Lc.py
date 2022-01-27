from analysis_functionality.widget_streamlit_start_environnement.widget_streamlit_start_environnement import start_environnement
from analysis_functionality.python_list_output.parameters_read import parameter_read
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import savgol_filter
# from foldometer.analysis.threading import calculate_rolling_slopes
import numpy as np
from scipy.ndimage import label, binary_closing
import streamlit as st
from bokeh.plotting import figure
from analysis_functionality.tools.streamlit_wide_mode import wide_mode
from foldometer.tools.misc import data_selection, column_indexer
from scipy.signal import savgol_filter
import copy
from scipy.signal import savgol_filter, find_peaks
import itertools
import csv
import os
from analysis_functionality.tools.str_analysis import str_extension_remove, compact_file_name
from foldometer.ixo.lumicks_c_trap import process_lumicks_data
from foldometer.analysis.region_classification import assign_regions
st.set_option('deprecation.showPyplotGlobalUse', False)
wide_mode()

folderProject = "D:/projects/Polymerase"
folderData = folderProject + "/csv_raw_data"
folderSave = folderProject + "/extrusion_detection_no_Lc"


fileNameList = [str_extension_remove(fileName) for fileName in os.listdir(folderData) if not "Power Spectrum" in fileName]
fileNameShortList = [compact_file_name(fileName) for fileName in os.listdir(folderData) if not "Power Spectrum" in fileName]
fileNameTemp = st.sidebar.selectbox("Select your file", fileNameShortList)
fileName = [name for (name, nameShort) in zip(fileNameList, fileNameShortList) if nameShort==fileNameTemp][0]
#------------------------------------------------ parameters -----------------------------------------------------------
minSlope = -10
maxSlope = 10

minContourLength = 1637
maxContourLength = 1640

minTime = 0
maxTime = 2000

minForce = 3
threshold = -2

channel = "surfaceSepX"
boolAssignRegion = False



#------------------------------------------ def usefull function -------------------------------------------------------
def calculate_rolling_slopes(data, window=600, columnY="surfaceSepX", center=True):
    df = data[["time", columnY]]
    df.index = df["time"]

    dt = df["time"].diff().mean()

    def summing_window(data):
        return (data * np.arange(1, len(data) + 1)).sum()

    # print(self.metadata["sampleFreq"])
    denominator = dt / 12 * (2 * window + window ** 3)
    slope = (df[columnY].rolling(window, center=center).apply(summing_window, raw=True) - window /
              2 * df[columnY].rolling(window, center=center).mean() * (window + 1)) / denominator
    return slope

def find_runs(x):
    """Find runs of consecutive items in an array."""

    # ensure array
    x = np.asanyarray(x)
    if x.ndim != 1:
        raise ValueError('only 1D array supported')
    n = x.shape[0]

    # handle empty array
    if n == 0:
        return np.array([]), np.array([]), np.array([])

    else:
        # find run starts
        loc_run_start = np.empty(n, dtype=bool)
        loc_run_start[0] = False
        np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
        run_starts = np.nonzero(loc_run_start)[0]

        # find run values
        run_values = x[loc_run_start]

        # find run lengths
        run_lengths = np.diff(np.append(run_starts, n))

        timeIntervals = []
        for (run_value, run_start, run_length) in zip(run_values, run_starts, run_lengths):
            t0 = data["time"].iloc[run_start]
            t1 = data["time"].iloc[run_start + run_length-1]
            if run_value:
                timeIntervals.append([t0, t1])
        return timeIntervals

def make_interval(makeInterval, timeUnfoldings, timeOffsetStr):
    intervalsStr = [interval.replace("[", "").replace("]", "").replace(" ", "").split(",") for interval in makeInterval if interval[0]=="["]
    intervals = [[float(a),float(b)] for [a,b] in intervalsStr]
    timeOffset = timeOffsetStr.replace("[", "").replace("]", "").replace(" ", "").split(",")
    tmin = intervals[0][0]
    tmax = intervals[0][1]
    if "delete" in makeInterval:
        return [tmin, tmin]
    for [t0,t1] in intervals:
        if t0 < tmin:
            tmin = t0
        if t1 > tmax:
            tmax = t1
    if "previous_unfolding" in makeInterval:
        tmin = timeUnfoldings.loc[timeUnfoldings <= tmin].max()
    if "next_unfolding" in makeInterval:
        tmax = timeUnfoldings.loc[timeUnfoldings >= tmax].min()
    tmin = tmin + float(timeOffset[0])
    tmax = tmax + float(timeOffset[1])
    return [tmin, tmax]

@st.cache(allow_output_mutation=True)
def load_data(folderProject, dataName):
    dataTemp = pd.read_csv(folderProject + "/" + dataName + ".csv")
    dataTemp.index = pd.to_datetime(dataTemp["time"], unit='s')
    dataTemp = dataTemp.dropna()
    thermalCalibration = pd.read_csv(folderData + "/" + fileName + " Power Spectrum.csv", index_col=0)
    dataTemp2 = process_lumicks_data(dataTemp, thermalCalibration, foldometerCalFit=thermalCalibration)
    if boolAssignRegion:
        data = assign_regions(dataTemp2)
    else:
        data = dataTemp2
        data["region"] = "stationary"
    return data


#----------------------------------------------- initialize ------------------------------------------------------------
data = load_data(folderData, fileName)
data.index = data["time"]

data["average"] = savgol_filter(data[channel], window_length=51, polyorder=1)
slope = calculate_rolling_slopes(data, window=600, columnY="average", center=True)

data["slope"] = np.array(slope)
maskTime = (data["time"] >= minTime) * (data["time"] <= maxTime)
maskForce = (data["forceX"] >= minForce)
maskStationary = (data["region"] == "stationary")
maskSlopeThreshold = data["slope"]<=threshold

maskExtrusion = maskSlopeThreshold * maskStationary * maskForce * maskTime


#---------------------------------------------- plots full time --------------------------------------------------------
st.sidebar.header("Full time")
plt.subplot(211)
plt.plot(data["time"], slope)
plt.scatter(data["time"].loc[maskSlopeThreshold*maskStationary], data["slope"].loc[maskSlopeThreshold*maskStationary], color="r")
plt.ylabel("Slope (nm.s-1)")
plt.ylim(minSlope, maxSlope)

plt.subplot(212)
plt.plot(data["time"], data[channel], color="r")
plt.xlabel("Time (s)")
plt.ylabel("Extension (nm)")
# plt.ylim(minContourLength, maxContourLength)
st.sidebar.pyplot()


#------------------------------------------------ analysis -------------------------------------------------------------
timeIntervals = find_runs(maskExtrusion)

(indexUnfolding, properties) = find_peaks(data["slope"].loc[maskStationary * maskForce * maskTime], height=20, distance=500)
timeUnfoldings = data["time"].loc[maskStationary * maskForce * maskTime].iloc[indexUnfolding]


#------------------------------------------ By hand corrections --------------------------------------------------------
st.sidebar.header("Correct extrusions")
makeIntervals = [None]*len(timeIntervals)
selectedIntervals = [None]*len(timeIntervals)
timeOffsets = [None]*len(timeIntervals)
for (i, timeInterval) in enumerate(timeIntervals):
    makeIntervals[i] = st.sidebar.multiselect(str(timeInterval), ["delete", "previous_unfolding", "next_unfolding"] + [str(timeInterval) for timeInterval in timeIntervals], [str(timeInterval), "delete"])
    selectedIntervals[i] = [float(t) for t in st.sidebar.text_input("timeOffset "+ str(timeInterval), str(timeInterval)).replace(" ","").replace("[","").replace("]","").split(",")]
    # selectedIntervals[i] = make_interval(makeIntervals[i], timeUnfoldings, timeOffsets[i])


#-------------------------------------------------- save --------------------------------------------------------------
if st.sidebar.button("Save"):
    selectedIntervalsToSave = [[a,b] for [a, b] in selectedIntervals if a!=b]
    if not os.path.exists(folderSave):
        os.mkdir(folderSave)
    with open(folderSave + "/" + fileName + '.csv', "w", newline="") as fp:
        wr = csv.writer(fp)
        wr.writerows(selectedIntervalsToSave)


#-------------------------------------------------- plots --------------------------------------------------------------
mode = st.selectbox("Select mode:", ["All the data zoomed","All the extrusions"])
if mode == "All the data zoomed":
    timeSliceSize = 20
    timeSlices = [[sliceNumber*timeSliceSize, sliceNumber*timeSliceSize + timeSliceSize] for sliceNumber in range(int(int(data["time"].max())/20)+1)]
    maskSlices = []
    for timeSlice in timeSlices:
        maskSlice = (data["time"]>=timeSlice[0]) * (data["time"]<timeSlice[1])

        st.header("Time: " + str(timeSlice))

        plt.subplot(211)
        plt.plot(data["time"].loc[maskSlice], data["slope"].loc[maskSlice])
        plt.scatter(data["time"].loc[maskSlice*maskExtrusion], data["slope"].loc[maskSlice*maskExtrusion], color="r")
        plt.ylabel("Slope (nm.s-1)")
        plt.ylim(minSlope, maxSlope)

        plt.subplot(212)
        plt.plot(data["time"].loc[maskSlice], data[channel].loc[maskSlice], color="r")
        plt.plot(data["time"].loc[maskSlice*maskExtrusion], data[channel].loc[maskSlice*maskExtrusion], color="b")
        plt.xlabel("Time (s)")
        plt.ylabel("Extension (nm)")
        # plt.ylim(minContourLength, maxContourLength)
        st.pyplot()

if mode == "All the extrusions":
    for timeInterval in selectedIntervals:
        time_start = timeInterval[0]
        maskTimeWindow = (data["time"] >= time_start-5) * (data["time"]<time_start+15)
        maskSingleExtrusion = (data["time"] >= timeInterval[0]) * (data["time"] <= timeInterval[1])

        st.header(str(timeInterval))

        plt.subplot(211)
        plt.plot(data["time"].loc[maskTimeWindow], data["slope"].loc[maskTimeWindow])
        plt.scatter(data["time"].loc[maskTimeWindow*maskExtrusion], data["slope"].loc[maskTimeWindow*maskExtrusion], color="r")
        plt.plot(data["time"].loc[maskSingleExtrusion], data["slope"].loc[maskSingleExtrusion],"g")

        unfoldingInWindow = (timeUnfoldings >= time_start-5) * (timeUnfoldings <= time_start+15)
        if unfoldingInWindow.any():
            for timeUnfolding in timeUnfoldings.loc[unfoldingInWindow]:
                plt.plot([timeUnfolding, timeUnfolding], [-40, 40], "k")
        plt.ylabel("Slope (nm.s-1)")
        plt.ylim(minSlope, maxSlope)

        plt.subplot(212)
        plt.plot(data["time"].loc[maskTimeWindow], data[channel].loc[maskTimeWindow], color="r")
        plt.plot(data["time"].loc[maskTimeWindow*maskExtrusion], data[channel].loc[maskTimeWindow*maskExtrusion], color="b")
        plt.plot(data["time"].loc[maskSingleExtrusion], data[channel].loc[maskSingleExtrusion], color="g")
        plt.xlabel("Time (s)")
        plt.ylabel("Contour length (nm)")
        plt.ylim(minContourLength, maxContourLength)
        st.pyplot()

