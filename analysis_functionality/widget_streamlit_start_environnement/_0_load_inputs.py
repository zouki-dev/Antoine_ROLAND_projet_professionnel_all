from analysis_functionality.tools.str_analysis import make_action_name
from analysis_functionality.tools.str_analysis import str_extension_remove


def load_inputs(folderProject, __file__parent, loadFrom="pickled_raw_data"):
    filePathAnalysis = __file__parent.replace("\\", "/")
    folderData = folderProject + "/" + loadFrom
    actionName = str_extension_remove(make_action_name(filePathAnalysis))
    return (filePathAnalysis, actionName)
# from analysis_functionality.action_streamlit_wlc_auto_fit.wlc_auto_fit._0load_inputs_add_folderAnalysis_to_sys import load_inputs_add_folderAnalysis_to_sys
# (folderAnalysis, folderProject, folderData, actionFilePath, actionName) = load_inputs_add_folderAnalysis_to_sys(folderAnalysis)