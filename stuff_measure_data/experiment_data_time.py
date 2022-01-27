import os
import pandas as pd

folderProject = "D:/projects/ubiquitin_K48chain"
folderData = folderProject + "/" + "wlc_manual_fit"
folderSave = folderProject + "/" + "experiment_data_time"

if not os.path.exists(folderSave):
    os.mkdir(folderSave)

names = [name[:-4] for name in os.listdir(folderData)]

timeExperiment = 0
experimentName_1 = names[0][0:8] + "_" + " ".join(names[0].split(" ")[1:-1])
print(len(names))
for (i,name) in enumerate(names):
    print(str(i)+": "+name)
    experimentName = name[0:8] + "_" + " ".join(name.split(" ")[1:-1])
    data = pd.read_csv(folderData + "/" + name + ".csv")
    timeExperiment += data["time"].max() - data["time"].min()

    if experimentName != experimentName_1:
        f = open(folderSave + "/" + experimentName_1 + ".txt", "a")
        f.write(str(int(timeExperiment)))
        f.close()
        experimentName_1 = experimentName
        timeExperiment = 0
f = open(folderSave + "/" + experimentName + ".txt", "a")
f.write(str(int(timeExperiment)))
f.close()
