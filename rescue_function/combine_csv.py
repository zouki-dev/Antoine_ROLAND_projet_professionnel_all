import pandas as pd
import numpy as np

folderProject = "D:/projects/temp"
listFileToFuse = ["wlc_manual_fit", "wlc_manual_fit_old"]
nameSave = "combine_csv"

listDataframe = [pd.read_csv(folderProject+"/"+file+".csv") for file in listFileToFuse]
dfFinal = pd.concat(listDataframe)

if "fileName" in dfFinal.columns:
    names = dfFinal["fileName"].unique()
    dfUniqueLine = None
    for name in names:
        line = dfFinal.loc[dfFinal["fileName"] == name].iloc[[-1]]
        if dfUniqueLine is None:
            dfUniqueLine = line
        else:
            dfUniqueLine = pd.concat(dfUniqueLine,line)

    dfUniqueLine.to_csv(folderProject+"/"+nameSave+".csv")
else:
    dfFinal.to_csv(folderProject+"/"+nameSave+".csv")
