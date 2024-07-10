from . import GLOBAL_MEAN_DATA_DIR
import os
import xarray as xr
import glob 
from ..esgf.path_cell_search import get_path_cell
from ..spiritx.path_search import get_path_area

def download_cell_file(model, 
                       variable,
                       grid, 
                       generation='CMIP6',
                       overwrite=False,
                       source = 'esgf',
                       **kwargs):
    """Download the file for cell area size

    Args:
        model (str): _description_
        variable (str): _description_
        grid (str): _description_
        generation (str, optional): Generation of the models. For now only works with CMIP6 data. Defaults to 'CMIP6'.
        overwrite (bool, optional): if True overwrites an existing file. Defaults to False.
    """
    path_out = f"{GLOBAL_MEAN_DATA_DIR}/{generation}/{model}/grids"
    if os.path.exists(path_out):
        path_out_exists = True
        path_out_file = glob.glob(f"{path_out}/{variable}_{model}_{grid}.nc")
        if len(path_out_file)!=0 and not overwrite:
            print("File already exists. Add overwrite=True, to overwrite it")
            return
    else:
        path_out_exists = False
   
    try:
        path_data = get_path_area(model, variable, grid)
        data_area = xr.open_dataset(path_data, **kwargs)
    except:
        list_path_data = get_path_cell(model, 
                                      variable,
                                      grid)
        if not path_out_exists : 
            os.makedirs(path_out)
        for path_data in list_path_data:
            try:
                data_area = xr.open_dataset(path_data, **kwargs)
                break
            except:
                print('Area file failed to save. Trying next one...')
    out_name = f"{variable}_{model}_{grid}.nc"
    data_area.to_netcdf(f'{path_out}/{out_name}')
    print(f'    --> File saved: {out_name}')

    

def get_cell_data(model, variable, grid, generation='CMIP6',
                  **kwargs):
    """Opens a dataset containing cell area data for a given model and grid

    Args:
        model (_type_): _description_
        variable (_type_): _description_
        grid (_type_): _description_
        generation (str, optional): _description_. Defaults to 'CMIP6'.

    Returns:
        _type_: _description_
    """
    file_path = f"{GLOBAL_MEAN_DATA_DIR}/{generation}/{model}/grids/{variable}_{model}_{grid}.nc"
    if os.path.exists(file_path):
        return xr.open_dataset(file_path)
    else:
        print('Area file not avaiable, trying to download it ...')
        download_cell_file(model, variable, grid, generation=generation, **kwargs)
        return xr.open_dataset(file_path)
