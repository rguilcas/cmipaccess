import xarray as xr 
import glob
from tqdm import tqdm
import numpy as np
from cmipaccess.tools import sort_realisations

EMC2_DATA_DIR = '/projets/EMC2/data'
    

def load_toa_energy_budget(model, experiment, 
                           anom = True, progress = True, yearly = False, control_mean = True, no_parent=False):
    ds = load_multirealisation_multi_variable(model, experiment, 
                                   'tas','rlut','rsdt','rsut', 
                                   anom=anom, progress = progress, yearly = yearly,control_mean = control_mean, no_parent=no_parent)
    ds['eei'] = ds.rsdt - ds.rsut - ds.rlut
    if not no_parent:
        ds['eei_control_mean'] = ds.rsdt_control_mean - ds.rsut_control_mean - ds.rlut_control_mean
        ds['eei'] = ds.eei
    return ds
                            
def load_multirealisation_multi_variable(model, experiment, *variables, 
                                         anom=True, progress = True, yearly = False,control_mean = True,remove_when_control_shorter_than = None,
                                         no_parent=False):
    list_variables_data = []
    if progress:
        iterable = tqdm(variables)
    else:
        iterable = variables
    for variable in iterable:
        list_variables_data.append(load_multirealisation_single_variable(model, experiment, variable, 
                                                                         anom=anom, yearly = yearly, 
                                                                         control_mean = control_mean,
                                                                         remove_when_control_shorter_than = remove_when_control_shorter_than,
                                                                         no_parent=no_parent))
    ds = xr.merge(list_variables_data)
    return ds

def load_multirealisation_single_variable(model, experiment, variable, 
                                          anom=True, control_mean = True, yearly = False, 
                                          remove_when_control_shorter_than = None,
                                          no_parent=False):
    if no_parent:
        variable_name = variable
    else:
        variable_name = f"{variable}-depiC"
    files = glob.glob(f"{EMC2_DATA_DIR}/Models/*/{model}/{experiment}/*/{variable_name}_*")
    realisations = [file.split('/')[-2] for file in files]
    
    def preprocess(ds):
        if "realisation" in ds.dims:
            ds = ds.mean('realisation')
        if not no_parent:
            control_mean_value = ds[variable].attrs['control_mean_value']
            if control_mean:
                ds[f"{variable}_control_mean"] = control_mean_value
            if anom:
                ds[variable] -= control_mean_value
            if remove_when_control_shorter_than is not None:
                if ds[variable].control_duration_years < remove_when_control_shorter_than:
                   return np.nan*ds
        return ds
    ds = xr.open_mfdataset(files, concat_dim='realisation', combine='nested', preprocess=preprocess).load()
    ds['realisation'] = realisations
    if yearly:
        ds = ds.resample(time='YS').mean()
    return ds#.dropna('realisation')
