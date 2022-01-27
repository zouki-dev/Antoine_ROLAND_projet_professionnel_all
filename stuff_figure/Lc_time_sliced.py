import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import png
import os
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
import seaborn as sns
from scipy.signal import savgol_filter
from analysis_functionality.tools.streamlit_wide_mode import wide_mode
st.set_option('deprecation.showPyplotGlobalUse', False)
wide_mode()

#_____________________________________________________________________________________________________________________
folderProject = "D:/projects/ubiquitin_extrusion"
folderData = folderProject + "/" + "wlc_manual_fit"
folderDrawing = folderProject + "/" + "protein_drawing"
folderExtrusionConfirmed = folderData
folderRainbow = folderProject + "/" + "rainbow"
folderSave = folderProject + "/" + "Lc_time_sliced"
if not os.path.exists(folderRainbow):
    os.mkdir(folderRainbow)
if not os.path.exists(folderDrawing):
    os.mkdir(folderDrawing)
if not os.path.exists(folderSave):
    os.mkdir(folderSave)


#_____________________________________________________________________________________________________________________
st.title("Cut Time vs Lc plot + assign drawing")
namesDrawing = [name[:-4] for name in os.listdir(folderDrawing) if ".png" in name]
names = [name[:-4] for name in os.listdir(folderData) if ".csv" in name]
name = st.sidebar.selectbox("Select data", names)
data = pd.read_csv(folderData + "/" + name + ".csv")
maskForce = data["forceX"]>=2
LcFiltered = savgol_filter(data["proteinLc"].loc[maskForce], 51, 1)

parameters = pd.read_csv(folderProject + "/wlc_manual_fit.csv")
parameter = parameters.loc[parameters["fileName"] == name].iloc[[-1]]
rulersStr = st.sidebar.text_input("Rulers:", parameter["rulers"].item())
rulers = [float(string) for string in rulersStr.replace("[","").replace("]","").replace(" ","").split(",")]

LcOffset = - st.sidebar.number_input("- Lc Offset = ", None, None, 0.)
LcMin = st.sidebar.number_input("LcMin ", None, None, -160.)
LcMax = st.sidebar.number_input("LcMax ", None, None, 330.)


#_____________________________________________________________________________________________________________________
tMin = st.number_input("tMin", None, None, data["time"].min())
tMax = st.number_input("tMax", None, None, data["time"].max())
order = 1
window = 51
savgol = lambda x: savgol_filter(x, window, order)
fig, ax1 = plt.subplots()
ax1.plot(data["time"], data["proteinLc"],'k', zorder=1)#348ABD
ax1.set_ylabel("Protein Contour Length (nm)",color='#348ABD')
ax1.set_ylim(LcMin,LcMax)
ax2 = ax1.twinx()
ax2.plot(data["time"], data["forceX"],'#E24A33', zorder=2)
ax2.set_ylabel("Force (pN)",color='#E24A33')
ax2.set_xlabel("Time (s)")
ax2.set_ylim(-10,70)
ax2.set_xlim(data["time"].min(),data["time"].max())
fig.tight_layout()
plt.hlines(83.3,0,max(data["time"]),colors='k',linestyles='dashdot',label='Estimated protein contour length')
plt.grid()
ax1.set_xlim(tMin,tMax)
ax2.set_xlim(tMin,tMax)
st.pyplot()


#_____________________________________________________________________________________________________________________
if not os.path.exists(folderRainbow+"/"+name+".png"):
    fig = plt.figure(constrained_layout=True)
    gs = gridspec.GridSpec(6, 6, figure=fig)
    colors = cm.rainbow(np.linspace(0,1,len(data["time"])))
    ax0 = fig.add_subplot(gs[:-1,:])
    ax0.scatter(data["surfaceSepX"], data["forceX"], marker='.', linewidths=0.001, color=colors)
    forceArray = np.arange(0.5, 60, 0.2)
    for length in rulers:
        extArray = wlc_series_accurate(forceArray, \
                                     parameter["contourLengthDNA"].item(), \
                                     parameter["persistenceLengthDNA"].item(), \
                                     parameter["stretchModulusDNA"].item(), \
                                     length, \
                                     parameter["persistenceLengthProtein"].item(), \
                                     )
        ax0.plot(extArray, forceArray, color="gray", zorder=0)
    plt.xlabel("Extension (nm)")
    plt.ylabel("Force (pN)")
    ax1 = fig.add_subplot(gs[-1,:])
    ax1.scatter(data["time"],np.zeros(len(data["time"])), color=colors, linewidths=2)
    plt.xlabel("time(s)")
    ax0.set_xlim(data["surfaceSepX"].mean()-700, data["surfaceSepX"].mean()+700)
    plt.savefig(folderRainbow+"/"+name+".png")
rainbowPng = mpimg.imread(folderRainbow+"/"+name+".png")
imageboxRainbow = OffsetImage(rainbowPng, zoom=0.72)
abRainbow = AnnotationBbox(imageboxRainbow, (0.49, 0.5))
fig, ax = plt.subplots()
ax.add_artist(abRainbow)
plt.draw()
st.sidebar.pyplot()


