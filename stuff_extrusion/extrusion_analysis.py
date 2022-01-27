import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

folderProject = "D:/projects/ubiquitin"
folderData = folderProject + "/" + "wlc_manual_fit_extrusion"
folderExtrusionDetection = folderProject + "/" + "extrusion_detection"

epsilon = 0.05

def calculate_rolling_slopes(data, window=600, columnY="proteinLc", center=True):
    df = data[["time", columnY]]
    df.index = df["time"]

    dt = df["time"].diff().mean()

    def summing_window(data):
        return (data * np.arange(1, len(data) + 1)).sum()

    # print(self.metadata["sampleFreq"])
    denominator = dt / 12 * (2 * window + window ** 3)
    slope = (df[columnY].rolling(window, center=center).apply(summing_window, raw=True) - window /
              2 * df[columnY].rolling(window, center=center).mean() * (window + 1)) / denominator
    return slope

filesContainingExtrusion = os.listdir(folderExtrusionDetection)
listDelaLc = []
listSpeedMean = []
listSpeedMedian = []
for fileName in filesContainingExtrusion:
    print(fileName)
    data = pd.read_csv(folderData+ "/" + fileName)
    extrusionsTimePoints = np.array(pd.read_csv(folderExtrusionDetection + "/" + fileName))
    for [t0,t1] in extrusionsTimePoints:
        maskT0 = (data["time"] >= t0-epsilon) & (data["time"] <= t0+epsilon)
        maskT1 = (data["time"] >= t1-epsilon) & (data["time"] <= t1+epsilon)
        Lc0 = data["proteinLc"].loc[maskT0].mean()
        Lc1 = data["proteinLc"].loc[maskT1].mean()
        deltaLc = Lc1 - Lc0

        maskExtrusion = (data["time"] >= t0) & (data["time"] <= t1)
        slope = calculate_rolling_slopes(data, window=600, columnY="proteinLc", center=True)
        data["slope"] = np.array(slope)
        speedMean = data["slope"].loc[maskExtrusion].mean()
        speedMedian = data["slope"].loc[maskExtrusion].median()

        listDelaLc.append(deltaLc)
        listSpeedMean.append(speedMean)
        listSpeedMedian.append(speedMedian)


print(listDelaLc)
print(listSpeedMean)
print(listSpeedMedian)


