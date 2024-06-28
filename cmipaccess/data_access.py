import xarray as xr
from .path_search import get_path_CMIP_data



def get_CMIP6_data(model, 
                   experiment, 
                   realisation, 
                   variable,
                   grid=None,
                   freq='mon',
                   source = 'spiritx',
                   esgf_fallback=True, 
                   **xr_kwargs):
    """
    Loads gridded CMIP6 data from spirit or esgf

    grid : default is 'gn' native grid
    freq : can be 'mon', 'day', '3h', ... See CMIP documentation
    source : can be 'spiritx' for local access or 'esgf' for remote access
    esgf_fallback : if source is 'spirit' but the dataset is not found, tries to get remote data from esgf
    xr_kwargs : keyword args passed to xarray open_mfdataset function that opens files (chunks, cftime, ...) 
    """
    paths = get_path_CMIP_data(model, 
                               experiment, 
                               realisation, 
                               variable,
                               grid=grid,
                               freq=freq,
                               source = source,
                               esgf_fallback=esgf_fallback,
                               generation='CMIP6')
    dataset = xr.open_mfdataset(paths, **xr_kwargs)
    return dataset