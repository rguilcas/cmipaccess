from .esgf_data_access import esgf_search
import numpy as np
import os
import glob

def get_path_CMIP_data(model, 
                       experiment, 
                       realisation, 
                       variable,
                       grid=None,
                       freq='mon',
                       source = 'spirit',
                       esgf_fallback=True,
                       generation=None):
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
                                   freq=freq,
                                   source = source,
                                   esgf_fallback=esgf_fallback)
    elif generation == 'CMIP5':
        return get_path_CMIP6_data(model, 
                                   experiment, 
                                   realisation, 
                                   variable,
                                   freq=freq,
                                   source = source,
                                   esgf_fallback=esgf_fallback)
    elif generation is None:
        try:
            paths = get_path_CMIP6_data(model, 
                                        experiment, 
                                        realisation, 
                                        variable,
                                        grid=grid,
                                        freq=freq,
                                        source = source,
                                        esgf_fallback=esgf_fallback)
            return paths
        except ValueError:
            pass 
        try:
            paths = get_path_CMIP5_data(model, 
                                        experiment, 
                                        realisation, 
                                        variable,
                                        freq=freq,
                                        source = source,
                                        esgf_fallback=esgf_fallback)
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
                        grid=None,
                        freq='mon',
                        source = 'spirit',
                        esgf_fallback=True):
    """
    Return path to corresponding model-experiment-realisation-variable gridded data. 
    
    grid : None
        if grid is not used, default is 'gn'
    
    freq : 'mon' or 'day' or 'fx' for fx variables
        frequency of simulation result file. Default is 'mon'

    source : 'spirit' or 'esgf'
        default returns local path to access data from climserv but can return remote path from esgf
    
    esgf_fallback : True or False
        if True and source is 'spirit', will get the path from esgf if data does not exist on spirit.
    """
    if source == 'spirit':
        try:
            paths = get_path_CMIP6_data_spirit(model, 
                                               experiment,
                                               realisation, 
                                               variable, 
                                               freq=freq,
                                               grid=grid)
        except ValueError:
            if esgf_fallback:
                paths = get_path_CMIP6_data_esgf(model, 
                                                 experiment,
                                                 realisation, 
                                                 variable,
                                                 freq=freq, 
                                                 grid=grid)
            else:
                raise ValueError('No data on ESGF')
    elif source == 'esgf':
        paths = get_path_CMIP6_data_esgf(model,     
                                         experiment,
                                         realisation, 
                                         variable,
                                         freq=freq, 
                                         grid=grid)
    else:
        raise ValueError('Source must be spirit or esgf')
    return paths

