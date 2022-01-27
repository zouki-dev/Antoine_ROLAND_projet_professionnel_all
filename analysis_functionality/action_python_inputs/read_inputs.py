import pandas as pd
import  streamlit as st

def read_inputs(projectFolder):
    inputs = pd.read_csv(projectFolder + "/inputs.csv")

    rulers_str = st.sidebar.text_input("Rulers :", inputs["rulers"][0])
    list_ruler_str = rulers_str.replace(" ", "").replace("]", "").replace("[", "").split(",")
    rulers = [float(ruler_str) for ruler_str in list_ruler_str]

    bpDnaDefault = int(inputs["bpDna"][0])
    bpDna = int(st.sidebar.text_input("bpDna :", bpDnaDefault))
    return (rulers, bpDna)

# from analysis_functionality.action_python.inputs.read_inputs import read_inputs
# projectFolder = "C:/Users/Zouki/PycharmProjects/data/kathi_data"
# (folderProject, rulers, bpDna) = read_inputs(projectFolder)
# print(folderProject)
# print(rulers)
# print(bpDna)