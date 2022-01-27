import os
import pandas as pd
from analysis_functionality.action_python_inputs.read_inputs import read_inputs
from analysis_functionality.tools.str_analysis import str_extension_remove
from analysis_functionality.tools.str_analysis import make_action_name
from os import listdir
from analysis_functionality.tools.get_molecule_id import get_molecule_id
import streamlit as st


def read_all(folderProject, folderData, fileName, __file__parent):
    csvPathActionRawOutput = folderData + "/" + fileName + ".csv"

    # @st.cache
    def read_csv_data(Path):
        allRawData = pd.read_csv(filepath_or_buffer=Path)
        return allRawData

    allRawData = read_csv_data(csvPathActionRawOutput)
    actionName = make_action_name(__file__parent).split(".")[0]

    # _________________________________read excel ________________________________________
    def get_excel_action_analysis(folderProject, action):
        if os.path.exists(folderProject + '/' + action + ".csv"):
            allAction = pd.read_csv(folderProject + '/' + action + ".csv")
            analysisId = len(allAction["fileName"])
        else:
            allAction = None
            analysisId = 0
        return (allAction, analysisId)

    (allAction, analysisId) = get_excel_action_analysis(folderProject, actionName)

    fileNameList = [str_extension_remove(name) for name in listdir(folderData) if not "Power Spectrum" in name]
    moleculeId = get_molecule_id(fileName, fileNameList)

    return (allAction, allRawData, moleculeId, analysisId)

# from analysis_functionality.action_streamlit_wlc_auto_fit._1read_all import read_all
# (moleculeID, actionFromCsv, rulers, bpDna, fileName, dataExtension, allRawData) = read_all(folderProject, fileName, folderAnalysis, folderData)

# print("moleculeID : ")
# print(moleculeID)
# print("actionFromCsv : ")
# print(actionFromCsv)
# print("rulers : ")
# print(rulers)
# print("bpDna : ")
# print(bpDna)
# print("fileNameList : ")
# print(fileNameList)
# print("fileName : ")
# print(fileName)
# print("allRawData : ")
# print(allRawData)



# print(folderProject)
# print(rulers)
# print(bpDna)
# print(fileNameList)
# print(fileName)
# print(allRawData)