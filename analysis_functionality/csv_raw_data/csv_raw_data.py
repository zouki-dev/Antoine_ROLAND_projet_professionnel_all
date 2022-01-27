import os
import pandas as pd
from foldometer.ixo.lumicks_c_trap import read_file_lumicks
import shutil

folder = "D:/projects/ubiquitin"
folderToAnalyse = folder + "/raw_data"
folderToSave = folder + "/csv_raw_data"

REQUIRED_INPUT = "raw_data"
COLUMN_CSV_OUTPUT = ["time", "trapSepX", "PSD1ForceX", "PSD2ForceX", "MirrorX", "forceX"]

try:
    os.mkdir(folderToSave)
except:
    pass

def getListOfFiles(dirName):
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
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath.replace("\\", "/"))
    filePathList = [f for f in allFiles if
                    (".tdms" in f) and not (".tdms_index" in f) and not ("Power Spectrum" in f) and not ("/fluo/" in f)]
    return filePathList

filePathList = getListOfFiles(folderToAnalyse)

print("File to read : " + str(len(filePathList)))

for i in range(len(filePathList)):
    filePath = filePathList[i]
    name = filePath.replace("\\", "/").split("/")[-1]

    print(str(i)+" : "+name[:-5])
    allRawData = read_file_lumicks(filePath).reset_index(drop=True)

    a = allRawData[COLUMN_CSV_OUTPUT].to_csv(folderToSave + "/" + name[:-5] + ".csv")


    for spectrumFileName in os.listdir(os.path.split(filePath)[0]):
        if spectrumFileName.endswith("Power Spectrum.tdms") and spectrumFileName[9:15] <= os.path.split(filePath)[1][9:15]:
            calibrationFilePath = os.path.join(os.path.split(filePath)[0], spectrumFileName)

    shutil.copyfile(calibrationFilePath, folderToSave + "/" + name[:-5] + " Power Spectrum.tdms")

print("finish")
