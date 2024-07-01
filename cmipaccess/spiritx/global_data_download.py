from cmath import exp
import cmipaccess.esgf as esgf
import cmipaccess.spiritx as spiritx
import cmipaccess as cmip
from .constants import GLOBAL_MEAN_DATA_DIR
import xarray as xr 
import warnings
from tqdm import tqdm
warnings.simplefilter("ignore", category=xr.SerializationWarning) 
import os
import glob
from cmipaccess.tools import sort_realisations


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
                               area_path = None
                               **kwargs):
    # See if file already exists
    path_out = f"{GLOBAL_MEAN_DATA_DIR}/Models/{generation}/{model}/{experiment}/{realisation}"
    if os.path.exists(path_out):
        path_out_exists = True
        path_out_file = glob.glob(f"{path_out}/{variable}_*")
        if len(path_out_file)!=0 and not overwrite:
            print("File already exists. Add overwrite=True, to overwrite it")
            return
    else:
        path_out_exists = False
    # Find data file
    path_data = cmip.get_path_CMIP_data(model, 
                                        experiment, 
                                        realisation, 
                                        variable,
                                        grid=grid,
                                        freq=freq,
                                        source = source,
                                        esgf_fallback=esgf_fallback,
                                        generation=generation)
    if not path_out_exists : 
        os.makedirs(path_out)
    data_experiment = xr.open_mfdataset(path_data, **kwargs)
    # Find area file
    grid_label = data_experiment.grid_label
    table_id = data_experiment.table_id
    if table_id=='Amon':
        table_grid = 'fx'
        area_var = 'areacella'
    elif table_id=='Omon':
        table_grid='Ofx'
        area_var = 'areacello'
    if area_path is None:
        path_list_to_area = glob.glob(f"/bdd/CMIP6/CMIP/*/{model}/{experiment}/*/{table_grid}/{area_var}/{grid_label}/latest/*")
        if len(path_list_to_area) == 0:
            path_list_to_area = glob.glob(f"/bdd/CMIP6/CMIP/*/{model}/piControl/*/{table_grid}/{area_var}/{grid_label}/latest/*")
            if len(path_list_to_area) == 0:
                path_list_to_area = glob.glob(f"/bdd/CMIP6/CMIP/*/{model}/*/*/{table_grid}/{area_var}/{grid_label}/latest/*")
                if len(path_list_to_area) == 0:
                    path_list_to_area = glob.glob(f"/bdd/CMIP6/*/*/{model}/*/*/{table_grid}/{area_var}/{grid_label}/latest/*")
        area_path = path_list_to_area[0]
    area = xr.open_dataset(area_path)[area_var].fillna(0)
    averaging_dims = area.dims
    # Compute global average
    data_global_mean = data_experiment[[variable]].weighted(area).mean(averaging_dims, keep_attrs=True)
    # Save data
    year_start, year_end = data_global_mean.time.dt.year.values[[0,-1]]
    out_name = f"{variable}_{table_id}_{model}_{experiment}_{realisation}_{grid_label}_{year_start}_{year_end}.nc"
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
                                        generation='CMIP6',
                                        overwrite = False,
                                        **kwargs):
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
                                        **kwargs):
    
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
                                            **kwargs)


def download_all_realisations_all_models(experiment, 
                                         *variables,
                                         grid=None,
                                         freq='mon',
                                         source = 'spiritx',
                                         esgf_fallback=True,
                                         generation='CMIP6',
                                         overwrite = False,
                                         **kwargs):
    
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
                                            **kwargs)
