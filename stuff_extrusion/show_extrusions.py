import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
from scipy.signal import savgol_filter

folderProject = "D:/projects/ubiquitin_extrusion"
folderData = folderProject + "/" + "wlc_manual_fit"
folderExtrusionTime = folderProject + "/" + "extrusion_time"

names = [name[:-4] for name in os.listdir(folderData)]
nWindow = st.sidebar.number_input("slope window",None,None,100,10)
st.sidebar.text(str(0.002*nWindow)+" s")

for name in names:
    data = pd.read_csv(folderData+"/"+name+".csv")[["time", "forceX", "proteinLc"]]
    deltaT = data["time"].diff().mean()

    maskForce = data["forceX"]>= 2
    data["proteinLcFiltered"] = np.nan
    data["proteinLcFiltered"].loc[maskForce] = savgol_filter(data["proteinLc"].loc[maskForce],21,1)/0.34

    timeExtrusions = np.array(pd.read_csv(folderExtrusionTime+"/"+name+".csv"))
    for timeExtrusion in timeExtrusions:
        useThisExtrusion = st.checkbox("Use this data: "+name+"  "+str(timeExtrusion), True)
        if useThisExtrusion:
            t0 = st.number_input("t0: "+name+"  "+str(timeExtrusion),None,None, timeExtrusion[0],step=0.1)
            tend = st.number_input("tend: "+name+"  "+str(timeExtrusion),None,None, timeExtrusion[1],step=0.1)
            mask = (data["time"]>=t0) * (data["time"]<=tend)

            fig, ax = plt.subplots()
            ax.plot(data["time"].loc[mask], data["proteinLc"].loc[mask]/0.34, "lightGrey")
            ax.plot(data["time"].loc[mask], data["proteinLcFiltered"].loc[mask], "r")
            st.pyplot(fig)

            lc = np.array(data["proteinLcFiltered"].loc[mask])
            slope = (lc[nWindow:] - lc[:-nWindow]) / (deltaT*nWindow)
            time = np.array(range(len(slope)))*deltaT

            fig, ax = plt.subplots()
            ax.plot(time, slope, "r")
            plt.xlabel("Time (s)")
            plt.ylabel("Slope (aa.s-1)")
            st.pyplot(fig)