#_____________________________________________________________________________________________________________________
st.sidebar.title("------- Section -------")
nbSection = st.sidebar.number_input("Add a section on the figure",1)
tMinSection = np.ones(nbSection)*data["time"].min()
tMaxSection = np.ones(nbSection)*data["time"].max()

st.subheader("Section")
if nbSection==1:
    figFinal, ax = plt.subplots(1, nbSection, sharey=True)
    axs = [ax]
else:
    figFinal, axs = plt.subplots(1, nbSection, sharey=True)
rulersStrActives = ["" for i in range(nbSection)]
for nSection in range(nbSection):
    st.sidebar.subheader("Section "+str(nSection))
    tMinSection[nSection] = st.sidebar.number_input("tMin "+str(nSection), None, None, data["time"].min())
    tMaxSection[nSection] = st.sidebar.number_input("tMax "+str(nSection), None, None, data["time"].max())

    axs[nSection].plot(data["time"], data["proteinLc"]-LcOffset, color="lightgrey", zorder=0)
    axs[nSection].plot(data["time"].loc[maskForce], LcFiltered-LcOffset, color="r", linewidth=0.2, zorder=2)

    rulersStrActives[nSection] = st.text_input("Select active rulers for Section: "+str(nSection), str(rulers))
    rulerActives = [float(l) for l in rulersStrActives[nSection].replace("[", "").replace("]", "").replace(" ", "").split(",")]
    for ruler in rulers:
        if ruler in rulerActives:
            colorRuler="k"
        else:
            colorRuler="silver"
        axs[nSection].plot([tMinSection[nSection],tMaxSection[nSection]], [ruler,ruler], color=colorRuler, linewidth=0.5, zorder=1)
    axs[nSection].set_xlim(tMinSection[nSection], tMaxSection[nSection])
    # axs[nSection].xlim((tMinSection[nSection], tMaxSection[nSection]))
    axs[nSection].set_ylim((LcMin, LcMax))
    axs[nSection].spines['right'].set_visible(False)
    axs[nSection].spines['left'].set_visible(False)
    # axs[nSection].tick_params(labelleft=False)
    from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                                   AutoMinorLocator)
    axs[nSection].grid(False)
    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=axs[nSection].transAxes, color='k', clip_on=False)
    if not nSection==0:
        axs[nSection].plot((-d, +d), (-d, +d), **kwargs)  # top-right diagonal
    else:
        axs[nSection].set_ylabel("Protein Contour Length Lc (nm)")
    if not nSection==nbSection-1:
        axs[nSection].plot((1-d, 1+d), (-d, +d), **kwargs)  # top-right diagonal
    axs[nSection].set_xlabel("Time (s)")
    axs[nSection].xaxis.grid(True, which='minor')


#_____________________________________________________________________________________________________________________
st.sidebar.title("-------- State --------")
nbStates = st.sidebar.number_input("Add a state picture on the figure",None ,None ,0)
colorsStates = sns.color_palette(n_colors=nbStates)
xPositionPictures = np.ones(nbStates)
yPositionPictures = np.ones(nbStates)
zoomPictures = np.ones(nbStates)
states = [" " for i in range(nbStates)]
for nState in range(nbStates):
    st.sidebar.header("State "+str(nState))
    states[nState] = st.sidebar.selectbox("State "+str(nState), namesDrawing)
    xPositionPictures[nState] = st.sidebar.number_input("x position of the picture "+str(nState), None, None, 1.)
    yPositionPictures[nState] = st.sidebar.number_input("y position of the picture "+str(nState), None, None, -100.)
    zoomPictures[nState] = st.sidebar.number_input("zoom of the picture "+str(nState), None, None, 0.1)

    drawing = mpimg.imread(folderDrawing + "/" + states[nState] + ".png")
    imagebox = OffsetImage(drawing, zoom=zoomPictures[nState])
    for ax in axs:
        ab2 = AnnotationBbox(imagebox, (xPositionPictures[nState], yPositionPictures[nState]))
        ax.add_artist(ab2)
    plt.draw()
if st.button("Save figure"):
    plt.savefig(folderSave+"/"+name+".png")
    plt.savefig(folderSave+"/"+name+".pdf")
st.pyplot()









#_____________________________________________________________________________________________________________________
st.sidebar.header("protein_drawing Library")
for nameDrawing in namesDrawing:
    st.sidebar.text(nameDrawing)
    drawing = mpimg.imread(folderDrawing+"/"+nameDrawing+".png")
    imagebox = OffsetImage(drawing, zoom=0.6)
    ab = AnnotationBbox(imagebox, (0.5, 0.5))

    fig, ax = plt.subplots()
    ax.add_artist(ab)
    plt.draw()
    st.sidebar.pyplot()


# drawing[:,:,:]