def get_path_CMIP6_data_spirit(model, 
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
        error_message = f"\nThere is no data for model '{model}' on Climserv\n"  #Check available models?
        raise ValueError(error_message)
    center = path_list_to_model[0].split('/')[-2]

    # Checks if model-experiment data is on spirit
    path_list_to_experiment = glob.glob(f"/bdd/CMIP6/*/{center}/{model}/{experiment}")
    if len(path_list_to_experiment) == 0:
        error_message = f"\nThere is no '{experiment}' data for model '{model}' on Climserv\n"  #Check available models?
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
            error_message = f"\nThere is no realisation '{realisation}' for '{experiment}' for model '{model}'on Climserv\n" + \
                            f"Available realisation for experiment '{experiment}' and model '{model}' are:\n     " + print_list(realisations_available)
            raise ValueError(error_message)

    # Checks if model-experiment-realisation-variable data is on spirit
    path_list_to_variable = glob.glob(f"{path_to_experiment}/{realisation}/*/{variable}")
    if len(path_list_to_variable) == 0:
        error_message = f"\nThere is no variable '{variable}' for this model-experiment-realisation combo on Climserv\n"  #Check available models?
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

def get_path_CMIP6_data_esgf(model, 
                             experiment, 
                             realisation, 
                             variable,
                             freq='mon', 
                             grid=None):        
        """
        Returns the remote ESGF path to the corresponding datasets they exist on ESGF.
        """
         # Checks model availability
        all_paths = esgf_search(variable_id=variable,
                                experiment_id=experiment, 
                                member_id=realisation,
                                frequency=freq,
                                source_id=model)
        if len(all_paths) == 0:
            raise ValueError("No such data exist on ESGF")
        # select grid
        grids = list(set([path.split('/')[14] for path in all_paths]))
        if grid is None:
            if 'gn' in grids:
                grid = 'gn'
            else:
                grid = grids[0]
        all_paths = [path for path in all_paths if path.split('/')[14] == grid]
        # find longest source available
        sources = [path.split('/')[2] for path in all_paths]
        list_durations = []
        for source in sources:
            dates_source = [path.split('_')[-1][:-3].split('-') for path in all_paths if source in path]
            duration = sum([int(date[1][:-2]) - int(date[0][:-2]) for date in dates_source])
            list_durations.append(duration)
        longest_source = sources[np.argmax(list_durations)]
        return [path for path in all_paths if longest_source in path]
    


#########################
#        CMIP5          #
#########################


def get_path_CMIP5_data(model, 
                        experiment, 
                        realisation, 
                        variable,
                        freq='mon',
                        source = 'spirit',
                        esgf_fallback=True):
    """
    Return path to corresponding CMIP5 model-experiment-realisation-variable gridded data. 
    
    freq : 'mon' or 'day'
        frequency of simulation result file. Default is 'mon'

    source : 'spirit' or 'esgf'
        default returns local path to access data from climserv but can return remote path from esgf
    
    esgf_fallback : True or False
        if True and source is 'spirit', will get the path from esgf if data does not exist on spirit.
    """
    if source == 'spirit':
        try:
            paths = get_path_CMIP5_data_spirit(model, 
                                               experiment,
                                               realisation, 
                                               variable, 
                                               freq=freq)
        except ValueError:
            if esgf_fallback:
                paths = get_path_CMIP5_data_esgf(model, 
                                                 experiment,
                                                 realisation, 
                                                 variable,
                                                 freq=freq)
            else:
                raise ValueError('No data on ESGF')
    elif source == 'esgf':
        paths = get_path_CMIP5_data_esgf(model,     
                                         experiment,
                                         realisation, 
                                         variable,
                                         freq=freq)
    else:
        raise ValueError('Source must be spirit or esgf')
    return paths

def get_path_CMIP5_data_spirit(model, 
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
        error_message = f"\nThere is no data for model '{model}' on Climserv\n"  #Check available models?
        raise ValueError(error_message)
    center = path_list_to_model[0].split('/')[-2]
    # Checks if model-experiment data is on spirit
    path_list_to_experiment = glob.glob(f"/bdd/CMIP5/output/{center}/{model}/{experiment}")
    if len(path_list_to_experiment) == 0:
        error_message = f"\nThere is no '{experiment}' data for model '{model}' on Climserv\n"  #Check available models?
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
            error_message = f"\nThere is no realisation '{realisation}' for '{experiment}' for model '{model}'on Climserv\n" + \
                            f"Available realisation for experiment '{experiment}' and model '{model}' are:\n     " + print_list(realisations_available)
            raise ValueError(error_message)

    # Checks if model-experiment-realisation-variable data is on spirit
    path_list_to_variable = glob.glob(f"{path_to_freq}/*/*/{realisation}/latest/{variable}")
    if len(path_list_to_variable) == 0:
        error_message = f"\nThere is no variable '{variable}' for this model-experiment-realisation combo on Climserv\n"  #Check available models?
        raise ValueError(error_message)
    path_to_variable = [path for path in path_list_to_variable if freq in path][0]
    final_paths = glob.glob(f"{path_to_variable}/*")
    if len(final_paths) == 0:
        error_message = f"\nThe directory exists but data are missing" 
        raise ValueError(error_message)
    return final_paths


def get_path_CMIP5_data_esgf(model, 
                             experiment, 
                             realisation, 
                             variable,
                             freq='mon'):        
        """
        Returns the remote ESGF path to the corresponding CMIP5 datasets they exist on ESGF.
        """
         # Checks model availability
        all_paths = esgf_search(project='CMIP5',
                                variable=variable,
                                experiment=experiment, 
                                ensemble=realisation,
                                model=model,
                                time_frequency=freq)
        if len(all_paths) == 0:
            raise ValueError("No such data exist on ESGF")
        # find longest source available
        sources = [path.split('/')[2] for path in all_paths]
        list_durations = []
        for source in sources:
            dates_source = [path.split('_')[-1][:-3].split('-') for path in all_paths if source in path]
            duration = sum([int(date[1][:-2]) - int(date[0][:-2]) for date in dates_source])
            list_durations.append(duration)
        longest_source = sources[np.argmax(list_durations)]
        return [path for path in all_paths if longest_source in path]
        
def print_list(model_list):
    return ('\n     '.join([f'{model:<30}' for model in sorted(model_list) if '.nc' not in model]))

