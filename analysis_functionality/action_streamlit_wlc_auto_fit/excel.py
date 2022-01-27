import streamlit as st
import os
import pandas as pd
from foldometer.tools.str_analysis import compact_file_name
from streamlit import caching

@st.cache
def get_excel_wlc_analysis(folderProject):
    if os.path.exists(folderProject + '/wlc_fit_analysis.csv'):
        wlcParmetersFromCsv = pd.read_csv(folderProject + '/wlc_fit_analysis.csv')
        moleculeID = len(wlcParmetersFromCsv["fileName"])
    else:
        wlcParmetersFromCsv = None
        moleculeID = 0
    return (moleculeID, wlcParmetersFromCsv)

def print_excel_wlc_analysis(fileNameList, wlcParmetersFromCsv):
    fileAnalysed = ""
    fileNotAnalysed = ""
    for fileName in fileNameList:
        if wlcParmetersFromCsv is not None:
            if wlcParmetersFromCsv["fileName"].str.contains(fileName).any():
                fileAnalysed += compact_file_name(fileName) + "\n"
            else:
                fileNotAnalysed += compact_file_name(fileName) + "\n"
        else:
            fileNotAnalysed += compact_file_name(fileName) + "\n"

    st.sidebar.header("Inventory")
    st.sidebar.subheader("Analysed File:")
    st.sidebar.success(fileAnalysed)
    st.sidebar.subheader("Not Analysed File:")
    st.sidebar.error(fileNotAnalysed)
    return

def save_excel_row(folderProject, fileName, foldometerCalFit, paramsWlcfit, extensionOffset, forceOffset,\
                   extensionOffsetCorrection, tweezersParametersModification, tStart, tEnd, moleculeID):
    columnOrder = ["fileName", "extensionOffset", "forceOffset", "stiffness1", "stiffness2", "expDiffusion1",\
                   "expDiffusion2", "contourLengthDNA", "persistenceLengthDNA", "stretchModulusDNA",\
                   "persistenceLengthProtein", "tweezersParametersModification",\
                   "extensionOffsetCorrection", "tStart", "tEnd"]

    wlcParametersDico = {"fileName": fileName,\
                         "extensionOffset": extensionOffset,\
                         "forceOffset": forceOffset,\
                         "stiffness1": foldometerCalFit["stiffness"]["PSD1x"],\
                         "stiffness2": foldometerCalFit["stiffness"]["PSD2x"],\
                         "expDiffusion1": foldometerCalFit["diffusionExp"]["PSD1x"],\
                         "expDiffusion2": foldometerCalFit["diffusionExp"]["PSD2x"],\
                         "contourLengthDNA": paramsWlcfit["contourLengthDNA"],\
                         "persistenceLengthDNA": paramsWlcfit["persistenceLengthDNA"],\
                         "stretchModulusDNA": paramsWlcfit["stretchModulusDNA"],\
                         "persistenceLengthProtein": paramsWlcfit["persistenceLengthProtein"],\
                         "tweezersParametersModification": tweezersParametersModification,\
                         "extensionOffsetCorrection": extensionOffsetCorrection,\
                         "tStart": tStart,\
                         "tEnd": tEnd}

    wlcParameters = pd.DataFrame(wlcParametersDico, index=[moleculeID])

    if not (os.path.exists(folderProject + '/wlc_fit_analysis.csv')):
        wlcParameters.to_csv(folderProject + '/wlc_fit_analysis.csv', index=[0])   #, mode='a', header=True
    else:
        (moleculeID, wlcParmetersFromCsv) = get_excel_wlc_analysis(folderProject)
        pd.concat([wlcParmetersFromCsv, wlcParameters])[columnOrder].to_csv(folderProject + '/wlc_fit_analysis.csv')
    caching.clear_cache()
    return
