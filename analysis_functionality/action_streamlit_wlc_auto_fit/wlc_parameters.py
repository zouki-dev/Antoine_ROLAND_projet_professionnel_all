import streamlit as st
from copy import deepcopy

def select_parameters(thermalCalibration, paramsWlc):
    st.sidebar.header("Fitting parameters")
    paramsWlcFit = {}
    foldometerCalFit = {}
    trapStiffnessModification = 1

    tweezersParametersModification = float(st.sidebar.text_input("tweezerParametersModification = 1", str(1.0)))
    stiffnessModification = tweezersParametersModification
    diffusionModification = tweezersParametersModification ** 2

    foldometerCalFit = deepcopy(thermalCalibration)

    foldometerCalFit["diffusionExp"] = thermalCalibration["diffusionExp"] * diffusionModification
    foldometerCalFit["stiffness"] = thermalCalibration["stiffness"] * stiffnessModification
    foldometerCalFit["alpha"] = thermalCalibration["alpha"] / (diffusionModification ** 0.5)
    foldometerCalFit["beta"] = thermalCalibration["beta"]  # * (stiffnessModification / diffusionModification**0.5) = 1

    paramsWlcFit["persistenceLengthDNA"] = float(st.sidebar.text_input("persistenceLengthDNA = 44.4", str(paramsWlc["persistenceLengthDNA"])))
    paramsWlcFit["stretchModulusDNA"] = float(st.sidebar.text_input("stretchModulusDNA = 720", str(paramsWlc["stretchModulusDNA"])))
    paramsWlcFit["contourLengthDNA"] = paramsWlc["contourLengthDNA"]
    paramsWlcFit["persistenceLengthProtein"] = paramsWlc["persistenceLengthProtein"]

    extensionOffsetCorrection = float(st.sidebar.text_input("- Correction Extension Offset", str(0.0)))
    forceOffset = float(st.sidebar.text_input("- Force Offset", str(0.0)))


    return (foldometerCalFit, paramsWlcFit, extensionOffsetCorrection, forceOffset, tweezersParametersModification)



def make_dna_parameter(bpDNA=5000, persistenceLengthDNA=44.4, stretchModulusDNA=720, persistenceLengthProtein=0.75):
    paramsWlc = {}
    paramsWlc["contourLengthDNA"] = bpDNA*0.34
    paramsWlc["persistenceLengthDNA"] = persistenceLengthDNA
    paramsWlc["stretchModulusDNA"] = stretchModulusDNA
    paramsWlc["persistenceLengthProtein"] = persistenceLengthProtein
    return paramsWlc


