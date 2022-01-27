import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import os
from analysis_functionality.tools.str_analysis import compact_file_name
from analysis_functionality.wlc_manual_fit.user_input import select_region_of_interest
from scipy.signal import savgol_filter
from scipy.ndimage import median_filter
from PIL import Image
import altair as alt
from matplotlib import cm

folderProject = "D:/Projects/ubiquitin_extrusion"
folderData = folderProject + "/" + "wlc_manual_fit"
folderSave = folderProject + "/" + "pairwise_distance"
folderExtrusionTime = folderProject + "/" + "extrusion_time"


names = [name[:-4] for name in os.listdir(folderData)]
namesCompact = [compact_file_name(name[:-4]) for name in os.listdir(folderData)]
nameCompact = st.sidebar.selectbox("Select Data:", namesCompact)
nameTemp = [name for (name,nameComp) in zip(names,namesCompact) if nameCompact[:8] in nameComp and nameCompact[8:] in nameComp]
st.sidebar.text(nameTemp)
name = nameTemp[0]

data = pd.read_csv(folderData+"/"+name+".csv")
timeExtrusions = np.array(pd.read_csv(folderExtrusionTime+"/"+name+".csv", header=None))
st.sidebar.text(pd.read_csv(folderExtrusionTime+"/"+name+".csv"))
for timeExtrusion in timeExtrusions:
    (dataExtrusion, tStart, tEnd) = select_region_of_interest(data, timeExtrusion[0], timeExtrusion[1])
    break
if len(timeExtrusions)==0:
    (dataExtrusion, tStart, tEnd) = select_region_of_interest(data, data["time"].min(), data["time"].max())
maskForce = dataExtrusion["forceX"]>=2


BUTTON_SAVE = st.sidebar.button("save")
if BUTTON_SAVE:
    if not os.path.exists(folderSave):
        os.mkdir(folderSave)

savagoWindow = st.sidebar.number_input("Window size", None, None, 21, 2)

st.sidebar.header("Parameter for histogram")
stepsize = st.sidebar.number_input("step size (aa)",None,None,24.,step=1.)
nbLines1 = st.sidebar.number_input("nb lines 1",None,None,7,step=1)
amplitude1 = st.sidebar.number_input("amplitude",None,None,10.,step=1.)
offset1 = st.sidebar.number_input("offset 1",None,None,0.,1.)

st.sidebar.header("Parameter for extrusion figure")
nbLines2 = st.sidebar.number_input("nb lines 2",None,None,7,step=1)
offset2 = st.sidebar.number_input("offset 2",None,None, dataExtrusion["proteinLc"].loc[maskForce].min()/0.34,1.)


fig, ax = plt.subplots()
plt.plot(dataExtrusion["time"].loc[maskForce], dataExtrusion["proteinLc"].loc[maskForce]/0.34, color="lightGrey", zorder=1)
plt.plot(savgol_filter(dataExtrusion["time"].loc[maskForce],savagoWindow,1), savgol_filter(dataExtrusion["proteinLc"].loc[maskForce]/0.34,savagoWindow,1), color="r", zorder=1)
for i in range(nbLines2):
    plt.plot([dataExtrusion["time"].loc[maskForce].min(), dataExtrusion["time"].loc[maskForce].max()], [i*stepsize+offset2, i*stepsize+offset2], "k", zorder=0)
plt.xlabel("Time (s)")
plt.ylabel("Lc (aa)")
plt.title("Stepsize = "+str(stepsize))
if BUTTON_SAVE:
    plt.savefig(folderSave + "/" + name +"_extrusionStep"+ ".png")
    plt.savefig(folderSave + "/" + name +"_extrusionStep"+ ".pdf")
st.pyplot(fig)

if not st.checkbox("pause", True):
    time = np.array(dataExtrusion["time"].loc[maskForce])
    lc = np.array(savgol_filter(dataExtrusion["proteinLc"].loc[maskForce],savagoWindow,1)) / 0.34
    n = int(np.max(lc) + 1)

    @st.cache
    def pairwise_distance_matrix(lc,n):
        pairwiseDistanceMatrix = np.zeros((n, n))
        for (i,li) in enumerate(lc):
            for (j, lj) in enumerate(lc):
                if np.abs(time[j]-time[i]) <= 3:
                    # st.text(time[j] - time[i])
                    pairwiseDistanceMatrix[int(li), int(lj)] += 1
        return pairwiseDistanceMatrix / np.max(np.max(pairwiseDistanceMatrix))
    pairwiseDistanceMatrix = pairwise_distance_matrix(lc,n)
    diag = np.diagonal(pairwiseDistanceMatrix)

    fig, ax = plt.subplots()
    plt.imshow(np.log(pairwiseDistanceMatrix[int(np.min(lc)):,int(np.min(lc)):]))
    plt.colorbar()
    st.pyplot(fig)

    def pairwise(pairwiseDistanceMatrix):
        n = len(pairwiseDistanceMatrix)
        pairwise = np.zeros(n)
        for i in range(n):
            for j in range(i,n):
                pairwise[j-i] += pairwiseDistanceMatrix[i,j]
        return pairwise


    pairwiseDistance = pairwise(pairwiseDistanceMatrix)
    fig, ax = plt.subplots()
    plt.plot(pairwiseDistance, zorder=1)
    for i in range(nbLines1):
        plt.plot([stepsize*i,stepsize*i], [0,amplitude1], "r", zorder=0)

    plt.xlim((0,st.number_input("max x",None,None,120.,10.)))
    plt.xlabel("Lc (aa)")
    plt.ylabel("")
    plt.title("Stepsize = "+str(stepsize))
    if BUTTON_SAVE:
        plt.savefig(folderSave+"/"+name+".png")
        plt.savefig(folderSave+"/"+name+".pdf")
    st.pyplot(fig)