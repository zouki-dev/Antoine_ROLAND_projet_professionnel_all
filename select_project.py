import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os
import subprocess
import shutil
import time
from csv_raw_data import csv_raw_data
from plot_preview import plot_preview
from wlc_manual_fit import wlc_manual_fit
from split_cycle import split_cycle
from all_figure import all_figure
from step_analysis import step_analysis
from project_overview import project_overview
from presentation import presentation
from fuse_projects import fuse_projects
from pull_data import pull_data

folderLocal="D:/projects"
folderTeam="Data"

def select_project(folderLocal=folderLocal, folderTeam=folderTeam):
    if st.checkbox("TUTO"):
        st.title("Tuto")
        folderVideo = os.path.dirname(__file__) + "/" + "tuto_video"
        st.subheader("main")
        st.video(folderVideo + "/" + "main.webm")
        st.subheader("wlc_manual_fit")
        st.video(folderVideo + "/" + "wlc_manual_fit.webm")
        st.subheader("all_figure")
        st.video(folderVideo + "/" + "all_figure.webm")
        st.subheader("step_analysis")
        st.video(folderVideo + "/" + "step_analysis.webm")
        st.subheader("project_overview")
        st.video(folderVideo + "/" + "project_overview.webm")

    userDefault = "Antoine"
    user = st.sidebar.selectbox("User", os.listdir(folderTeam), index=os.listdir(folderTeam).index(userDefault))
    folderProjects = folderTeam + "/" + user
    allProjects = os.listdir(folderProjects)
    projects = st.multiselect("Selects the projects", allProjects, allProjects)

    st.title('Choose ONE project:')
    for ip, project in enumerate(list(reversed(projects))):
        st.header(project)
        folderProject = folderProjects + "/" + project
        folderRawData = folderProject + "/" + "raw_data"
        folderCsvRawData = folderProject + "/" + "csv_raw_data"
        folderWlcManualFit = folderProject + "/" + "wlc_manual_fit"
        folderStepAnalysis = folderProject + "/" + "step_analysis"
        folderDiscard = folderProject + "/" + "discard"
        folderAnalysis = os.path.dirname(__file__)

        if st.button("folderProject = " + project):
            f = open(os.path.dirname(__file__).replace("\\", "/") + "/" + "folderProject.txt", "w")
            f.write(folderProject)
            f.close()

        (namesRawData, namesCsvRawData, namesWlcManualFit, namesStepAnalysis, parameters, namesDiscard) = (
        [], [], [], [], [], [])
        if os.path.exists(folderRawData):
            namesRawData = [os.path.splitext(file)[0] for root, dirs, files in os.walk(folderRawData) for file in files
                            if not "Power Spectrum" in file and not "_index" in file and not "/fluo/" in root]
            dirs = [dir for (root, dirs, files) in os.walk(folderRawData) for dir in dirs]
            experimentsList = [expDay for expDay in pd.unique(dirs) if not "fluo" in expDay]
            namesDay = [[os.path.splitext(name)[0] for name in os.listdir(folderRawData + "/" + expDay) if
                         not "Power Spectrum" in name and not "_index." in name] for expDay in experimentsList]
        if os.path.exists(folderCsvRawData):
            namesCsvRawData = [file[:-4] for file in os.listdir(folderCsvRawData) if not "Power Spectrum" in file]
        if os.path.exists(folderWlcManualFit):
            namesWlcManualFit = [file[:-4] for file in os.listdir(folderWlcManualFit)]
        if os.path.exists(folderStepAnalysis):
            namesStepAnalysis = [file[:-4] for file in os.listdir(folderStepAnalysis)]
        if os.path.exists(folderDiscard):
            namesDiscard = [file[:-4] for file in os.listdir(folderDiscard)]
        if os.path.exists(folderProject + "/" + "wlc_manual_fit.csv"):
            parametersTemp = pd.read_csv(folderProject + "/wlc_manual_fit.csv")
            parameters = pd.concat([parametersTemp.loc[parametersTemp["fileName"] == name].iloc[[-1]] for name in
                                    parametersTemp["fileName"].unique()])

        with st.expander(str(ip) + " csv_raw_data - " + str(len(namesCsvRawData)) + " / " + str(len(namesRawData))):
            for (experiment, names) in zip(experimentsList, namesDay):
                experiment + " - " + str(len([name for name in names if name in namesCsvRawData])) + " / " + str(
                    len([name for name in names if name in namesRawData]))
        with st.expander(str(ip) + " wlc_manual_fit - " + str(len(namesWlcManualFit)) + " + " + str(
                len(namesDiscard)) + " / " + str(len(namesCsvRawData))):
            for (experiment, names) in zip(experimentsList, namesDay):
                experiment + " - " + str(len([name for name in names if name in namesWlcManualFit])) + " + " + str(
                    len(namesDiscard)) + " / " + str(len([name for name in names if name in namesCsvRawData]))
        with st.expander(
                str(ip) + " step_analysis - " + str(len(namesStepAnalysis)) + " / " + str(len(namesWlcManualFit))):
            for (experiment, names) in zip(experimentsList, namesDay):
                experiment + " - " + str(len([name for name in names if name in namesStepAnalysis])) + " / " + str(
                    len([name for name in names if name in namesWlcManualFit]))

    # folderProjectToSet = st.sidebar.text_input("folderProject = ?", folderProject)
    # if st.sidebar.button("folderProject= above"):
    #     f = open("folderProject.txt", "w+")
    #     f.write(folderProjectToSet)
    #     f.close()

    st.sidebar.header("----------------------------------------------")
    st.sidebar.header("Data download")
    projectSelected = st.sidebar.selectbox("Project to pull", projects)
    experimentsDay = st.sidebar.multiselect("Experiment day to pull",
                                            os.listdir(folderProjects + "/" + projectSelected + "/" + "raw_data"),
                                            [os.listdir(folderProjects + "/" + projectSelected + "/" + "raw_data")[-1]])
    folderProjectSelected = folderProjects + "/" + projectSelected
    st.sidebar.header("----------------------------------------------")
    PULL_DATA = st.sidebar.button("pull_data")
    for (iExp, experimentDay) in enumerate(experimentsDay):
        folderDownload = st.sidebar.text_input(str(iExp) + " folderDowload = ?",
                                               folderLocal + "/" + projectSelected + "_" + experimentDay)
        if PULL_DATA:
            if folderProjectSelected is None:
                st.warning("Tick a project to pull Data")
            pull_data(folderProjectSelected, folderDownload, experimentDay)
            f = open("folderProject.txt", "w+")
            f.write(folderLocal + "/" + projectSelected + "_" + experimentDay)
            f.close()
            st.balloons()

    st.sidebar.header("----------------------------------------------")
    st.sidebar.header("Upload Analysed folder")
    projectDay = st.sidebar.text_input("folderProjectDay = ?", folderLocal + "/" + projectSelected + "_YYYYMMDD")
    folderProjectMain = st.sidebar.text_input("folderProjectMain = ?", folderProjects + "/" + projectSelected)
    folderProjectDay = folderProjects + "/" + projectDay
    if st.sidebar.button("fuse_projects"):
        fuse_projects(folderProject=folderProjectMain, folderProjectDay=folderProjectDay)
        st.balloons()
    return

if __name__ == '__main__':
    select_project()