import numpy as np
import os
import glob



def get_path_area(model, 
                  variable,
                  grid):
    """Returns path to area file in spiritx

    Args:
        model (str): climate model
        variable (str): variable of the cell data : can be areacello or areacella
        grid (str): grid id


    Returns:
        str: path to the grid on spiritx if found
    """
    if variable == 'areacello':
        table='Ofx'
    elif variable == 'areacella':
        table='fx'
    else:
        raise ValueError('Variable needs to be areacello or areacella')
    list_area = glob.glob(f'/bdd/CMIP6/CMIP/*/{model}/piControl/*/{table}/{variable}/{grid}/latest')
    if len(list_area) != 0:
        return list_area[0]
    list_area = glob.glob(f'/bdd/CMIP6/CMIP/*/{model}/historical/*/{table}/{variable}/{grid}/latest')
    if len(list_area) != 0:
        return list_area[0]
    list_area = glob.glob(f'/bdd/CMIP6/CMIP/*/{model}/*/*/{table}/{variable}/{grid}/latest')
    if len(list_area) != 0:
        return list_area[0]
    list_area = glob.glob(f'/bdd/*/CMIP/*/{model}/piControl/*/{table}/{variable}/{grid}/latest')
    if len(list_area) != 0:
        return list_area[0]
    raise ValueError('Area file not found on spiritx')


def get_path_CMIP_data(model, 
                       experiment, 
                       realisation, 
                       variable,
                       grid=None,
                       generation=None,
                       freq='mon'):
    """
    Returns path to access gridded CMIP data from either CMIP5 or CMIP6

    grid : default is 'gn' native grid, only for CMIP6
    freq : can be 'mon', 'day', '3h' or else, see CMIP documentation
    source : can be 'spirit' for local access or 'esgf' for remote access
    esgf_fallback : if source is 'spirit' but the dataset is not found, tries to get remote data from esgf
    generation : specify the generation wanted : either 'CMIP5' or 'CMIP6'. If None, it tries CMIP6 first then CMIP5 which can be slower. 
    """
    if generation == 'CMIP6':
        return get_path_CMIP6_data(model, 
                                   experiment, 
                                   realisation, 
                                   variable,
                                   grid=grid,
                                   freq=freq,)
    elif generation == 'CMIP5':
        return get_path_CMIP6_data(model, 
                                   experiment, 
                                   realisation, 
                                   variable,
                                   freq=freq,)
    elif generation is None:
        try:
            paths = get_path_CMIP6_data(model, 
                                        experiment, 
                                        realisation, 
                                        variable,
                                        grid=grid,
                                        freq=freq,)
            return paths
        except ValueError:
            pass 
        try:
            paths = get_path_CMIP5_data(model, 
                                        experiment, 
                                        realisation, 
                                        variable,
                                        freq=freq,)
            return paths
        except ValueError:
            raise ValueError('Data not found')
    else:
        raise ValueError("Generation can only be None, 'CMIP5' or 'CMIP6'")


#########################
#        CMIP6          #
#########################


def get_path_CMIP6_data(model, 
                        experiment, 
                        realisation, 
                        variable, 
                        freq='mon',
                        grid=None):
    """
    Returns the local path to the corresponding CMIP6 datasets if the data exist on spirit.

    Realisation can be "first" in which case the first r1iXpXfX is selected if available, if not another realisation is chosen.
    """
    # Checks if model data is on spirit
    path_list_to_model = glob.glob(f"/bdd/CMIP6/CMIP/*/{model}")
    if len(path_list_to_model) == 0:
        error_message = f"\nThere is no data for model '{model}' on Spiritx\n"  #Check available models?
        raise ValueError(error_message)
    center = path_list_to_model[0].split('/')[-2]

    # Checks if model-experiment data is on spirit
    path_list_to_experiment = glob.glob(f"/bdd/CMIP6/*/{center}/{model}/{experiment}")
    if len(path_list_to_experiment) == 0:
        error_message = f"\nThere is no '{experiment}' data for model '{model}' on Spiritx\n"  #Check available models?
        raise ValueError(error_message)
    path_to_experiment = path_list_to_experiment[0]

    # Checks if model-experiment-realisation data is on spirit
    realisations_available = [real for real in os.listdir(path_to_experiment) if not  real.startswith('.')]
    if realisation == 'first':
        # find r1i.p.f. realisation
        r1_list = np.array(realisations_available)[np.array(['r1i' in real for real in realisations_available])]
        if len(r1_list) == 0:
            realisation = realisations_available[0]
        else:
            realisation = r1_list[0]
    else:
        if realisation not in realisations_available:
            error_message = f"\nThere is no realisation '{realisation}' for '{experiment}' for model '{model}'on Spiritx\n" + \
                            f"Available realisation for experiment '{experiment}' and model '{model}' are:\n     " + print_list(realisations_available)
            raise ValueError(error_message)

    # Checks if model-experiment-realisation-variable data is on spirit
    path_list_to_variable = glob.glob(f"{path_to_experiment}/{realisation}/*/{variable}")
    if len(path_list_to_variable) == 0:
        error_message = f"\nThere is no variable '{variable}' for this model-experiment-realisation combo on Spiritx\n"  #Check available models?
        raise ValueError(error_message)
    path_to_variable = [path for path in path_list_to_variable if freq in path][0]

    # Select appropriate grid. Tries 'gn' if grid is None, else, select the first one available
    grids = os.listdir(f"{path_to_variable}/")
    
    if grid is None:
        if 'gn' in grids:
            grid = 'gn'
        else:
            grid = grids[0]
    if grid not in grids : 
        error_message = f"\nGrid '{grid}' not available. Available grids are \n     " +print_list(grids) 
        raise ValueError(error_message)
    # Select data to specific frequency only
    pre_table_paths = glob.glob(f"{path_to_variable}/{grid}/latest/*")
    final_paths = [path for path in pre_table_paths if freq in path.split('/')[8]]
    if len(final_paths) == 0:
        error_message = f"\nFrequency not available" 
        raise ValueError(error_message)
    return final_paths

