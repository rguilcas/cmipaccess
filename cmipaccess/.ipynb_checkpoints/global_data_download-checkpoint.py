from cmath import exp
from .get_paths import get_global_mean_EMC2_path, get_remote_path
from .constants import EMC2_DATA_DIR
import xarray as xr 
import warnings
from tqdm import tqdm
warnings.simplefilter("ignore", category=xr.SerializationWarning) 
import os
import numpy as np
import glob
from .finders import find_realisations_experiment, find_models_experiment
from .tools import sort_realisations
from .DetrendedRealisation import DetrendedRealisation


def download_full_experiment_all_model(experiment, *variables, 
                                       no_parent=False, table = None, 
                                       progress = None):
    """
    progress can be None, realisation, variable, both
    """
    models = find_models_experiment(experiment)
    for model in models[1:]:
        print(model)
        realisations = find_realisations_experiment(model, experiment)
        fails = []
        if progress in ['variable','both']:
            variables = tqdm(variables)
        if progress in ['realisation','both']:
            realisations = tqdm(realisations)
        
        for realisation in realisations:
            for variable in variables:
                print(variable)
                real = DetrendedRealisation(model, experiment, realisation, variable)
                try:
                    real.save_global_mean_remote_data()
                except:
                    fails.append(f"{model} {realisation} {variable} global mean data")
                if not no_parent:
                    try:
                        real.save_global_mean_detrended_run()
                    except:
                        fails.append(f"{model} {realisation} {variable} global mean detrended data")
        print(f"--------- {len(fails)}/{len(variables)*len(realisations)} failed processes  --------")
        for k in fails:
            print('    '+k)

def download_full_experiment_one_model(model, experiment, *variables, 
                                       no_parent=False, table = None, 
                                       progress = None):
    """
    progress can be None, realisation, variable, both
    """
    realisations = find_realisations_experiment(model, experiment)
    fails = []
    if progress in ['variable','both']:
        variables = tqdm(variables)
    if progress in ['realisation','both']:
        realisations = tqdm(realisations)
    
    for realisation in realisations:
        for variable in variables:
            real = DetrendedRealisation(model, experiment, realisation, variable)
            try:
                real.save_global_mean_remote_data()
            except:
                fails.append(f"{model} {realisation} {variable} global mean data")
            if not no_parent:
                try:
                    real.save_global_mean_detrended_run()
                except:
                    fails.append(f"{model} {realisation} {variable} global mean detrended data")
    print(f"--------- {len(fails)}/{len(variables)*len(realisations)} failed processes  --------")
    for k in fails:
        print('    '+k)
    
    # print(realisations)


# def download_full_experiment_global_mean_data(experiment,
#                                               *variables,
#                                               table='Amon',
#                                               grid=None, 
#                                               source='climserv',
#                                               esgf_fallback=True,
#                                               override=False,
#                                               force_grid_weights=False):
#     models = find_models_experiment(experiment)
#     n_models = len(models)
#     print(f"-\| {n_models} MODELS FOUND FOR {experiment} |/-")
#     for k, model in enumerate(models):
#         print(f'\n   {k+1}/{n_models} DOWNLOADING {model.upper()}...')
#         download_multiple_remote_global_mean_data(model, 
#                                                   experiment,
#                                                  *variables,
#                                                   table=table,
#                                                   grid=grid, 
#                                                   source=source,
#                                                   esgf_fallback=esgf_fallback,
#                                                   override=override,
#                                                   force_grid_weights=force_grid_weights)    

# def download_multiple_remote_global_mean_data(model, 
#                                               experiment,
#                                               *variables,
#                                               table='Amon',
#                                               grid=None, 
#                                               source='climserv',
#                                               esgf_fallback=True,
#                                               override=False,
#                                               force_grid_weights=False):
#     realisations = find_relisations_experiment(experiment, model)
#     n_real = len(realisations)
#     print(f'{n_real} realisations on ESGF')
#     for k,realisation in enumerate(realisations):
#         print(f'{k+1}/{n_real}: {realisation} downloading ...')
#         for variable in variables:
#             try:
#                 _ = download_remote_global_mean_data(model, 
#                                                         experiment,
#                                                         realisation,
#                                                         variable,
#                                                         table=table,
#                                                         grid=grid,
#                                                         source=source,
#                                                         esgf_fallback=esgf_fallback,
#                                                         override=override,
#                                                         force_grid_weights=force_grid_weights)
#             except Exception as e:
#                 print(e)
    

