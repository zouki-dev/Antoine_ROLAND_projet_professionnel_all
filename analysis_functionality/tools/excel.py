import streamlit as st
import os
import pandas as pd
from analysis_functionality.tools.str_analysis import compact_file_name
import caching
from analysis_functionality.tools.str_analysis import make_action_name
import numpy as np

def get_excel_rows(folderProject, action):
    if os.path.exists(folderProject + '/' + action + '.csv'):
        allRowFromCsv = pd.read_csv(folderProject + '/' + action + '.csv')
    else:
        allRowFromCsv = None
    return allRowFromCsv
# from analysis_functionality.tools.excel import get_excel_rows
# allRowFromCsv = get_excel_rows(folderProject, action)

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


def save_excel_row(allRowFromCsv, folderProject, actionName, labels, parameters, analysisId, moleculeID):
    labels_str = [str(label) for label in labels]
    parameters_str = [str(parameter) for parameter in parameters]
    row_to_save = np.array([labels_str, parameters_str])
    if allRowFromCsv is None:
        st.text("if allRowFromCsv is None")
        file_to_save_dict = {}
        for (label, parameter) in zip(labels,parameters):
            file_to_save_dict[label] = parameter
        st.text(file_to_save_dict)
        file_to_save = pd.DataFrame(file_to_save_dict, index=analysisId)
        st.text(file_to_save)
    else:
        st.text("if allRowFromCsv is not None")
        file_to_save_dict = {}
        for (label, parameter) in zip(labels, parameters):
            file_to_save_dict[label] = parameter
        file_to_save = [labels_str, parameters_str, allRowFromCsv]
        st.text(file_to_save)

    return

# def save_excel_row(folderProject, actionName, labels, parameters, analysisId):
#     actionRowDict = {}
#     # for (label, parameter) in zip(labels, parameters):
#     actionRowDict[labels] = [str(parameter) for parameter in parameters]
#     actionRow = pd.DataFrame(actionRowDict, labels)
#     st.dataframe(actionRow)
#
#     if not (os.path.exists(folderProject + '/' + actionName + '.csv')):
#         actionRow.to_csv(folderProject + '/' + actionName + '.csv', index=True)   #, mode='a', header=True
#     else:
#         allRawFromCsv = get_excel_rows(actionName, folderProject)
#         rowToSaveInExcel = pd.DataFrame(actionRow, index=[analysisId])
#
#         st.text(pd.concat([allRawFromCsv, rowToSaveInExcel]))
#
#         pd.concat([allRawFromCsv, rowToSaveInExcel]).to_csv(folderProject + '/' + actionName + '.csv', index=True)
#     return