#########################
#        CMIP5          #
#########################


def get_path_CMIP5_data(model, 
                        experiment, 
                        realisation, 
                        variable, 
                        freq='mon'):
    """
    Returns the local path to the corresponding CMIP5 datasets if the data exist on spirit.

    Realisation can be "first" in which case the first r1iXpXfX is selected if available, if not another realisation is chosen.
    """
    # Checks if model data is on spirit
    path_list_to_model = glob.glob(f"/bdd/CMIP5/output/*/{model}")
    if len(path_list_to_model) == 0:
        error_message = f"\nThere is no data for model '{model}' on Spiritx\n"  #Check available models?
        raise ValueError(error_message)
    center = path_list_to_model[0].split('/')[-2]
    # Checks if model-experiment data is on spirit
    path_list_to_experiment = glob.glob(f"/bdd/CMIP5/output/{center}/{model}/{experiment}")
    if len(path_list_to_experiment) == 0:
        error_message = f"\nThere is no '{experiment}' data for model '{model}' on Spiritx\n"  #Check available models?
        raise ValueError(error_message)
    path_to_experiment = path_list_to_experiment[0]
    
    # Checks if model-experiment-fres data is on spirit
    path_list_to_freq = glob.glob(f"{path_to_experiment}/{freq}")
    if len(path_list_to_freq) == 0:
        error_message = f"\nFrequency '{freq}' is not available\n"  #Check available freq?
        raise ValueError(error_message)
    path_to_freq = path_list_to_freq[0]
    # Checks if model-experiment-realisation data is on spirit
    path_list_to_real = glob.glob(f"{path_to_freq}/*/*/*")
    realisations_available = list(set([real.split('/')[-1] for real in path_list_to_real ]))
    if realisation == 'first':
        # find r1i.p.f. realisation
        r1_list = np.array(realisations_available)[np.array(['r1i' in real for real in realisations_available])]
        if len(r1_list) == 0:
            realisation = realisations_available[0]
        else:
            realisation = r1_list[0]
    else:
        if realisation not in realisations_available:
            error_message = f"\nThere is no realisation '{realisation}' for '{experiment}' for model '{model}'on Spiritx\n" + \
                            f"Available realisation for experiment '{experiment}' and model '{model}' are:\n     " + print_list(realisations_available)
            raise ValueError(error_message)

    # Checks if model-experiment-realisation-variable data is on spirit
    path_list_to_variable = glob.glob(f"{path_to_freq}/*/*/{realisation}/latest/{variable}")
    if len(path_list_to_variable) == 0:
        error_message = f"\nThere is no variable '{variable}' for this model-experiment-realisation combo on Spiritx\n"  #Check available models?
        raise ValueError(error_message)
    path_to_variable = [path for path in path_list_to_variable if freq in path][0]
    final_paths = glob.glob(f"{path_to_variable}/*")
    if len(final_paths) == 0:
        error_message = f"\nThe directory exists but data are missing" 
        raise ValueError(error_message)
    return final_paths


def print_list(model_list):
    return ('\n     '.join([f'{model:<30}' for model in sorted(model_list) if '.nc' not in model]))

