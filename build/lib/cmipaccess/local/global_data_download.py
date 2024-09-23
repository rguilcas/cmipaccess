from cmath import exp
from .. import esgf
from .config import GLOBAL_MEAN_DATA_DIR
from .cell_files import get_cell_data
from ..path_search import get_path_CMIP_data
import xarray as xr 
import warnings
from tqdm import tqdm
warnings.simplefilter("ignore", category=xr.SerializationWarning) 
import os
import glob


def download_single_timeseries(model, 
                               experiment, 
                               realisation, 
                               variable,
                               grid=None,
                               freq='mon',
                               source = 'spiritx',
                               esgf_fallback=True,
                               generation='CMIP6',
                               overwrite = False,
                               esgf_server=None,
                               **kwargs):
    """Downloads single global mean time series to local directory

    Args:
        model (_type_): _description_
        experiment (_type_): _description_
        realisation (_type_): _description_
        variable (_type_): _description_
        grid (_type_, optional): _description_. Defaults to None.
        freq (str, optional): _description_. Defaults to 'mon'.
        source (str, optional): _description_. Defaults to 'spiritx'.
        esgf_fallback (bool, optional): _description_. Defaults to True.
        generation (str, optional): _description_. Defaults to 'CMIP6'.
        overwrite (bool, optional): _description_. Defaults to False.
    """
    # See if file already exists
    path_out = f"{GLOBAL_MEAN_DATA_DIR}/{generation}/{model}/{experiment}/{realisation}"
    if os.path.exists(path_out):
        path_out_exists = True
        path_out_file = glob.glob(f"{path_out}/{variable}_*")
        if len(path_out_file)!=0 and not overwrite:
            print("File already exists. Add overwrite=True, to overwrite it")
            return
    else:
        path_out_exists = False
    # Find data file
    path_data = get_path_CMIP_data(model, 
                                   experiment, 
                                   realisation, 
                                   variable,
                                   grid=grid,
                                   freq=freq,
                                   source = source,
                                   esgf_fallback=esgf_fallback,
                                   esgf_server=esgf_server,
                                   generation=generation)
    if not path_out_exists : 
        os.makedirs(path_out)
    data_experiment = xr.open_mfdataset(path_data, **kwargs)
    # Find area file
    grid_label = data_experiment.grid_label
    table_id = data_experiment.table_id
    if table_id=='Amon':
        area_var = 'areacella'
    elif table_id=='Omon':
        area_var = 'areacello'

    area = get_cell_data(model, area_var, grid_label)[area_var].fillna(0)
    averaging_dims = area.dims
    # Compute global average
    data_global_mean = data_experiment[[variable]].weighted(area).mean(averaging_dims, keep_attrs=True)
    # Save data
    year_start, year_end = data_global_mean.time.dt.year.values[[0,-1]]
    out_name = f"{variable}_{table_id}_{model}_{experiment}_{realisation}_{grid_label}_{year_start:04.0f}-{year_end:04.0f}.nc"
    data_global_mean.to_netcdf(f"{path_out}/{out_name}")
    print(f'    --> File saved: {out_name}')
    return 

def download_multi_variables_timeseries(model, 
                                        experiment, 
                                        realisation, 
                                        *variables,
                                        grid=None,
                                        freq='mon',
                                        source = 'spiritx',
                                        esgf_fallback=True,
                                        esgf_server=None,
                                        generation='CMIP6',
                                        overwrite = False,
                                        **kwargs):
    """Downloads global mean time series for multiple variables to local directory

    Args:
        model (_type_): _description_
        experiment (_type_): _description_
        realisation (_type_): _description_
        grid (_type_, optional): _description_. Defaults to None.
        freq (str, optional): _description_. Defaults to 'mon'.
        source (str, optional): _description_. Defaults to 'spiritx'.
        esgf_fallback (bool, optional): _description_. Defaults to True.
        generation (str, optional): _description_. Defaults to 'CMIP6'.
        overwrite (bool, optional): _description_. Defaults to False.
    """
    for variable in variables:
        try:
            download_single_timeseries(model, 
                                    experiment, 
                                    realisation, 
                                    variable,
                                    grid=grid,
                                    freq=freq,
                                    source = source,
                                    esgf_fallback=esgf_fallback,
                                    generation=generation,
                                    overwrite = overwrite,
                                    esgf_server=esgf_server,
                                    **kwargs)
        except Exception as e:
            print(f"   !!FAIL !! {model} {experiment} {realisation} {variable} ")
            print(e)
            print('')

def download_all_realisations_one_model(model, 
                                        experiment, 
                                        *variables,
                                        grid=None,
                                        freq='mon',
                                        source = 'spiritx',
                                        esgf_fallback=True,
                                        generation='CMIP6',
                                        overwrite = False,
                                        esgf_server=None,
                                        **kwargs):
    """Download timeseries for all available realisations for multiple variables

    Args:
        model (_type_): _description_
        experiment (_type_): _description_
        grid (_type_, optional): _description_. Defaults to None.
        freq (str, optional): _description_. Defaults to 'mon'.
        source (str, optional): _description_. Defaults to 'spiritx'.
        esgf_fallback (bool, optional): _description_. Defaults to True.
        generation (str, optional): _description_. Defaults to 'CMIP6'.
        overwrite (bool, optional): _description_. Defaults to False.
    """
    realisations = esgf.find_realisations_experiment(model, 
                                                     experiment,
                                                     variable='tas',
                                                     table='Amon')
    print(f"  {model} | {experiment} | Downloading {len(realisations)*len(variables):.0f} file(s) ...")
    for realisation in realisations: 
        download_multi_variables_timeseries(model, 
                                            experiment, 
                                            realisation, 
                                            *variables,
                                            grid=grid,
                                            freq=freq,
                                            source = source,
                                            esgf_fallback=esgf_fallback,
                                            generation=generation,
                                            overwrite = overwrite,
                                            esgf_server=esgf_server,
                                            **kwargs)


def download_all_realisations_all_models(experiment, 
                                         *variables,
                                         grid=None,
                                         freq='mon',
                                         source = 'spiritx',
                                         esgf_fallback=True,
                                         generation='CMIP6',
                                         overwrite = False,
                                         esgf_server=None,
                                         **kwargs):
    """Downloads global time series for all models and all experiments available for a given experiment

    Args:
        experiment (_type_): _description_
        grid (_type_, optional): _description_. Defaults to None.
        freq (str, optional): _description_. Defaults to 'mon'.
        source (str, optional): _description_. Defaults to 'spiritx'.
        esgf_fallback (bool, optional): _description_. Defaults to True.
        generation (str, optional): _description_. Defaults to 'CMIP6'.
        overwrite (bool, optional): _description_. Defaults to False.
        esgf_server (str, optional): specicy the esgf erver to find the data
    """
    
    models = esgf.find_models_experiment(experiment, 
                                         variable='tas',
                                         table='Amon')
    print(f"Downloading data from {len(models):.0f} models")
    for model in models: 
        download_all_realisations_one_model(model, 
                                            experiment, 
                                            *variables,
                                            grid=grid,
                                            freq=freq,
                                            source = source,
                                            esgf_fallback=esgf_fallback,
                                            generation=generation,
                                            overwrite = overwrite,
                                            esgf_server=esgf_server,
                                            **kwargs)
