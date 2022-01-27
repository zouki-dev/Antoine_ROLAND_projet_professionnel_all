from analysis_functionality.tools.str_analysis import str_extension_remove, str_extension_select, compact_file_name
from os import listdir
import streamlit as st
import os
import pandas as pd

def get_excel_action_analysis(folderProject, action):
    if os.path.exists(folderProject + '/' + action + ".csv"):
        allAction = pd.read_csv(folderProject + '/' + action + ".csv")
        analysisId = len(allAction["fileName"])
    else:
        allAction = None
        analysisId = 0
    return (allAction, analysisId)

def print_action_inventory(folderProject, folderData, actionName):
    st.sidebar.text("\n")
    (allAction, analysisId) = get_excel_action_analysis(folderProject, actionName)
    fileNamesInFolderData = [str_extension_remove(name) for name in listdir(folderData) if not "Power Spectrum" in name]
    if allAction is not None:
        st.header("All analysis row saved")
        st.dataframe(allAction)

        maskAnalysed = allAction["actionState"] == "success"
        allFileNameSuccess = list(allAction.loc[maskAnalysed]["fileName"])

        maskFailed = allAction["actionState"] == "failed"
        allFileNameFailed = list(allAction.loc[maskFailed]["fileName"])

        maskInProgress = [not(fileName in allFileNameSuccess) and not(fileName in allFileNameFailed) for fileName in allAction["fileName"]]
        allFileNameInProgress = list(allAction.loc[maskInProgress]["fileName"])

        st.sidebar.text("\n")
        st.sidebar.text("\n")
        st.sidebar.text("\n")
        st.sidebar.text("\n")
        st.sidebar.text("\n")

        strAllFileNameSuccess = ""
        strAllFileNameInProgress = ""
        strAllFileNameFailed = ""
        for fileName in allFileNameSuccess:
            strAllFileNameSuccess = strAllFileNameSuccess + str(compact_file_name(fileName)) + "\n"
        for fileName in allFileNameInProgress:
            strAllFileNameInProgress = strAllFileNameInProgress + str(compact_file_name(fileName)) + "\n"
        fileNameNotSeen = [fileName for fileName in list(fileNamesInFolderData) if (not (fileName in allFileNameSuccess)) and (not (fileName in allFileNameFailed))]
        for fileName in fileNameNotSeen:
            strAllFileNameInProgress = strAllFileNameInProgress + str(compact_file_name(fileName)) + "\n"
        for fileName in allFileNameFailed:
            strAllFileNameFailed = strAllFileNameFailed + str(compact_file_name(fileName)) + "\n"

        st.sidebar.header("Inventory")
        st.sidebar.subheader("Analysed File:")
        st.sidebar.success(strAllFileNameSuccess)
        st.sidebar.subheader("In Progress File:")
        st.sidebar.warning(strAllFileNameInProgress)
        st.sidebar.subheader("Analysis Failed File:")
        st.sidebar.error(strAllFileNameFailed)
    else:
        allFileNameInProgress = list(fileNamesInFolderData)
        strAllFileNameInProgress = ""
        for fileName in allFileNameInProgress:
            strAllFileNameInProgress = strAllFileNameInProgress + str(compact_file_name(fileName)) + "\n"
        st.sidebar.header("Inventory")
        st.sidebar.subheader("Analysed File:")
        st.sidebar.success("")
        st.sidebar.subheader("In Progress File:")
        st.sidebar.warning(strAllFileNameInProgress)
        st.sidebar.subheader("Analysis Failed File:")
        st.sidebar.error("")

    return

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