import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
from foldometer.ixo.lumicks_c_trap import process_lumicks_data

folderProject = "D:/projects/Antoine/ubiquitin"

def wlc_auto_fit(folderProject=folderProject):
    folderData = folderProject + "/" + "csv_raw_data"
    folderSave = folderProject + "/" + "wlc_auto_fit"
    folderSaveFit = folderProject + "/" + "wlc_auto_fit_parameters"
    if not os.path.exists(folderSave):
        os.mkdir(folderSave)
    if not os.path.exists(folderSaveFit):
        os.mkdir(folderSaveFit)
    names = [name[:-4] for name in os.listdir(folderData) if "Power Spectrum" not in name]
    for name in names:
        rawData = pd.read_csv(folderData+"/"+name+".csv")
        powerSpectrum = pd.read_csv(folderData+"/"+name+" Power Spectrum"+".csv", index_col=0)

        allData = pd.DataFrame(process_lumicks_data(rawData, powerSpectrum))

        # st.title("All data and power spectrum")
        # st.write(allData)
        # st.write(powerSpectrum)


        def find_breaking(data):
            forceDiff = data["forceX"].diff()
            forceBreakingIndicator = data["forceX"].iloc[1:] - 5*np.abs(forceDiff)
            mask = forceBreakingIndicator<=-10    # a drop of force of 10pN will cut off the data for the fit
            if mask.any():
                # st.text(data["time"].iloc[np.array(forceBreakingIndicator[mask].index)[-1]-2].item())
                return data["time"].iloc[np.array(forceBreakingIndicator[mask].index)[-1]-2].item()
            else:
                return data["time"].max()
        def find_double_thethers(data):
            maskForceTooHigh = data["forceX"]>=67
            timeDoubleTether = data["time"].loc[maskForceTooHigh].max() + 0.1

            if timeDoubleTether==timeDoubleTether:
                return timeDoubleTether
            else:
                return 0

        maskTime = (allData["time"]>=find_double_thethers(allData))*(allData["time"]<=find_breaking(allData))
        columnsMapping = {"time":"time", "forceX":"force", "surfaceSepX":"extension"}
        data = allData.loc[maskTime].rename(columns=columnsMapping)


        st.text("Rename columnsMapping to match the columns names of time force extension for the package Potato")
        st.text("line 51: columnsMapping = {'time':'time', 'forceX':'force', 'surfaceSepX':'extension'}")
        st.write(columnsMapping)

        st.subheader("Data Cut without breaking and without double tethers that break above 67pN")
        st.write(data)


        wlcParameter = pd.DataFrame({"name":[name], "persistenceLengthDNA":[44.4], "stretchModulusDNA":[720], "forceOffset":[0.], "extensionOffset":[0.]})
        # ...


        dataFit = data
        dataFit.to_csv(folderSave+"/"+name+".csv")
        # wlcParameter = pd.DataFrame({"name":[name], "persistenceLengthDNA":[44.4], "stretchModulusDNA":[720], "forceOffset":[0.], "extensionOffset":[0.]})
        wlcParameter.to_csv(folderSaveFit+"/"+name+".csv")
        break
    return

if __name__ == '__main__':
    wlc_auto_fit()