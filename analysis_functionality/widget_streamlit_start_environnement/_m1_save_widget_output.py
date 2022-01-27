import streamlit as st
from os import listdir

from analysis_functionality.tools.str_analysis import make_action_name
from analysis_functionality.python_list_output.parameters_read import parameter_read
import os
import pandas as pd
from analysis_functionality.tools.csv_tools import make_the_dict, saveDataFrameOneRawToCsv
from streamlit import caching
import os

def save_widget_output(allRawData, data, folderSave, labels, parameters):
    folderProject = parameter_read(labels, parameters, "folderProject")
    fileName = parameter_read(labels, parameters, "fileName")
    analysisId = parameter_read(labels, parameters, "analysisId")
    moleculeId = parameter_read(labels, parameters, "moleculeId")
    actionName = parameter_read(labels, parameters, "actionName")
    # _________________________________-1_Saving______________________________________________________
    st.sidebar.success("")
    isSuccess = st.sidebar.button("Save")
    # isSuccess = True  #auto active saving (use it to develop new saving procedure)
    if isSuccess:
        actionState = "success"
        labels.append("actionState")
        parameters.append(actionState)

    st.sidebar.error("")
    isFailed = st.sidebar.button("Discard")
    if isFailed:
        actionState = "failed"
        labels.append("actionState")
        parameters.append(actionState)
        folderDiscard = folderProject + "/" + "discard"
        if not os.path.exists(folderDiscard):
            os.mkdir(folderDiscard)
        allRawData.to_csv(folderDiscard + "/" + fileName + ".csv")

    if isSuccess:
        try:
            os.mkdir(folderSave)
        except:
            pass

        # st.dataframe(allRawData)
        #______________________________________________ Saving Date Fame _______________________________________________
        data.to_csv(folderSave + "/" + fileName + ".csv")

    if isFailed:
        if os.path.exists(folderProject + "/" + actionName + "/" + fileName + ".csv"):
            os.remove(folderProject + "/" + actionName + "/" + fileName + ".csv")

    #______________________________________________ Saving Excel Row _______________________________________________
    # st.text(labels)
    # st.text(parameters)
    if isSuccess:
        (label_parameters_of_dict, parameters_dict) = make_the_dict(labels, parameters)
        dataFrameOneRaw = pd.DataFrame(parameters_dict, index=[analysisId])[label_parameters_of_dict]
        saveDataFrameOneRawToCsv(label_parameters_of_dict, parameters_dict, dataFrameOneRaw, folderSave=folderProject, fileName=actionName)
        st.balloons()
    return
