import streamlit as st

def print_parameters(labels, parameters):
    for [label, parameter] in zip(labels, parameters):
        st.text("")
        st.text(label + " : ")
        st.text(parameter)
