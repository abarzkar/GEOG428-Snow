"""
Main user function to retrieve snow depth with snow depth and wet snow flag
"""
import os
from os.path import join
from pathlib import Path
import pandas as pd
import xarray as xr
import shapely.geometry
from typing import Tuple, Union, List

# Add main repo to path
import sys
from os.path import expanduser
sys.path.append(expanduser('../'))

# import the functions for snow_index calculation
from spicy_snow.processing.snow_index import calc_delta_VV, calc_delta_cross_ratio, \
    calc_delta_gamma, clip_delta_gamma_outlier, calc_snow_index, calc_snow_index_to_snow_depth

def retrieval_from_parameters(dataset: xr.Dataset, 
                              A: float = 2, 
                              B: float = 0.5, 
                              C: float = 0.44):
    """
    Retrieve snow depth with varied parameter set from an already pre-processed
    dataset.

    Args:
    dataset: Already preprocessed dataset with s1, fcf, ims, deltaVV, merged images, 
    and masking applied.
    A: A parameter
    B: B parameter
    C: C parameter

    Returns:
    dataset: xarray dataset with snow_depth variable calculated from parameters
    """

    # dataset = dataset[['s1','deltaVV','ims','fcf','lidar-sd']]

    # load datast to index
    dataset = dataset.load()

    # calculate delta CR and delta VV
    dataset = calc_delta_cross_ratio(dataset, A = A)

    # calculate delta gamma with delta CR and delta VV with FCF
    dataset = calc_delta_gamma(dataset, B = B)

    # clip outliers of delta gamma
    dataset = clip_delta_gamma_outlier(dataset)

    # calculate snow_index from delta_gamma
    dataset = calc_snow_index(dataset)

    # convert snow index to snow depth
    dataset = calc_snow_index_to_snow_depth(dataset, C = C)


    return dataset
