import os
import pandas as pd
from foldometer.ixo.lumicks_c_trap import read_file_lumicks
from analysis_functionality.wlc_manual_fit.load import get_calibration_from_power_spectrum
from nptdms import TdmsFile
import numpy as np
from analysis_functionality.tools.str_analysis import int_to_000str
import lumicks.pylake as lk
import streamlit as st

folderProject = 'S:/projects/Luca/dmMBP'
def csv_raw_data(folderProject=folderProject):
    # __________________________________________________ Inputs ____________________________________________________________
    folderData = folderProject + "/raw_data"
    folderToSave = folderProject + "/csv_raw_data"

    if ".h5" in [extension[-3:] for extension in os.listdir(folderData)]:
        freqWanted = 1 / 0.02  # Hz
        lenMax = 500000  # nb point max by file

        if not os.path.exists(folderToSave):
            os.mkdir(folderToSave)

        namesCsvRawData = [name[:-4] for name in os.listdir(folderToSave) if not "Power Spectrum" in name]
        names = [name[:-3] for name in os.listdir(folderData) if any([name[:-3] in nameCsv for nameCsv in namesCsvRawData])]
        try:
            st.text("nbData "+str(len(names)))
        except:
            pass
        for name in names[0:]:
            print(name)
            try:
                st.text(name)
            except:
                pass
            filePath = folderData + "/" + name + ".h5"
            file = lk.File(filePath)

            cali1x = file.force1x.calibration[0]
            cali2x = file.force2x.calibration[0]
            cali1y = file.force1y.calibration[0]
            cali2y = file.force2x.calibration[0]

            # diffusionTheory = ((constants.Boltzmann * (self.foldometerCalFit["temperature"] + 273.15))\
            #           / (3 * constants.pi * self.foldometerCalFit["viscosity"] * 1000 * self.foldometerCalFit["beadDiameter"] * 10 ** -9))
            # self.foldometerCalFit["diffusionExp"] = self.foldometerCalFit["diffusionTheory"] / (
            #         (self.foldometerCalFit["distanceResponse"] * 10 ** -6) ** 2)
            dictCalibration = {"beadDiameter": [cali1x['Bead diameter (um)'] * 1000, cali2x['Bead diameter (um)'] * 1000,
                                                cali1y['Bead diameter (um)'] * 1000, cali2y['Bead diameter (um)'] * 1000], \
                               "stiffness": [cali1x['kappa (pN/nm)'], cali2x['kappa (pN/nm)'], cali1y['kappa (pN/nm)'],
                                             cali2y['kappa (pN/nm)']], \
                               "diffusionExp": [cali1x['D (V^2/s)'] * (cali1x['Rd (um/V)'] * 10e-6) ** 2,
                                                cali2x['D (V^2/s)'] * (cali2x['Rd (um/V)'] * 10e-6) ** 2,
                                                cali1y['D (V^2/s)'] * (cali1y['Rd (um/V)'] * 10e-6) ** 2,
                                                cali2y['D (V^2/s)'] * (cali2y['Rd (um/V)'] * 10e-6) ** 2], \
                               "alpha": [cali1x['alpha'], cali2x['alpha'], cali1y['alpha'], cali2y['alpha']], \
                               "beta": [cali1x['fc (Hz)'], cali2x['fc (Hz)'], cali1y['fc (Hz)'], cali2y['fc (Hz)']], \
                               "distanceResponse": [cali1x['Rd (um/V)'] * 1000, cali2x['Rd (um/V)'] * 1000,
                                                    cali1y['Rd (um/V)'] * 1000, cali2y['Rd (um/V)'] * 1000], \
                               "forceResponse": [cali1x['Rf (pN/V)'], cali2x['Rf (pN/V)'], cali1y['Rf (pN/V)'],
                                                 cali2y['Rf (pN/V)']], \
                               "viscosity": [cali1x['Viscosity (Pa*s)'], cali2x['Viscosity (Pa*s)'],
                                             cali1y['Viscosity (Pa*s)'], cali2y['Viscosity (Pa*s)']], \
                               "cornerFrequency": [cali1x['fc (Hz)'], cali2x['fc (Hz)'], cali1y['fc (Hz)'],
                                                   cali2y['fc (Hz)']]}
            calibration = pd.DataFrame(dictCalibration, index=["PSD1x", "PSD2x", "PSD1y", "PSD2y"])
            # print(calibration["diffusionExp"])

            time = (file.force1x.timestamps - file.force1x.timestamps[0]) / 10 ** 9
            force = (file.force1x.data - file.force2x.data) / 2
            PSD1ForceX = -file.force1x.data
            PSD2ForceX = -file.force2x.data
            PSD1xDisplacement = -(PSD1ForceX / calibration.loc["PSD1x", "stiffness"])
            PSD2xDisplacement = (PSD2ForceX / calibration.loc["PSD2x", "stiffness"])
            surfaceSepX = file["Distance"]["Piezo Distance"].data * 10 ** 3
            trapSepX = surfaceSepX + calibration.loc["PSD1x", "beadDiameter"] / 2 + calibration.loc[
                "PSD2x", "beadDiameter"] / 2 \
                       + PSD2xDisplacement + PSD1xDisplacement
            dictData = {"time": time, \
                        "forceX": force, \
                        "surfaceSepX": surfaceSepX, \
                        "PSD1ForceX": PSD1ForceX, \
                        "PSD2ForceX": PSD2ForceX, \
                        "trapSepX": trapSepX}
            data = pd.DataFrame(dictData)
            data.set_index("time")
            freq = 1 / data["time"].diff().mean()

            data["time"] = ((data["time"] * freq / freqWanted).astype(int).astype(float) * freqWanted / freq)
            dataResample = data.groupby("time").mean()

            n = len(dataResample)
            if n <= lenMax:
                calibration.to_csv(folderToSave + "/" + name + " Power Spectrum.csv")
                dataResample.to_csv(folderToSave + "/" + name + ".csv")
            else:
                print("Split in " + str(int(n / lenMax) + 1))
                for i in range(int(n / lenMax) + 1):
                    calibration.to_csv(folderToSave + "/" + name + "-" + str(i) + " Power Spectrum.csv")
                    try:
                        dataResample.iloc[i * lenMax:(i + 1) * lenMax].to_csv(
                            folderToSave + "/" + name + "-" + str(i) + ".csv")
                    except:
                        dataResample.iloc[i * lenMax:].to_csv(folderToSave + "/" + name + "-" + str(i) + ".csv")








    else:
        #decrease MAX_SIZE_IN_MB if you have memory issue: TraceBack "unable to alocate dataFrame (n, m)"
        MAX_SIZE_IN_MB = 50

        COLUMN_CSV_OUTPUT = ["time", "trapSepX", "PSD1ForceX", "PSD2ForceX", "MirrorX", "forceX"]

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


        filePathList = getListOfFiles(folderData, folderToSave)


        # _________________________________________ Read tdms and save csv _____________________________________________________c
        print("File to read : " + str(len(filePathList)))
        try:
            st.text("File to read : " + str(len(filePathList)))
        except:
            pass

        for i in range(len(filePathList)):
            filePath = filePathList[i]
            name = filePath.replace("\\", "/").replace(".", "-").split("/")[-1]
            size = os.path.getsize(filePath)/1000000
            print(str(i)+" : "+name[:-5] + "   " + str(int(size)) + " MB")
            try:
                st.text(str(i)+" : "+name[:-5] + "   " + str(int(size)) + " MB")
            except:
                pass
            for spectrumFileName in os.listdir(os.path.split(filePath)[0]):
                if spectrumFileName.endswith("Power Spectrum.tdms") and spectrumFileName[9:15] <= os.path.split(filePath)[1][9:15]:
                    calibrationFilePath = os.path.join(os.path.split(filePath)[0], spectrumFileName)

            if size<MAX_SIZE_IN_MB:
                allRawData = read_file_lumicks(filePath).reset_index(drop=True)
                allRawData[COLUMN_CSV_OUTPUT].to_csv(folderToSave + "/" + name[:-5] + ".csv")

                thermalCalibration = get_calibration_from_power_spectrum(os.path.dirname(calibrationFilePath),
                                                                         calibrationFilePath.replace("\\", "/").split("/")[-1][
                                                                         :-20], extension=".tdms")
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
                        dfSlice[COLUMN_CSV_OUTPUT].to_csv(folderToSave + "/" + name[:-5] + "-" + int_to_000str(i) + ".csv")

                        thermalCalibration = get_calibration_from_power_spectrum(os.path.dirname(calibrationFilePath),
                                                                                 calibrationFilePath.replace("\\", "/").split(
                                                                                     "/")[-1][:-20], extension=".tdms")
                        pd.DataFrame(thermalCalibration).to_csv(folderToSave + "/" + name[:-5] + "-" + int_to_000str(i) + " Power Spectrum.csv")



    print("finish")
    st.balloons()

if __name__ == '__main__':
    csv_raw_data()