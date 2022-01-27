import os

def compact_file_name(fileName):
    date = fileName[:8]
    i = fileName.find("#")
    id = fileName[i:]
    return date+id
# from analysis_functionality.tools.str_analysis import compact_file_name
# Bla_Bla_XXX_XXX = compact_file_name(fileName)

def int_to_000str(i):
    strI = str(i)
    return "0"*(3-len(strI)) + strI

def make_action_name(__file__input):
    actionName = __file__input.replace("\\", "/").split("/")[-1]
    # print(actionName)
    return actionName
# # from analysis_functionality.tools.str_analysis import make_action_name
# # current_action_file_name = make_action_name(__file__)

def make_experiment_name(fileName):
    nameMaker = fileName.split(" ")
    return nameMaker[0][:8]+" "+nameMaker[1]

def str_extension_remove(name_extension):
    nameMaker = name_extension.split(".")
    nMaker = len(nameMaker)
    # print(nameMaker)
    # print(nMaker)
    if nMaker == 2:
        name = nameMaker[0]
    elif nMaker == 3:
        name = [nameMaker[0] + "." + nameMaker[1]]
    elif nMaker < 2:
        # print("warning, no extension in the name. name might be corrupt (no point in the filePath).")
        return name_extension
    else:
        # print("warning, no extension in the name. name might be very corrupt (Multiple point in the filePath).")
        return name_extension

    return name
# # from analysis_functionality.tools.str_analysis import str_extension_remove
# # name = str_extension_remove(name_extension)

def str_extension_select(name_extension):
    nameMaker = name_extension.split(".")
    extension = nameMaker[-1]
    return extension