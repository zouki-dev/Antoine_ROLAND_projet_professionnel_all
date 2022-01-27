import streamlit as st
import pandas as pd

def select_region_of_interest(allRawData, listLabelZoom_input, listTimeZoom_input, selectBordersBool=True):
    listTimeZoom = listTimeZoom_input.copy()
    timeLabelZoom = listLabelZoom_input.copy()

    for time in listTimeZoom:
        listTimeZoom.append(time)

    minTime = allRawData["time"].min()
    maxTime = allRawData["time"].max()

    if not timeLabelZoom in listTimeZoom:
        tStart = allRawData["time"].min()  #default value
        listTimeZoom["tStart"] = tStart
    if not listTimeZoom.contain("tEnd"):
        tEnd = allRawData["time"].max()  #default value
        listTimeZoom["tEnd"] = tEnd


    for (timeZoom,labelZoom) in zip(listTimeZoom, timeLabelZoom):
        timeZoom_userInput = st.text_input(labelZoom + " : ", str(timeZoom))
        epsilon = (allRawData["time"] - float(timeZoom_userInput)).abs()
        timeZoom_tEnd = epsilon.idxmax()



    mask = (allRawData["time"] >= listTimeZoom["tEnd"]) * (allRawData["tStart"] <= listTimeZoom["tEnd"])
    rawData = allRawData.loc[mask]
    return (rawData, timeZoom)
