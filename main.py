import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os
import subprocess
import shutil
import time
from foldometer.analysis.region_classification import assign_regions
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
from select_project import select_project
from plot_preview import plot_preview
from rescue_function.assign_all_region import assign_all_regions

def main(folderLocal="D:/projects", folderTeam="Data"):
    f = open(os.path.dirname(__file__).replace("\\","/")+"/"+"folderProject.txt", "r")
    folderProject = f.read()
    f.close()

    scripts = ["presentation", "plot_preview", "wlc_fit", "make_all_figures", "select_project"]
    script = st.sidebar.selectbox("Select script", scripts, index=0)

    if script == "assign_all_region":
        assign_all_regions(folderProject=folderProject)
    if script == "presentation":
        presentation(folderAnalysis=os.path.dirname(__file__).replace("\\","/"))
    if script == "plot_preview":
        plot_preview(folderProject=folderProject)
    if script == "csv_raw_data":
        csv_raw_data(folderProject=folderProject)
    if script == "plot_preview":
        plot_preview(folderProject=folderProject)
    if script == "wlc_fit":
        wlc_manual_fit(folderProject=folderProject)
    if script == "split_cycle":
        split_cycle(folderProject=folderProject)
    if script == "make_all_figures":
        all_figure(folderProject=folderProject)
    if script == "step_analysis":
        step_analysis(folderProject=folderProject)
    if script == "project_overview":
        project_overview(folderTeam="Data", folderProject=folderProject)
    if script == "select_project":
        select_project(folderLocal=folderLocal, folderTeam=folderTeam)



if __name__ == '__main__':
    folderData = "/".join(__file__.replace("\\","/").split("/")[:-1]) + "/" + "Data"
    main(folderLocal="D:/projects", folderTeam=folderData)
