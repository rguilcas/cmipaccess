from xmip.preprocessing import combined_preprocessing
import xarray as xr
from .CMIP_path_search import get_path_CMIP6_data



def get_CMIP6_data(model, 
                   experiment, 
                   realisation, 
                   variable,
                   grid=None,
                   freq='mon',
                   source = 'spirit',
                   esgf_fallback=True, 
                   xr_kwargs = dict()):
    """
    Loads gridded CMIP6 data from spirit or esgf using xmip combined_preprocessing routine

    grid : default is 'gn' native grid
    freq : can be 'mon', 'day', '3h', ... See CMIP documentation
    source : can be 'spirit' for local access or 'esgf' for remote access
    esgf_fallback : if source is 'spirit' but the dataset is not found, tries to get remote data from esgf
    xr_kwargs : keyword args passed to xarray open_mfdataset function that opens files (chunks, cftime, ...) 
    """
    paths = get_path_CMIP6_data(model, 
                                experiment, 
                                realisation, 
                                variable,
                                grid=None,
                                freq='mon',
                                source = 'spirit',
                                esgf_fallback=True)
    dataset = xr.open_mfdataset(paths, **xr_kwargs)
    return combined_preprocessing(dataset)