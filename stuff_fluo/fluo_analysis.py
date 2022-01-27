import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
from analysis_functionality.tools.streamlit_wide_mode import wide_mode
from foldometer.analysis.fluorescence import track_gaussian_feature
from scipy.signal import convolve2d, medfilt
from copy import deepcopy


folderProject = "F:/projects/test2"
folderData = folderProject + "/csv_raw_data"
folderFluo = folderProject + "/fluo_raw"
folderSave = folderProject + "/fluo_analysis"
if not os.path.exists(folderSave):
    os.mkdir(folderSave)
wide_mode()

names = [name[:-4] for name in os.listdir(folderFluo) if not "Power Spectrum" in name]
name = st.sidebar.selectbox("Select Data:", names)

data = pd.read_csv(folderData+"/"+name+".csv")
data532 = plt.imread(folderFluo+"/"+name+"_532nm"+".tif")
data683 = plt.imread(folderFluo+"/"+name+"_683nm"+".csv")
metaData = pd.read_csv(folderFluo+"/"+name+"_metaData"+".csv")

(n, m) = np.shape(data532)


RAW_DATA = st.sidebar.checkbox("raw data", True)
if RAW_DATA:
    plt.subplot(2,1,1)
    plt.imshow(np.log(data532), cmap="inferno")
    plt.grid(False)
    plt.subplot(2,1,2)
    plt.imshow(np.log(data683), cmap="viridis")
    plt.grid(False)
    st.pyplot()

matrixConvolution = np.array([[1., 0., 1.],
                              [2., 4., 2.],
                              [1., 0., 1.]])/12
data532Filtered = convolve2d(data532, matrixConvolution)[1:-1,1:-1]
data683Filtered = convolve2d(data683, matrixConvolution)[1:-1,1:-1]


FILTERED_DATA = st.sidebar.checkbox("filtered data", False)
if FILTERED_DATA:
    plt.subplot(2,1,1)
    plt.title("Zoom on the first 500 time points")
    plt.imshow(np.log(data532[:,:500]), cmap="inferno")
    plt.grid(False)
    plt.subplot(2,1,2)
    plt.imshow(np.log(data532Filtered[:,:500]), cmap="inferno")
    plt.grid(False)
    st.pyplot()

    plt.subplot(2,1,1)
    plt.title("Zoom on the first 500 time points")
    plt.imshow(np.log(data683[:,:500]), cmap="viridis")
    plt.grid(False)
    plt.subplot(2,1,2)
    plt.imshow(np.log(data683Filtered[:,:500]), cmap="viridis")
    plt.grid(False)
    st.pyplot()


BACKGROUND_DATA = st.sidebar.checkbox("background data", False)
backgroundLowIndex = st.sidebar.number_input("Region background low", 0, 10000, 1)
backgroundHighIndex = st.sidebar.number_input("Region background High", 0, 10000, 10)

backgroundRegion532nm = data532Filtered[backgroundLowIndex:backgroundHighIndex, :]
backgroundSignal532nm = medfilt(np.mean(backgroundRegion532nm, axis=0), 101)
data532background = data532Filtered - backgroundSignal532nm

backgroundRegion683nm = data683Filtered[backgroundLowIndex:backgroundHighIndex, :]
backgroundSignal683nm = medfilt(np.mean(backgroundRegion683nm, axis=0), 101)
data683background = data683Filtered - backgroundSignal683nm
if BACKGROUND_DATA:
    plt.subplot(211)
    plt.imshow(np.log(data532), cmap="inferno")
    plt.plot([1,m], [backgroundLowIndex, backgroundLowIndex], color="g")
    plt.plot([1,m], [backgroundHighIndex, backgroundHighIndex], color="g")
    plt.grid(False)
    plt.subplot(212)
    plt.imshow(data532background, cmap="inferno")
    plt.grid(False)
    st.pyplot()

    plt.subplot(211)
    plt.imshow(np.log(data683), cmap="viridis")
    plt.plot([1,m], [backgroundLowIndex, backgroundLowIndex], color="g")
    plt.plot([1,m], [backgroundHighIndex, backgroundHighIndex], color="g")
    plt.grid(False)
    plt.subplot(212)
    plt.imshow(data683background, cmap="viridis")
    plt.grid(False)
    st.pyplot()


TIME_OFFSET = st.sidebar.checkbox("Time Offset", False)
def find_breaking(data):
    forceDiff = data["forceX"].diff()
    forceBreakingIndicator = data["forceX"].iloc[1:] - 5*np.abs(forceDiff)
    mask = forceBreakingIndicator<=-10
    if mask.any():
        # st.text(data["time"].iloc[np.array(forceBreakingIndicator[mask].index)[-1]-2].item())
        return data["time"].iloc[np.array(forceBreakingIndicator[mask].index)[-1]-2].item()
    else:
        return data["time"].max()
tEndDefault = find_breaking(data)
timeBreakingExt = st.sidebar.number_input("Time breaking extension data", None, None, tEndDefault, 1.)
timeBreakingFluo = st.sidebar.number_input("Time breaking extension data", None, None, int(m*0.9))
if TIME_OFFSET:
    plt.plot(data["time"], data["forceX"])
    plt.plot([timeBreakingExt, timeBreakingExt], [0, 70], color="g", linewidth=1)
    plt.grid(False)
    st.pyplot()

    plt.imshow(data532Filtered, cmap="inferno")
    plt.plot([timeBreakingFluo, timeBreakingFluo], [1,n], color="g", linewidth=1)
    plt.grid(False)
    st.pyplot()


REGION_OF_INTEREST = st.sidebar.checkbox("region of interest", False)
if REGION_OF_INTEREST:
    x, y = np.meshgrid(np.linspace(-1, 1, 51), np.linspace(-1, 1, 11))
    dst = np.sqrt(x * x + y * y)
    sigma = 1
    muu = 0.000
    gauss = np.exp(-((dst - muu) ** 2 / (2.0 * sigma ** 2)))
    gauss = np.array(gauss/np.sum(np.sum(gauss)))
    ngauss = len(gauss)

    data532Beads = convolve2d(data532background, gauss)[int(ngauss/2):-int(ngauss/2), int(ngauss/2):-int(ngauss/2)]
    data683Beads = convolve2d(data683background, gauss)[int(ngauss/2):-int(ngauss/2), int(ngauss/2):-int(ngauss/2)]

    extFluo1 = st.sidebar.number_input("Region of interest 1:", 0, n, int(n/2)-3)
    extFluo2 = st.sidebar.number_input("Region of interest 2:", 0, n, int(n/2)+3)

    extMovementFluo1 = st.sidebar.number_input("Region of interest movement 1:", 0., 1000., 1.)
    extMovementFluo2 = st.sidebar.number_input("Region of interest movement 2:", 0., 1000., 1.)
    movement = (data["trapSepX"]-data["trapSepX"].min())/((data["trapSepX"]-data["trapSepX"].min()).max())*n/10
    movement1 = movement * extMovementFluo1 + extFluo1
    movement2 = movement * extMovementFluo2 + extFluo2

    plt.subplot(313)
    plt.imshow(data532Filtered, cmap="inferno")
    plt.plot(data["time"]/metaData["fluoTimeRes"].item(), movement1, color="g", linewidth=1)
    plt.plot(data["time"]/metaData["fluoTimeRes"].item(), movement2, color="g", linewidth=1)
    plt.grid(False)
    st.pyplot()
