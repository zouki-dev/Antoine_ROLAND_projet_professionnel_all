import streamlit as st


def select_region_of_interest(allRawData, tStartDefault, tEndDefault):
    tStart = st.slider("T0 (s)", allRawData["time"].min(), allRawData["time"].max(), tStartDefault)
    tEnd = st.slider("T0 (s)", allRawData["time"].min(), allRawData["time"].max(), tEndDefault)
    mask = (allRawData["time"] >= tStart) * (allRawData["time"] <= tEnd)

    rawData = allRawData.loc[mask]
    return (rawData, tStart, tEnd)
