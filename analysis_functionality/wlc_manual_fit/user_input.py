import streamlit as st


def select_region_of_interest(allRawData, tStartDefault, tEndDefault):
    tStart = st.number_input("T0 (s)", None, None, float(tStartDefault), step=0.5)
    tEnd = st.number_input("T0 (s)", None, None, float(tEndDefault), step=0.5)
    mask = (allRawData["time"] >= tStart) * (allRawData["time"] <= tEnd)

    rawData = allRawData.loc[mask]
    return (rawData, tStart, tEnd)
    # return (allRawData, 0.03, 1167.53)

# def select_region_of_interest(allRawData, tStartDefault, tEndDefault):
#     tStart = st.slider("T0 (s)", allRawData["time"].min(), allRawData["time"].max(), float(tStartDefault))
#     tEnd = st.slider("T0 (s)", allRawData["time"].min(), allRawData["time"].max(), float(tEndDefault))
#     mask = (allRawData["time"] >= tStart) * (allRawData["time"] <= tEnd)
#
#     rawData = allRawData.loc[mask]
#     return (rawData, tStart, tEnd)
#     # return (allRawData, 0.03, 1167.53)
