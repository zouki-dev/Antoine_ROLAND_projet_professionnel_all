import streamlit as st

def parameter_read(labels, parameters, label_input):
    if label_input in labels:
        for (parameter, label) in zip(parameters, labels):
            if label == label_input:
                parameter_output = parameter
    else:
        parameter_output = None
    return parameter_output

# from analysis_functionality.python_list_output.parameters_read import parameter_read
# parameter_output = parameter_read(labels, parameters, label_input)