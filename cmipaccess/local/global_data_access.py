import xarray as xr 
import glob
from tqdm import tqdm
import cftime
import os
import numpy as np
from cmipaccess.tools import sort_realisations
import pandas as pd


from ..local.config import GLOBAL_MEAN_DATA_DIR    




def get_global_time_series(model, experiment, variable, realisation, **kwargs):
    """Return an xarray Dataset containing a global mean time series of the variable required.

    Args:
        model (str): Climate model
        experiment (str): Experiment id
        variable (str): variable name
        realisation (str): member id

    Raises:
        ValueError: An error is raised if the global mean data is not found on spiritX.

    Returns:
        xarray.Dataset: _description_
    """
    file = glob.glob(f"{GLOBAL_MEAN_DATA_DIR}/*/{model}/{experiment}/{realisation}/{variable}_*")
    if len(file)==0:
        raise ValueError('Global mean data not readily available on spiritx')
    return xr.open_dataset(file[0], **kwargs)


def get_all_detrended_global_time_series(model, experiment, variable, no_parent=False, 
                                         remove_if_control_less_than='max', warn_too_short_control=False, 
                                         convert_time_to_datetime=True,
                                         progress=True, **kwargs):
    """Returns all global mean time series for a given experiment, model and variable. The time series are corrected for control experiment drift.

    Args:
        model (str): Climate model
        experiment (str): experiment
        variable (str): variable name
        no_parent (bool, optional): Specify if the experiment has no parent (required for amip experiments). Defaults to False.
        remove_if_control_less_than (str or int, optional): does not load timeseries if parrallel control run is shorter than this value. Defaults to 'max'.
        warn_too_short_control (bool, optional): Prints warning when control experiment is too short. Defaults to False.
        convert_time_to_datetime (bool, optional): Converts cftime read with xarray to pandas datetime. Defaults to True.
        progress (bool, optional): Shows a progressbar for all realisations. Defaults to True.

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if no_parent:
        files = glob.glob(f"{GLOBAL_MEAN_DATA_DIR}/*/{model}/{experiment}/*/{variable}_*")
    else: #detrending only works for CMIP6
        files = glob.glob(f"{GLOBAL_MEAN_DATA_DIR}/CMIP6/{model}/{experiment}/*/{variable}_*")
    if len(files)==0:
        raise ValueError('Global mean data not readily available on spiritx')
    realisations = sort_realisations([file.split('/')[-2] for file in files])
    all_control = dict()
    all_detrended_data = []
    if progress:
        iterable = tqdm(realisations)
    else:
        iterable = realisations
    for realisation in iterable:
        # Load experiment data
        experiment_data = get_global_time_series(model, experiment, variable, realisation, use_cftime=True, **kwargs)
        if not no_parent:
            # Get parent information and load control data
            parent_experiment_id = experiment_data.attrs['parent_experiment_id']
            parent_variant_label = experiment_data.attrs['parent_variant_label']
            control_data_key = 'parent_experiment_id/parent_variant_label'
            if control_data_key in all_control:
                control_data = all_control[control_data_key]
            else:
                control_data = get_global_time_series(model, parent_experiment_id, variable, parent_variant_label, use_cftime=True, **kwargs)
                all_control[control_data_key] = control_data
            # Get branch time in parent time units
            branch_time_int = experiment_data.attrs['branch_time_in_parent']
            parents_time_units = experiment_data.attrs['parent_time_units']
            branch_time = cftime.num2date(branch_time_int, calendar=experiment_data.time.values[0].calendar, units = parents_time_units)
            # get piControl parallel to experiment
            control_data_extract = control_data.sel(time=slice(branch_time, None)).isel(time = slice(0, experiment_data.time.size))[variable]
            control_data_extract = control_data_extract.assign_coords(time=experiment_data.time.values[:control_data_extract.time.size])
            #Check control extract size
            control_years = control_data_extract.count('time')/12
            if remove_if_control_less_than == 'max':
                control_min_length = experiment_data.time.size/12
            else:
                control_min_length = remove_if_control_less_than
            if control_years < control_min_length:
                if warn_too_short_control:
                    print(f'{realisation}: only {control_years:.0f} years of piControl')
                continue
            # Determine linear trend and intercept
            control_drift = xr.polyval(experiment_data.time, control_data_extract.polyfit('time', deg=1).polyfit_coefficients)
            # Remove drift
            detrended_experiment_data = experiment_data[variable] - control_drift
            ds_realisation = xr.Dataset({variable: detrended_experiment_data, 
                                         'control_years': control_years, 
                                         f'{variable}_control_mean':control_drift.isel(time=0).values})
        elif no_parent :
            ds_realisation = xr.Dataset({variable:experiment_data[variable]})
        ds_realisation.attrs = experiment_data.attrs 
        all_detrended_data.append(ds_realisation.assign_coords(realisation=realisation))
    ds_out = xr.concat(all_detrended_data, dim='realisation')
    if convert_time_to_datetime:
        start_month = ds_out.time.dt.strftime('%Y-%m').values[0]
        try:
            ds_out['time'] = pd.date_range(start_month, freq='MS', periods=ds_out.time.size)
        except Exception as e:
            print("Time is likely out of the datetime range, staying with cftime")
    return ds_out




def get_detrended_global_time_series(model, experiment, variable, realisation, **kwargs):

    # Load experiment data
    experiment_data = get_global_time_series(model, experiment, variable, realisation, use_cftime=True, **kwargs)
    # Get parent information and load control data
    parent_experiment_id = experiment_data.attrs['parent_experiment_id']
    print(parent_experiment_id, parent_variant_label)
    parent_variant_label = experiment_data.attrs['parent_variant_label']
    control_data = get_global_time_series(model, parent_experiment_id, variable, parent_variant_label, use_cftime=True, **kwargs)
    # Get branch time in parent time units
    branch_time_int = experiment_data.attrs['branch_time_in_parent']
    parents_time_units = experiment_data.attrs['parent_time_units']
    branch_time = cftime.num2date(branch_time_int, calendar=experiment_data.time.values[0].calendar, units = parents_time_units)
    # get piControl parallel to experiment
    control_data_extract = control_data.sel(time=slice(branch_time, None)).isel(time = slice(0, experiment_data.time.size))[variable]
    control_data_extract = control_data_extract.assign_coords(time=experiment_data.time.values[:control_data_extract.time.size])
    # Determine linear trend and intercept
    control_drift = xr.polyval(experiment_data.time, control_data_extract.polyfit('time', deg=1).polyfit_coefficients)
    # Remove drift
    detrended_experiment_data = experiment_data[variable] - control_drift
    ds_out = xr.Dataset(dict(control_extract = control_data_extract, control_drift=control_drift, detrended_data= detrended_experiment_data))
    ds_out.attrs = experiment_data.attrs 
    return ds_out


                            


def get_global_toa_energy_budget(model, experiment, no_parent=False, 
                           remove_if_control_less_than='max', warn_too_short_control=True, 
                           convert_time_to_datetime=True,
                           progress = True, add_control_mean=False, **kwargs):
    """
    Load global mean time series of tas, rsut, rlut, rsdt and eei for the given model and experiment.
    Time series are by default detrended by the control experiment.
    """
    ds = get_all_detrended_global_time_series_multivariable(model, experiment,
                                                            'tas','rlut','rsut','rsdt', no_parent=no_parent, 
                                                            remove_if_control_less_than=remove_if_control_less_than, 
                                                            warn_too_short_control=warn_too_short_control, 
                                                            progress = progress, add_control_mean=add_control_mean,
                                                            convert_time_to_datetime=convert_time_to_datetime,
                                                            **kwargs)
    ds['eei'] = ds.rsdt - ds.rsut - ds.rlut
    if add_control_mean:
        ds['eei_control_mean'] = ds.rsdt_control_mean - ds.rsut_control_mean - ds.rlut_control_mean
    return ds

def get_all_detrended_global_time_series_multivariable(model, experiment, *variables, no_parent=False, 
                                         remove_if_control_less_than='max', warn_too_short_control=True, 
                                         progress = True, add_control_mean=False,
                                         convert_time_to_datetime=True, **kwargs):
    list_variables_data = []
    if progress:
        iterable = tqdm(variables)
    else:
        iterable = variables
    for variable in iterable:
        data_variable = get_all_detrended_global_time_series(model, experiment, variable, 
                                                            no_parent=no_parent,remove_if_control_less_than=remove_if_control_less_than, 
                                                            warn_too_short_control=warn_too_short_control, 
                                                            convert_time_to_datetime=convert_time_to_datetime,
                                                            progress=False, **kwargs)
        if add_control_mean :
            data_variable = data_variable[[variable, f"{variable}_control_mean"]]
        else:
            data_variable = data_variable[[variable]]
        list_variables_data.append(data_variable)
    ds = xr.merge(list_variables_data)
    return ds