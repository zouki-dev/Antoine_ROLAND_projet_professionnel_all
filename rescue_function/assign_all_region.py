import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foldometer.analysis.region_classification import assign_regions

folderProject = "E:/projects_analysis/tweezers_analysis-demo_Antoine/Data/Antoine/dmMBP"

def assign_all_regions(folderProject=folderProject):
    folderData = folderProject + "/" + "wlc_manual_fit"
    names = [name[:-4] for name in os.listdir(folderData) if ".csv" in name]

    for name in names:
        print(name)
        data = pd.read_csv(folderData + "/" + name + ".csv")
        dataRegion = assign_regions(data, verbose=False)
        dataRegion.to_csv(folderData+"/"+name+".csv")
    return

if __name__ == '__main__':
    assign_all_regions()