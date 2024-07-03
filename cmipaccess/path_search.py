from . import spiritx
from . import esgf


def get_path_CMIP_data(model, 
                       experiment, 
                       realisation, 
                       variable,
                       grid=None,
                       freq='mon',
                       source = 'spiritx',
                       esgf_fallback=True,
                       generation=None):
    """
    Returns path to access gridded CMIP data from either CMIP5 or CMIP6

    grid : default is 'gn' native grid, only for CMIP6
    freq : can be 'mon', 'day', '3h' or else, see CMIP documentation
    source : can be 'spiritx' for local access or 'esgf' for remote access
    esgf_fallback : if source is 'spiritx' but the dataset is not found, tries to get remote data from esgf
    generation : specify the generation wanted : either 'CMIP5' or 'CMIP6'. If None, it tries CMIP6 first then CMIP5 which can be slower. 
    """
    if source == 'spiritx':
        try:
            return spiritx.get_path_CMIP_data(model, 
                                    experiment, 
                                    realisation, 
                                    variable,
                                    grid=grid,
                                    freq=freq,
                                    generation=generation)
        except:
            if esgf_fallback:
                return esgf.get_path_CMIP_data(model, 
                                   experiment, 
                                   realisation, 
                                   variable,
                                   freq=freq,
                                   generation=generation,
                                   )
    elif source == 'esgf':
        return esgf.get_path_CMIP_data(model, 
                                   experiment, 
                                   realisation, 
                                   variable,
                                   freq=freq,
                                   generation=generation,
                                   )
    else:
        raise ValueError("Source can only be spiritx or esgf")
    
def print_list(model_list):
    return ('\n     '.join([f'{model:<30}' for model in sorted(model_list) if '.nc' not in model]))

