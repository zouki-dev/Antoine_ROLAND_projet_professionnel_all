import streamlit as st
import os
import pandas as pd
import numpy as np
from analysis_functionality.tools.str_analysis import compact_file_name
from analysis_functionality.tools.str_analysis import make_action_name
from analysis_functionality.tools.str_analysis import int_to_000str
from analysis_functionality.tools.str_analysis import str_extension_remove
from analysis_functionality.tools.str_analysis import str_extension_select



# a = 1
# b = "2"
# c = [3,4]
# d = 1.1
# e = np.zeros((3))
#
# labels = ["a", "b", "c", "d", "e"]
# parameters = [a, b, c, d, e]

def make_the_dict(labels, parameters):
    parameters_dict = {}
    label_parameters_dict = []
    for (label, parameter) in zip(labels, parameters):
        parameter_type_str = str(type(parameter))
        # print(parameter_type_str)
        if parameter_type_str == "<class 'int'>":
            parameters_dict[label] = [parameter]
            label_parameters_dict.append(label)
        elif parameter_type_str == "<class 'str'>":
            parameters_dict[label] = [parameter]
            label_parameters_dict.append(label)
        elif parameter_type_str == "<class 'float'>":
            parameters_dict[label] = [parameter]
            label_parameters_dict.append(label)
        elif parameter_type_str == "<class 'numpy.float64'>":
            parameters_dict[label] = [float(parameter)]
            label_parameters_dict.append(label)
        elif parameter_type_str == "<class 'list'>":
            parameters_dict[label] = [str(parameter)]
            label_parameters_dict.append(label)
        elif parameter_type_str == "<class 'numpy.ndarray'>":
            parameters_dict[label] = [str([p for p in parameter])]
            label_parameters_dict.append(label)
        elif type(parameter) == np.int64:
            parameters_dict[label] = [int(parameter)]
            label_parameters_dict.append(label)
        else:
            print("You need to edit the 'make_the_dict' in analysis/functionality/tools/csv_tools. And add the " + str(type(parameter)) + " to the elif")
            print("Or remove it from the list")
            # st.warning("You need to edit the 'make_the_dict' in analysis/functionality/tools/csv_tools. And add the " + str(type(parameter)) + " to the elif")
    # print(label_parameters_of_dict)
    # print(parameters_dict)
    return (label_parameters_dict, parameters_dict)

# (label_parameters_of_dict, parameters_dict) = make_the_dict(labels, parameters)


def saveDataFrameOneRawToCsv(label_parameters_of_dict, parameters_dict, dataFrameOneRaw, folderSave, fileName):
    # if folderSave
    if os.path.exists(folderSave+"/"+fileName+".csv"):
        dataFrame = pd.read_csv(folderSave+"/"+fileName+".csv")[label_parameters_of_dict]
        # print(dataFrame)

        dataFrame_update = pd.concat([dataFrame, dataFrameOneRaw])
        dataFrame_update.to_csv(folderSave+"/"+fileName+".csv")
        # print(dataFrame_update)
    else:
        dataFrameOneRaw = pd.DataFrame(parameters_dict, index=[0])
        dataFrameOneRaw.to_csv(folderSave + "/" + fileName + ".csv", mode='a')
    return
# dataFrameOneRaw = pd.DataFrame(parameters_dict, index=[4])[label_parameters_dict]
# folderSave = "."
# fileName = "parameters_test"
# saveDataFrameOneRawToCsv(label_parameters_of_dict, dataFrameOneRaw, folderSave, fileName)