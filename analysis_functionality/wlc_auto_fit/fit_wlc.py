import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import streamlit as st
import pandas as pd
import os
from foldometer.ixo.data_conversion import process_data, data_beadData_merging
from foldometer.ixo.lumicks_c_trap import process_lumicks_data
from foldometer.analysis.region_classification import assign_regions
from foldometer.analysis.event_classification import find_unfolding_events
from foldometer.analysis.wlc_curve_fit import wlc_fit_data, protein_contour_length, protein_contour_length_accurate

def fit_wlc(data):
    """
    Method to fit the different pulling curves to the WLC using a series of two WLC models by Odjik (1995)

    Args:
        recalculateExtensions (bool): add the contour length changes to unfoldingEvents
        kwargs: keyword arguments for the fitting function, see fm.analysis.wlc_curve_fit.wlc_fit_data for info
    """

    def recalculate_extension_change(pullingCycles):
        """
        Based on the fitted WLC regions, estimate the change in contour length of each unfolding event
        Args:
            pullingCycles (list): list with the pulling cycles to consider
        """
        extensions = []
        extensionErrors = []
        for pullingCycle in pullingCycles.unique():
            wlcRegions = [region for region in data.loc[data["pullingCycle"] == pullingCycle,
                                                        "wlcRegion"].unique() if region != -1]
            for wlcRegion in np.arange(len(wlcRegions) - 1):
                if wlcRegions[wlcRegion] in fits.keys() and wlcRegions[wlcRegion + 1] in \
                        fits.keys():
                    param1 = fits[wlcRegions[wlcRegion + 1]].params["contourLengthProtein"]
                    param0 = fits[wlcRegions[wlcRegion]].params["contourLengthProtein"]
                    extensions.append(abs(param1.value - param0.value))
                    extensionErrors.append(np.sqrt((param1.stderr) ** 2 + (param0.stderr) ** 2))
                else:
                    extensions.append(np.nan)
                    extensionErrors.append(np.nan)

        return extensions, extensionErrors

    extensionOffset = 0
    temporal = data["surfaceSepX"].mean()
    data, fits = wlc_fit_data(data)
    extensionOffset += temporal - data["surfaceSepX"].mean()  # accumulate extension offsets

    # if recalculateExtensions:
    #     unfoldingEvents["extensionChange"], unfoldingEvents["extensionChangeError"] = \
    #         recalculate_extension_change(unfoldingEvents["pullingCycle"])
    Lc = []
    LcErrors = []
    for key in fits:
        Lc.append(fits[key].params["contourLengthProtein"].value)
        LcErrors.append(fits[key].params["contourLengthProtein"].stderr)
    contourLengths = pd.DataFrame(data={"wlcRegion": list(fits.keys()), "contourLength": Lc,
                                        "contourLengthError": LcErrors})
    pullingCycles = pd.DataFrame(data.groupby("wlcRegion")["pullingCycle"].max())
    pullingCycles["wlcRegion"] = pullingCycles.index
    pullingCycles.index = pullingCycles.index.values
    contourLengths = contourLengths.merge(pullingCycles, how="inner", on="wlcRegion")

    contourLengths[["maximumForce", "region"]] = data.groupby(["wlcRegion"])["forceX", "region"].max()[0:]

    labelsWLC = ["persistenceLengthProtein", "persistenceLengthDNA", "contourLengthDNA", "stretchModulusDNA"]
    paramsWLC = {}
    for paramLabel in labelsWLC:
        paramsWLC[paramLabel] = np.mean([fits[fit].params[paramLabel].value
                                         for fit in fits])
    return (data, paramsWLC, fits)
