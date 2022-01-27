import streamlit as st
from os import listdir
from analysis_functionality import wide_mode
from analysis_functionality import load_inputs
from analysis_functionality import read_all
from analysis_functionality import streamlit_headline

def start_environnement(folderProject):
    REQUIRED_ACTION_INPUTS = "inputs"
    REQUIRED_ACTION_PICKLED_RAW_DATA = "pickled_raw_data"

    wide_mode()
    #__________________________________0load_inputs______________________________________________________
    (folderAnalysis, folderProject, folderData, actionName) = load_inputs(folderProject, __file__, loadFrom="pickled_raw_data")

    #__________________________________1read_all______________________________________________________
    filePathList = [f for f in listdir(folderData) if not "Power Spectrum" in f]
    filePath = st.selectbox("Select your file", filePathList)

    (moleculeID, actionFromCsv, rulers, bpDna, fileName, dataExtension, allRawData) = read_all(folderProject, folderData, filePath)

    # parameters_print(labels, parameters)
    #_________________________________2streamlit_head_line______________________________________________________
    streamlit_headline(folderProject, fileName, dataExtension, folderAnalysis, folderData, actionName)

    parameters = [folderAnalysis, folderProject, folderData, actionName, fileName, moleculeID, actionFromCsv, rulers, bpDna, fileName, dataExtension, allRawData, REQUIRED_ACTION_INPUTS, REQUIRED_ACTION_PICKLED_RAW_DATA]
    labels = ["folderAnalysis", "folderProject", "folderData", "actionName", "fileName", "moleculeID", "actionFromCsv", "rulers", "bpDna", "fileName", "dataExtension", "allRawData", "REQUIRED_ACTION_INPUTS", "REQUIRED_ACTION_PICKLED_RAW_DATA"]
    return (labels, parameters)

# from analysis_functionality.tools.streamlit_start_environnement import start_environnement
# folderProject = "C:/Users/Zouki/PycharmProjects/data/kathi_data"
# (parameters, labels) = start_environnement(folderProject)

def end_environnemnt(labels, parameters):

    return