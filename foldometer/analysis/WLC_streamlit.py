import streamlit as st
import foldometer as fm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from foldometer.analysis.wlc_curve_fit import wlc_series_accurate
import os
from matplotlib.figure import Figure
import pickle





def update_extension_offset(m, forceMask, fitMagicExtensionOffset, extensionOffset):
    print(len(forceMask))
    print(len(m.data["surfaceSepX"]))
    curvePositionReal = m.data["surfaceSepX"].loc[forceMask].mean()

    forceArray = np.arange(0.5, 60, 0.2)
    extensionWLC = wlc_series_accurate(forceArray, \
                    contourLengthDNA=m.paramsWLC["contourLengthDNA"], \
                    persistenceLengthDNA=m.paramsWLC["persistenceLengthDNA"], \
                    stretchModulusDNA=m.paramsWLC["stretchModulusDNA"], \
                    contourLengthProtein=m.proteinLength, \
                    persistenceLengthProtein=m.paramsWLC["persistenceLengthProtein"])

    mask = (forceArray>=25)*(forceArray<=30)
    WLCposition = (pd.DataFrame(extensionWLC).loc[mask]).mean()

    extensionOffset += curvePositionReal - WLCposition + fitMagicExtensionOffset
    return extensionOffset[0]

def make_force_mask(m, minForce=25, maxForce=30):
    return (m.data["forceX"]>=minForce)*(m.data["forceX"]<=maxForce)
