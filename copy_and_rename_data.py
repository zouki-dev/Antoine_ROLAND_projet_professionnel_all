import os
import pandas as pd
import streamlit as st

def copy_and_rename_data():
    folderProject = "./Data/Antoine/ubiquitin"
    folderCsvRawData = folderProject + "/" + "csv_raw_data"
    folderWlcManualFit = folderProject + "/" + "wlc_manual_fit"
    if not os.path.exists(folderCsvRawData):
        os.mkdir(folderCsvRawData)
    namesWlc = [name for name in os.listdir(folderWlcManualFit)]
    for name in namesWlc:
        data = pd.read_csv(folderWlcManualFit+"/"+name)
        data.to_csv(folderCsvRawData+"/"+name)


    folderProject = "./Data/Antoine/ubiquitin"
    folderCsvRawData = folderProject + "/" + "csv_raw_data"
    folderWlcManualFit = folderProject + "/" + "wlc_manual_fit"
    for root, dirs, files in os.walk(folderProject):
        for name in files:
            if name!="wlc_manual_fit.csv":
                nameMaker = name.split(" ")
                if len(nameMaker)==3:
                    pathFixed = os.path.join(root, " ".join((nameMaker[0],"data",nameMaker[2])))
                elif len(nameMaker)==4:
                    pathFixed = os.path.join(root, " ".join((nameMaker[0], "data", nameMaker[2])))
                else:
                    st.text(nameMaker)
                    pathFixed = os.path.join(root, "test"+name[-5:])
                os.rename(os.path.join(root,name), pathFixed)

    folderProject = "./Data/Antoine/dmMBP"
    folderCsvRawData = folderProject + "/" + "csv_raw_data"
    folderWlcManualFit = folderProject + "/" + "wlc_manual_fit"
    for root, dirs, files in os.walk(folderProject):
        for name in files:
            if name!="wlc_manual_fit.csv":
                nameMaker = name.split(" ")
                if len(nameMaker)==3:
                    pathFixed = os.path.join(root, " ".join((nameMaker[0],"data",nameMaker[2])))
                elif len(nameMaker)==4:
                    pathFixed = os.path.join(root, " ".join((nameMaker[0], "data", nameMaker[2], nameMaker[3])))
                elif len(nameMaker)==5:
                    pathFixed = os.path.join(root, " ".join((nameMaker[0], "data", nameMaker[2], nameMaker[3], nameMaker[4])))
                else:
                    st.text(nameMaker)
                    pathFixed = os.path.join(root, "test"+name[-5:])
                os.rename(os.path.join(root,name), pathFixed)

    folderProject = "./Data/ubiquitin_20200717"
    folderCsvRawData = folderProject + "/" + "csv_raw_data"
    folderWlcManualFit = folderProject + "/" + "wlc_manual_fit"
    for root, dirs, files in os.walk(folderProject):
        for name in files:
            if name != "wlc_manual_fit.csv":
                nameMaker = name.split(" ")
                if len(nameMaker) == 3:
                    pathFixed = os.path.join(root, " ".join((nameMaker[0], "data", nameMaker[2])))
                elif len(nameMaker) == 4:
                    pathFixed = os.path.join(root, " ".join((nameMaker[0], "data", nameMaker[2], nameMaker[3])))
                elif len(nameMaker) == 5:
                    pathFixed = os.path.join(root,
                                             " ".join((nameMaker[0], "data", nameMaker[2], nameMaker[3], nameMaker[4])))
                else:
                    st.text(nameMaker)
                    pathFixed = os.path.join(root, "test" + name[-5:])
                os.rename(os.path.join(root, name), pathFixed)

if __name__ == '__main__':
    copy_and_rename_data()
