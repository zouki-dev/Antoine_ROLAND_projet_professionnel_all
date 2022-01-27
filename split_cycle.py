import pandas as pd
import numpy as np
import os
from foldometer.tools.region_manipulation import get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting, get_cycle_region_time_sorted
from analysis_functionality.tools.str_analysis import int_to_000str

folderProject = "D:/projects/Rubisco"

def split_cycle(folderProject=folderProject):
    folderData = folderProject + "/" + "wlc_manual_fit"
    folderSave = folderProject + "/" + "split_cycle"
    if not os.path.exists(folderSave):
        os.mkdir(folderSave)

    names = [name[:-4] for name in os.listdir(folderData)]
    for name in names:
        data = pd.read_csv(folderData+"/"+name+".csv")

        for index,cycle in enumerate(get_cycle_region_by_cycle_previous_retracting_and_next_early_retracting(data)):
            (pullingCycleRetracting, regionRetracting, maskRetracting) = cycle['retracting']
            (pullingCycleStationary, regionStationary, maskStationary) = cycle['stationary']
            (pullingCyclePulling, regionPulling, maskPulling) = cycle['pulling']
            (pullingCycleNextRetracting, regionNextRetracting, maskNextRetracting) = cycle['nextRetracting']

            data["region"].loc[maskRetracting] = 'retracting'
            data["region"].loc[maskStationary] = 'stationary'
            data["region"].loc[maskPulling] = 'pulling'
            data["region"].loc[maskNextRetracting] = 'nextRetracting'

            mask = maskRetracting + maskStationary + maskPulling + maskNextRetracting
            data.loc[mask].to_csv(folderSave+"/"+name+"-c"+int_to_000str(index)+".csv")

if __name__ == '__main__':
    split_cycle()