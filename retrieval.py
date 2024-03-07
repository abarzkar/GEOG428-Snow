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

# import the functions for wet snow flag
from spicy_snow.processing.wet_snow import id_newly_frozen_snow, id_newly_wet_snow, \
    id_wet_negative_si, flag_wet_snow

def retrieve_snow_depth(area: shapely.geometry.Polygon, 
                        dates: Tuple[str, str], 
                        work_dir: str = './',
                        job_name: str = 'spicy-snow-run',
                        existing_job_name: Union[bool, str] = False,
                        debug: bool = False,
                        ims_masking: bool = True,
                        wet_snow_thresh: float = -2,
                        freezing_snow_thresh: float = 1,
                        wet_SI_thresh: float = 0,
                        outfp: Union[str, Path, bool] = False,
                        params: List[float] = [2.5, 0.2, 0.55]) -> xr.Dataset:
    """
    Finds, downloads Sentinel-1, forest cover, water mask (not implemented), and 
    snow coverage. Then retrieves snow depth using Lievens et al. 2021 method.

    Args:
    area: Shapely geometry to use as bounding box of desired area to search within
    dates: Start and end date to search between
    work_dir: filepath to directory to work in. Will be created if not existing
    job_name: name for hyp3 job
    existing_job_name: name for preexisiting hyp3 job to download and avoid resubmitting
    debug: do you want to get verbose logging?
    ims_masking: do you want to mask pixels by IMS snow free imagery?
    wet_snow_thresh: what threshold in dB change to use for melting and re-freezing snow? Default: -2
    freezing_snow_thresh: what threshold in dB change to use for re-freezing snow id. Default: +2
    wet_SI_thresh: what threshold to use for negative snow index? Default: 0
    outfp: do you want to save netcdf? default is False and will just return dataset
    params: the A, B, C parameters to use in the model. Current defaults are optimized to north america

    Returns:
    datset: Xarray dataset with 'snow_depth' and 'wet_snow' variables for all Sentinel-1
    image acquistions in area and dates
    """

    ## argument checking
    assert isinstance(area, shapely.geometry.Polygon), f"Must provide shapely geometry for area. Got {type(area)}"

    assert isinstance(dates, list) or isinstance(dates, tuple)
    assert len(dates) == 2, f"Can only provide two dates to work between. Got {dates}"

    assert isinstance(work_dir, str) or isinstance(work_dir, Path)
    if isinstance(work_dir, Path):
        work_dir = str(work_dir)
    
    assert isinstance(debug, bool), f"Debug keyword must be boolean. Got {debug}"

    assert isinstance(params, list) or isinstance(params, tuple), f"param keyword must be list or tuple. Got {type(params)}"
    assert len(params) == 3, f"List of params must be 3 in order A, B, C. Got {params}"
    A, B, C = params

    if type(outfp) != bool:
        outfp = Path(outfp).expanduser().resolve()
        assert outfp.parent.exists(), f"Out filepath {outfp}'s directory does not exist"

    ## set up directories and logging

    os.makedirs(work_dir, exist_ok = True)

    setup_logging(log_dir = join(work_dir, 'logs'), debug = debug)
    log = logging.getLogger(__name__)

    if wet_snow_thresh >= 0:
        log.warning(f"Running with wet snow threshold of {wet_snow_thresh}. This value is positive but should be negative.")
    
    if freezing_snow_thresh <= 0:
        log.warning(f"Running with refreeze threshold of {freezing_snow_thresh}. This value is negative but should be positive.")
    
    

    ## Snow Index Steps
    log.info("Calculating snow index")
    # calculate delta CR and delta VV
    ds = calc_delta_cross_ratio(ds, A = A)
    ds = calc_delta_VV(ds)

    # calculate delta gamma with delta CR and delta VV with FCF
    ds = calc_delta_gamma(ds, B = B)

    # clip outliers of delta gamma
    ds = clip_delta_gamma_outlier(ds)

    # calculate snow_index from delta_gamma
    ds = calc_snow_index(ds, ims_masking = ims_masking)

    # convert snow index to snow depth
    ds = calc_snow_index_to_snow_depth(ds, C = C)


    ds.attrs['param_A'] = A
    ds.attrs['param_B'] = B
    ds.attrs['param_C'] = C

    ds.attrs['job_name'] = job_name

    ds.attrs['bounds'] = area.bounds

    if outfp:
        outfp = str(outfp)
        
        ds.to_netcdf(outfp)

    return ds

def retrieval_from_parameters(dataset: xr.Dataset, 
                              A: float, 
                              B: float, 
                              C: float, 
                              wet_SI_thresh: float = 0, 
                              freezing_snow_thresh: float = 2,
                              wet_snow_thresh: float = -2):
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

    # find newly wet snow
    dataset = id_newly_wet_snow(dataset, wet_thresh = wet_snow_thresh)
    dataset = id_wet_negative_si(dataset, wet_SI_thresh = wet_SI_thresh)

    # find newly frozen snow
    dataset = id_newly_frozen_snow(dataset, freeze_thresh =  freezing_snow_thresh)

    # make wet_snow flag
    dataset = flag_wet_snow(dataset)

    return dataset
