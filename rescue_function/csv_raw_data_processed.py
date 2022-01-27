import os
import pandas as pd
from foldometer.ixo.lumicks_c_trap import read_file_lumicks
import shutil
from analysis_functionality.wlc_manual_fit.load import get_calibration_from_power_spectrum
from analysis_functionality.tools.str_analysis import str_extension_remove
from os import listdir
from pathlib import Path
import nptdms
from nptdms import TdmsFile
import numpy as np
from analysis_functionality.tools.str_analysis import int_to_000str
from foldometer.ixo.lumicks_c_trap import process_lumicks_data


# __________________________________________________ Inputs ____________________________________________________________
folderProject = "D:/projects/actinin"
folderToAnalyse = folderProject + "/raw_data"
folderToSave = folderProject + "/csv_raw_data_processed"

#decrease MAX_SIZE_IN_MB if you have memory issue: TraceBack "unable to alocate dataFrame (n, m)"
MAX_SIZE_IN_MB = 50

COLUMN_CSV_OUTPUT = ["time", "trapSepX", "PSD1ForceX", "PSD2ForceX", "MirrorX", "forceX", "surfaceSepX"]

try:
    os.mkdir(folderToSave)
except:
    pass

# _________________________________________ Find files to analyse ______________________________________________________
def getListOfFiles(dirName, folderSave):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath, folderSave)
        else:
            allFiles.append(fullPath.replace("\\", "/"))
    filePathList = [f for f in allFiles if
                    (".tdms" in f) and not (".tdms_index" in f) and not ("Power Spectrum" in f) and not ("/fluo/" in f) and not any([os.path.basename(f)[:-5] in name for name in os.listdir(folderSave)])]

    return filePathList


filePathList = getListOfFiles(folderToAnalyse, folderToSave)


# _________________________________________ Read tdms and save csv _____________________________________________________c
print("File to read : " + str(len(filePathList)))

for i in range(len(filePathList)):
    filePath = filePathList[i]
    name = filePath.replace("\\", "/").replace(".", "-").split("/")[-1]
    size = os.path.getsize(filePath)/1000000
    print(str(i)+" : "+name[:-5] + "   " + str(int(size)) + " MB")

    for spectrumFileName in os.listdir(os.path.split(filePath)[0]):
        if spectrumFileName.endswith("Power Spectrum.tdms") and spectrumFileName[9:15] <= os.path.split(filePath)[1][9:15]:
            calibrationFilePath = os.path.join(os.path.split(filePath)[0], spectrumFileName)

    if size<MAX_SIZE_IN_MB:
        allRawData = read_file_lumicks(filePath).reset_index(drop=True)
        thermalCalibration = get_calibration_from_power_spectrum(os.path.dirname(calibrationFilePath),
                                                                 calibrationFilePath.replace("\\", "/").split("/")[-1][
                                                                 :-20], extension=".tdms")
        data = process_lumicks_data(allRawData, thermalCalibration, thermalCalibration, beadTracking=False)
        data[COLUMN_CSV_OUTPUT].to_csv(folderToSave + "/" + name[:-5] + ".csv")

        pd.DataFrame(thermalCalibration).to_csv(folderToSave + "/" + name[:-5] + " Power Spectrum.csv")

    else:
        CHANNEL_LABEL_MAPPING = {"Time (ms)": "time",
                                 "Distance 1 (um)": "trapSepX",
                                 "Distance 2 (um)": "trapSepY",
                                 "Force Channel 0 (pN)": "PSD1ForceX",
                                 "Force Channel 1 (pN)": "PSD1ForceY",
                                 "Force Channel 2 (pN)": "PSD2ForceX",
                                 "Force Channel 3 (pN)": "PSD2ForceY"}
        group_name = 'FD Data'
        maxPoints = MAX_SIZE_IN_MB * 10000
        with TdmsFile.open(filePath) as tdms_file:
            channel = tdms_file[group_name]["Time (ms)"]
            n = len(channel)
            for i in range(int(np.ceil(n / maxPoints))):
                if i==0:
                    print("Split in " + str(int(np.ceil(n / maxPoints))))
                dictSlice = {}
                for channel_name in CHANNEL_LABEL_MAPPING:
                    channel = tdms_file[group_name][channel_name]

                    if (i + 1) * maxPoints <= n:
                        dictSlice[CHANNEL_LABEL_MAPPING[channel_name]] = channel[i * maxPoints:(i + 1) * maxPoints]
                    else:
                        dictSlice[CHANNEL_LABEL_MAPPING[channel_name]] = channel[i * maxPoints:]
                dfSlice = pd.DataFrame(dictSlice)
                dfSlice["time"] /= 1000
                dfSlice["trapSepX"] *= 1e3
                dfSlice["MirrorX"] = dfSlice.loc[:, "trapSepX"]
                dfSlice["forceX"] = (dfSlice["PSD2ForceX"] - dfSlice["PSD1ForceX"]) / 2

                thermalCalibration = get_calibration_from_power_spectrum(os.path.dirname(calibrationFilePath),
                                                                         calibrationFilePath.replace("\\", "/").split(
                                                                             "/")[-1][:-20], extension=".tdms")
                dataSlice = process_lumicks_data(dfSlice, thermalCalibration, thermalCalibration, beadTracking=False)

                dataSlice[COLUMN_CSV_OUTPUT].to_csv(folderToSave + "/" + name[:-5] + "-" + int_to_000str(i) + ".csv")




                pd.DataFrame(thermalCalibration).to_csv(folderToSave + "/" + name[:-5] + "-" + int_to_000str(i) + " Power Spectrum.csv")





    # shutil.copyfile(calibrationFilePath, folderToSave + "/" + name[:-5] + " Power Spectrum.tdms")

print("finish")
