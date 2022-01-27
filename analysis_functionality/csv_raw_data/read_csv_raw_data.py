import pandas as pd

def read_pickled_raw_data(folderData, fileName):
    filePath = folderData + "/" + fileName + ".csv"
    allRawData = pd.load(open(filePath))
    return allRawData