# def download_remote_global_mean_data(model,
#                                     experiment,
#                                     realisation,
#                                     variable,
#                                     table='Amon',grid=None,
#                                     source='climserv',esgf_fallback=True,
#                                     xr_kwargs = dict(),
#                                     download=True,
#                                     override=False,
#                                     force_grid_weights=False):
#     print(model, realisation, experiment, variable)
#     local_path = f'{get_local_model_path(model)}/{experiment}/{realisation}'
#     if not os.path.exists(local_path):
#         os.makedirs(local_path)
#     if len(glob.glob(f"{local_path}/{variable}_*")) == 0 or override:
#         remote_data, remote_paths = get_remote_data(model, 
#                                                     experiment, 
#                                                     realisation, 
#                                                     variable,
#                                                     table=table,grid=grid,
#                                                     source = source,
#                                                     esgf_fallback=esgf_fallback,
#                                                     xr_kwargs = xr_kwargs)
#         if force_grid_weights:
#             weights = np.cos(np.deg2rad(remote_data.lat))
#             global_mean_data = remote_data[variable].weighted(weights).mean(['lon','lat'], keep_attrs=True).to_dataset()
#         else:
#             weights = get_area(model, table=table)
#             global_mean_data = remote_data[variable].weighted(weights).mean(weights.dims, keep_attrs=True).to_dataset()
#         global_mean_data.attrs = remote_data.attrs


#         if download:
#             ds_name = '_'.join(remote_paths[0].split('/')[-1].split('_')[:-1] + \
#                                             [f"{global_mean_data.time.dt.year.values[0]:04d}-{global_mean_data.time.dt.year.values[-1]:04d}.nc"])
#             if ds_name not in os.listdir(local_path) or override:
#                 global_mean_data.to_netcdf(f"{local_path}/{ds_name}")
#                 global_mean_data.close()


#         return global_mean_data

# def get_remote_data(model, 
#                     experiment, 
#                     realisation, 
#                     variable,
#                     table='Amon',grid=None,
#                     source = 'climserv',
#                     esgf_fallback=True,
#                     xr_kwargs = dict()):

#     remote_paths = get_remote_path(model, 
#                                    experiment, 
#                                    realisation, 
#                                    variable,
#                                    table=table,grid=grid,
#                                    source = source,
#                                    esgf_fallback=esgf_fallback)
#     if '/bdd' not in remote_paths[0]:
#         ds = xr.open_mfdataset(remote_paths,engine='pydap', **xr_kwargs)
#         return ds, remote_paths
#     else:
#         ds = xr.open_mfdataset(remote_paths, **xr_kwargs)
#     return ds, remote_paths

# def get_local_model_path(model):
#     return f"{EMC2_DATA_DIR}/Models/CMIP6/{model}"

# def get_area(model, table='Amon', grid=None):
#     if table == 'Amon':
#         area_variable = 'areacella'
#         area_table = "fx"
#     elif table == 'Omon':
#         area_variable = 'areacello'
#         area_table = "Ofx"
#     local_model_path = get_local_model_path(model)
#     if grid is None:
#         area_local_name = f"{model}_{area_variable}_*.nc"
#         area_path = glob.glob(f"{local_model_path}/{area_local_name}")
#     else:
#         area_local_name = f"{model}_{area_variable}_{grid}.nc"
#         area_path = glob.glob(f"{local_model_path}/{area_local_name}")
#     if len(area_path) == 0:
#         print('Downloading the cell area file')
#         download_area(model, area_variable, area_table, grid=grid)
#     if grid is None:
#         area_local_name = f"{model}_{area_variable}*.nc"
#         area_path = glob.glob(f"{local_model_path}/{area_local_name}")
#     else:
#         area_local_name = f"{model}_{area_variable}_{grid}.nc"
#         area_path = glob.glob(f"{local_model_path}/{area_local_name}")
#     with xr.open_dataset(area_path[0])[area_variable] as area_data:
#         area = area_data.copy()
#         return area


# def download_area(model,area_variable,area_table, experiment='piControl',grid=None):
#     """
#     Attention trouve le path sans préciser de réalisation
#     """
#     finder = find_relisations_experiment('piControl',model,
#                                           variable=area_variable,
#                                           table=area_table)
#     area_path = get_remote_path(model, experiment,finder[0], area_variable, table=area_table)[0]
#     area_label =  area_path.split('/')[-3]
#     area_name = f'{model}_{area_variable}_{area_label}.nc'
#     local_model_path = get_local_model_path(model)

#     with xr.open_dataset(area_path) as area:
#         area.to_netcdf(f"{local_model_path}/{area_name}")
