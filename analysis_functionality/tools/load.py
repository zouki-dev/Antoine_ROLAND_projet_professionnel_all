from foldometer.ixo.lumicks_c_trap import extract_calibration_parameters
import os
from scipy import constants
import pickle
import streamlit as st

# thermalCalibration = get_calibration_from_power_spectrum(filePath)
def get_calibration_from_power_spectrum(filePath):
    for spectrumFileName in os.listdir(os.path.split(filePath)[0]):
        if spectrumFileName.endswith("Power Spectrum.tdms") and spectrumFileName[9:15] <= os.path.split(filePath)[1][9:15]:
            calibrationFilePath = os.path.join(os.path.split(filePath)[0], spectrumFileName)
    thermalCalibration = extract_calibration_parameters(calibrationFilePath)
    thermalCalibration["beadDiameter"] *= 1000
    thermalCalibration["beta"] = 0.001 / thermalCalibration["distanceResponse"]
    thermalCalibration["diffusionTheory"] = ((constants.Boltzmann * (thermalCalibration["temperature"] + 273.15)) \
                                                / (3 * constants.pi * thermalCalibration["viscosity"] * 1000 * thermalCalibration["beadDiameter"] * 10 ** -9))
    thermalCalibration["diffusionExp"] = thermalCalibration["diffusionTheory"] / (
            (thermalCalibration["distanceResponse"] * 10 ** -6) ** 2)
    return thermalCalibration

@st.cache
def load_pickled_file(folderData, fileName):
    file = open(folderData + "/" + fileName + ".pickle", 'rb')
    allRawData = pickle.load(file)
    file.close()
    return allRawData
