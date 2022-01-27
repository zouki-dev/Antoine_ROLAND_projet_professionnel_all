import os
import pandas as pd
import shutil
import numpy as np

folderProjectSelected = "S:/projects/Antoine/ubiquitin"
experiementDay = "20211114"
folderDownload = "D:/projects/ubiqitin" + "_" + experiementDay

def pull_data(folderProjectSelected, folderDownload, experiementDay):
    indexPath = len(folderProjectSelected)
    namesSelected = [os.path.splitext(file)[0] for root, dirs, files in
                     os.walk(folderProjectSelected + "/" + "raw_data" + "/" + experiementDay) for file in
                     files]
    filesPath = [root.replace("\\", "/")[len(folderProjectSelected) + 1:] + "/" + file for root, dirs, files in os.walk(folderProjectSelected) for file in files if os.path.splitext(file)[0] in namesSelected]

    for filePath in filesPath:
        if not os.path.exists(os.path.dirname(folderDownload + "/" + filePath)):
            os.makedirs(os.path.dirname(folderDownload + "/" + filePath))
        shutil.copyfile(folderProjectSelected + "/" + filePath, folderDownload + "/" + filePath)

    if os.path.exists(folderProjectSelected + "/" + "wlc_manual_fit.csv"):
        df = pd.read_csv(folderProjectSelected + "/" + "wlc_manual_fit.csv")
        mask = [True if name in namesSelected else False for name in df["fileName"]]
        if np.sum(mask) > 0:
            df.loc[mask].to_csv(folderDownload + "/" + "wlc_manual_fit.csv")

if __name__ == '__main__':
    pull_data(folderProjectSelected, folderDownload, experiementDay)