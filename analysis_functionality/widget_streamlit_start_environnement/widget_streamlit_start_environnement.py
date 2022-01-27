import streamlit as st
import os
import datetime
import pandas as pd
import numpy as np

from analysis_functionality.tools.streamlit_wide_mode import wide_mode
from analysis_functionality.tools.str_analysis import str_extension_remove
from analysis_functionality.tools.str_analysis import make_action_name
from analysis_functionality.tools.str_analysis import compact_file_name
from analysis_functionality.tools.get_molecule_id import get_molecule_id
from analysis_functionality.python_list_output.parameters_save import parameters_save

from analysis_functionality.widget_streamlit_start_environnement._0_load_inputs import load_inputs
from analysis_functionality.widget_streamlit_start_environnement._1_read_all import read_all
from streamlit import caching
from analysis_functionality.tools.str_analysis import compact_file_name
# from analysis_functionality.widget_streamlit_start_environnement.widget_streamlit_start_environnement import start_streamlit_environement
# [labels, parameters] = start_streamlit_environement()

def start_environnement(__file__parent, folderProject, folderData, seeFileAlreadyAnalysed=False, wideMode=True):
    if wideMode:
        wide_mode()

    #__________________________________0load_inputs______________________________________________________
    (filePathAnalysis, actionName) = load_inputs(folderProject=folderProject, __file__parent=__file__parent)

    #__________________________________1read_all______________________________________________________
    if os.path.exists(folderProject+"/"+actionName+".csv"):
        nameAnalysedList = [name for name in pd.read_csv(folderProject+"/"+actionName+".csv")["fileName"]]
    else:
        nameAnalysedList = []
    if os.path.exists(folderProject + "/discard"):
        namesDiscard = [name[:-4] for name in os.listdir(folderProject + "/discard")]
    else:
        namesDiscard = []
    for name in namesDiscard:
        nameAnalysedList.append(name)
    if st.sidebar.checkbox("See files already analysed ?", False):
        fileNameList = list(([str_extension_remove(name) for name in os.listdir(folderData) if not "Power Spectrum" in name]))
        fileNameShortList = [compact_file_name(name) for name in fileNameList]
    else:
        fileNameList = list(([str_extension_remove(name) for name in os.listdir(folderData) if not "Power Spectrum" in name]))
        fileNameShortList = [compact_file_name(name) for name in fileNameList if name not in nameAnalysedList]
        if len(fileNameShortList)==0:
            st.success("Everything is analysed in this project")
            fileNameList = list(([str_extension_remove(name) for name in os.listdir(folderData) if not "Power Spectrum" in name]))
            fileNameShortList = [compact_file_name(name) for name in fileNameList]


    fileNameShort = st.sidebar.selectbox("Select your file "+str(len(fileNameShortList)), fileNameShortList)
    for name in fileNameList:
        if (fileNameShort[8:] in name) and (fileNameShort[:8] in name):
            fileName = name

    dataExtension = "csv"
    (allAction, allRawData, moleculeId, analysisId) = read_all(folderProject, folderData, fileName, __file__parent=__file__parent)
    dateAction = str(datetime.datetime.now())


    #_________________________________2streamlit_head_line______________________________________________________
    labels = ["fileName", "analysisId", "moleculeId", "folderProject", "folderData",\
              "dateAction", "actionName",\
              "filePathAnalysis"]
    parameters = [fileName, analysisId, moleculeId, folderProject, folderData,\
                  dateAction, actionName,\
                  filePathAnalysis]

    st.title(actionName)
    st.text("")
    st.text("Package version : " + os.path.dirname(filePathAnalysis).split("/")[-1])
    st.text("folderProject : " + folderProject)
    st.text("fileName : " + fileName)

    # allRawData = allRawData
    # allAction = allAction
    return [allRawData, allAction, labels, parameters]



