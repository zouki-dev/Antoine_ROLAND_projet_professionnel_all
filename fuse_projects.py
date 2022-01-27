import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil

folderProject = "S:/projects/Antoine/ubiquitin"
folderProjectDay = "D:/projects/ubiquitin_20211114"

def fuse_projects(folderProject=folderProject, folderProjectDay=folderProjectDay):
    dayFilePaths = []
    indexPath = len(folderProject)
    for root, dir, files in os.walk(folderProjectDay):
        for file in files:
            dayFilePaths.append(root[indexPath+1:].replace("\\","/") +"/"+ file)

    projectFilePaths = []
    indexPath = len(folderProject)
    for root, dir, files in os.walk(folderProject):
        for file in files:
            projectFilePaths.append(root[indexPath+1:].replace("\\","/") +"/"+ file)


    for path in [path for path in dayFilePaths if path not in projectFilePaths and "/" in path]:
        print(path)
        if not os.path.exists(os.path.dirname(folderProject+"/"+path)):
            os.mkdir(os.path.dirname(folderProject+"/"+path))

        shutil.copyfile(folderProjectDay+"/"+path, folderProject+"/"+path)


    for name in [name for name in os.listdir(folderProjectDay) if ".csv" in name and name in os.listdir(folderProject)]:
        if os.path.exists(folderProject+"/"+name):
            df1 = pd.read_csv(folderProject+"/"+name, index_col=False)
            df2 = pd.read_csv(folderProjectDay+"/"+name, index_col=False)

            df = pd.concat([df1, df2])
            df.to_csv(folderProject+"/"+name, mode="w+")
        else:
            df2 = pd.read_csv(folderProjectDay + "/" + name, index_col=False)
            df2.to_csv(folderProject + "/" + name, mode="w+")


if __name__ == '__main__':
    fuse_projects(folderProject=folderProject, folderProjectDay=folderProjectDay)