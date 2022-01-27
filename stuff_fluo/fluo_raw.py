import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
from foldometer.ixo.lumicks_c_trap import read_fluorescence_file_lumicks

folderProject = "F:/projects/test2"
folderData = folderProject + "/raw_data"
folderCsvExtension = folderProject + "/csv_raw_data"
folderSave = folderProject + "/fluo_raw"
if not os.path.exists(folderSave):
    os.mkdir(folderSave)

namesCsvExtension = [name[:-4] for name in os.listdir(folderCsvExtension) if not "Power Spectrum" in name]

def has_been_split(name):
    idx = name.index("#")
    n = len(name)
    if n-idx == 8:
        return False
    elif n-idx == 12:
        return True
    else:
        print("Warning: weird shit happening in the fluo name file.\n")
        return False

pathsFluo = []
for name in namesCsvExtension:
    if has_been_split(name):
        strCoreName = name[16:-4]
        print(strCoreName)
    else:
        strCoreName = name[16:]
    didFindFluorescence = False
    for root, dirs, files in os.walk(folderData):
        for file in files:
            if strCoreName in file and (("/fluo" in root) or ("\\fluo" in root)) and ".tdms" in file and not ".tdms_index" in file:
                pathsFluo.append((root+"/"+file).replace("\\", "/"))
                didFindFluorescence = True
    if not didFindFluorescence:
        print("Warrning: No fluorescent file for " + name+"\n")

def diff_HHMMSS(recordedTimeStrExt, recordedTimeStrFluo):
    extHour = int(recordedTimeStrExt/10000)
    extMin = int((recordedTimeStrExt-extHour*10000)/100)
    extSec = int((recordedTimeStrExt-extHour*10000-extMin*100))

    fluoHour = int(recordedTimeStrFluo/10000)
    fluoMin = int((recordedTimeStrFluo-fluoHour*10000)/100)
    fluoSec = int((recordedTimeStrFluo-fluoHour*10000-fluoMin*100))

    return float((fluoHour-extHour)*3600 + (fluoMin-extMin)*60 + fluoSec-extSec)

from PIL import Image

for (name, pathFluo) in zip(namesCsvExtension, pathsFluo):
    print(name)
    fluoData, fluoTimeRes = read_fluorescence_file_lumicks(pathFluo)
    dico = {"fluoTimeRes": [fluoTimeRes],
            "timeOffsetFile": [diff_HHMMSS(int(name[9:16]), int(os.path.basename(pathFluo)[9:16]))]}

    plt.imshow(np.array(fluoData["532nm"]))
    plt.savefig(folderSave+"/"+name+"_532nm"+".tif", format = "tif")

    plt.imshow(np.array(fluoData["638nm"]))
    plt.savefig(folderSave+"/"+name+"_638nm"+".tif", format = "tif")

    pd.DataFrame(dico).to_csv(folderSave+"/"+name+"_metaData"+".csv")
