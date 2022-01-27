from foldometer.ixo.lumicks_c_trap import extract_calibration_parameters
import os
from scipy import constants
import pickle
import streamlit as st

# thermalCalibration = get_calibration_from_power_spectrum(filePath)
def get_calibration_from_power_spectrum(folderData, fileName):
    calibrationFilePath = folderData + "/" + fileName + " Power Spectrum.tdms"
    thermalCalibration = extract_calibration_parameters(calibrationFilePath)
    thermalCalibration["beadDiameter"] *= 1000
    thermalCalibration["beta"] = 0.001 / thermalCalibration["distanceResponse"]
    thermalCalibration["diffusionTheory"] = ((constants.Boltzmann * (thermalCalibration["temperature"] + 273.15)) \
                                                / (3 * constants.pi * thermalCalibration["viscosity"] * 1000 * thermalCalibration["beadDiameter"] * 10 ** -9))
    thermalCalibration["diffusionExp"] = thermalCalibration["diffusionTheory"] / (
            (thermalCalibration["distanceResponse"] * 10 ** -6) ** 2)
    return thermalCalibration

@st.cache
def load_pickled_file(folderProject, fileName):
    file = open(folderProject + "/pickled_raw_data/" + fileName + ".pickle", 'rb')
    allRawData = pickle.load(file)
    file.close()
    return allRawData
