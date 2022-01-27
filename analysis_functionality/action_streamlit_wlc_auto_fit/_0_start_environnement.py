from analysis_functionality.widget_streamlit_start_environnement.widget_streamlit_start_environnement import widget_streamlit_start_environnement
from analysis_functionality.python_list_output.parameters_save import parameters_save
from analysis_functionality.tools.str_analysis import str_extension_remove
from os import listdir
import streamlit as st
from analysis_functionality.python_list_output.parameters_read import parameter_read
from analysis_functionality.widget_streamlit_start_environnement._m1_save_widget_output import save_output_action
from analysis_functionality.python_list_output.parameters_read import parameter_read

folderProject="D:/projects/DHFR"
folderData = folderProject + "/csv_raw_data"
# start streamlit environnement
[allRawData, allAction, labels, parameters] = widget_streamlit_start_environnement(__file__parent=__file__, folderProject=folderProject)
# st.text(parameters)

save_output_action(allRawData, allAction, labels, parameters)
