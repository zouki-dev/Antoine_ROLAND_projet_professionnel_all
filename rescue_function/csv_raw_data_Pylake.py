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
import lumicks.pylake as lk
import matplotlib.pyplot as plt
from scipy import constants

# __________________________________________________ Inputs ____________________________________________________________
folderProject = "D:/projects/pylake"
folderData = folderProject + "/raw_data"
folderToSave = folderProject + "/csv_raw_data"

freqWanted = 1/0.02 #Hz
lenMax = 500000 #nb point max by file


if not os.path.exists(folderToSave):
    os.mkdir(folderToSave)

names = [name[:-3] for name in os.listdir(folderData)]
for name in names[0:]:
    print(name)
    filePath = folderData+"/"+name+".h5"
    file = lk.File(filePath)

    cali1x = file.force1x.calibration[0]
    cali2x = file.force2x.calibration[0]
    cali1y = file.force1y.calibration[0]
    cali2y = file.force2x.calibration[0]

    # diffusionTheory = ((constants.Boltzmann * (self.foldometerCalFit["temperature"] + 273.15))\
    #           / (3 * constants.pi * self.foldometerCalFit["viscosity"] * 1000 * self.foldometerCalFit["beadDiameter"] * 10 ** -9))
    # self.foldometerCalFit["diffusionExp"] = self.foldometerCalFit["diffusionTheory"] / (
    #         (self.foldometerCalFit["distanceResponse"] * 10 ** -6) ** 2)
    dictCalibration = {"beadDiameter": [cali1x['Bead diameter (um)']*1000, cali2x['Bead diameter (um)']*1000, cali1y['Bead diameter (um)']*1000, cali2y['Bead diameter (um)']*1000], \
                       "stiffness": [cali1x['kappa (pN/nm)'], cali2x['kappa (pN/nm)'], cali1y['kappa (pN/nm)'], cali2y['kappa (pN/nm)']], \
                       "diffusionExp": [cali1x['D (V^2/s)']*(cali1x['Rd (um/V)']*10e-6)**2, cali2x['D (V^2/s)']*(cali2x['Rd (um/V)']*10e-6)**2, cali1y['D (V^2/s)']*(cali1y['Rd (um/V)']*10e-6)**2, cali2y['D (V^2/s)']*(cali2y['Rd (um/V)']*10e-6)**2], \
                       "alpha": [cali1x['alpha'], cali2x['alpha'], cali1y['alpha'], cali2y['alpha']], \
                       "beta": [cali1x['fc (Hz)'], cali2x['fc (Hz)'], cali1y['fc (Hz)'], cali2y['fc (Hz)']], \
                       "distanceResponse": [cali1x['Rd (um/V)']*1000, cali2x['Rd (um/V)']*1000, cali1y['Rd (um/V)']*1000, cali2y['Rd (um/V)']*1000], \
                       "forceResponse": [cali1x['Rf (pN/V)'], cali2x['Rf (pN/V)'], cali1y['Rf (pN/V)'], cali2y['Rf (pN/V)']], \
                       "viscosity": [cali1x['Viscosity (Pa*s)'], cali2x['Viscosity (Pa*s)'], cali1y['Viscosity (Pa*s)'], cali2y['Viscosity (Pa*s)']], \
                       "cornerFrequency": [cali1x['fc (Hz)'], cali2x['fc (Hz)'], cali1y['fc (Hz)'], cali2y['fc (Hz)']]}
    calibration = pd.DataFrame(dictCalibration, index=["PSD1x", "PSD2x", "PSD1y", "PSD2y"])
    # print(calibration["diffusionExp"])

    time = (file.force1x.timestamps - file.force1x.timestamps[0])/10**9
    force = (file.force1x.data - file.force2x.data) / 2
    PSD1ForceX = -file.force1x.data
    PSD2ForceX = -file.force2x.data
    PSD1xDisplacement = -(PSD1ForceX / calibration.loc["PSD1x", "stiffness"])
    PSD2xDisplacement = (PSD2ForceX / calibration.loc["PSD2x", "stiffness"])
    surfaceSepX = file["Distance"]["Piezo Distance"].data*10**3
    trapSepX = surfaceSepX + calibration.loc["PSD1x", "beadDiameter"]/2 + calibration.loc["PSD2x", "beadDiameter"]/2 \
               + PSD2xDisplacement + PSD1xDisplacement
    dictData = {"time": time, \
                "forceX": force, \
                "surfaceSepX": surfaceSepX, \
                "PSD1ForceX": PSD1ForceX, \
                "PSD2ForceX": PSD2ForceX, \
                "trapSepX": trapSepX}
    data = pd.DataFrame(dictData)
    data.set_index("time")
    freq = 1/data["time"].diff().mean()

    data["time"] = ((data["time"]*freq/freqWanted).astype(int).astype(float)*freqWanted/freq)
    dataResample = data.groupby("time").mean()

    n = len(dataResample)
    if n <= lenMax:
        calibration.to_csv(folderToSave+"/"+name+" Power Spectrum.csv")
        dataResample.to_csv(folderToSave+"/"+name+".csv")
    else:
        print("Split in "+str(int(n/lenMax)+1))
        for i in range(int(n/lenMax)+1):
            calibration.to_csv(folderToSave+"/"+name+"-"+str(i)+" Power Spectrum.csv")
            try:
                dataResample.iloc[i*lenMax:(i+1)*lenMax].to_csv(folderToSave+"/"+name+"-"+str(i)+".csv")
            except:
                dataResample.iloc[i*lenMax:].to_csv(folderToSave+"/"+name+"-"+str(i)+".csv")
    print("Done")


