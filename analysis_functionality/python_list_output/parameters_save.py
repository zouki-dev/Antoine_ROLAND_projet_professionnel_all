import pandas as pd
import streamlit as st
from analysis_functionality.python_list_output.parameters_read import parameter_read

def parameters_save(allRawData, allAction, labels, parameters, analysisId = 0):
    pythonList = {}
    for (label, parameter) in zip(labels, parameters):
        pythonList[label] = parameter

    df = pd.DataFrame(pythonList, parameter_read(labels, parameters, "fileName"))
    st.dataframe(df)
    # pd.dataframe.save_to_csv(df, index=analysisId)
    # df.(columns=labels, index=analysisId)
    return

# from analysis_functionality.python_list_output.parameters_save import parameters_save
# parameters_save(labels=labels, parameters=parameters, analysisId = analysisId)

