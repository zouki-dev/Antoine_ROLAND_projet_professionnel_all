import streamlit as st

def streamlit_headline(folderProject, fileName, dataExtension, folderAnalysis, folderData, actionName):
    st.title("action :  " + actionName)
    st.text("")
    st.text("filePython : " + folderAnalysis)
    st.text("folderProject : " + folderProject)
    st.text("folderData : " + folderData)
    st.text("actionName : " + actionName)
    st.text("fileName : " + fileName)
    return
# from analysis_functionality.action_streamlit_wlc_auto_fit._2streamlit_headline import streamlit_headline
# fileName = streamlit_headline(folderProject, folderAnalysis, folderData, actionName)