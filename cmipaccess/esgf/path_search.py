from .esgf_data_access import esgf_search
import numpy as np

def get_path_CMIP_data(model, 
                       experiment, 
                       realisation, 
                       variable,
                       grid=None,
                       freq='mon',
                       latest=True,
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
                                   latest=latest,
                                   grid=grid,
                                   freq=freq)
    elif generation == 'CMIP5':
        return get_path_CMIP6_data(model, 
                                   experiment, 
                                   realisation, 
                                   variable,
                                   latest=latest,
                                   freq=freq)
    elif generation is None:
        try:
            paths = get_path_CMIP6_data(model, 
                                        experiment, 
                                        realisation, 
                                        variable,
                                        grid=grid,
                                        latest=latest,
                                        freq=freq)
            return paths
        except ValueError:
            pass 
        try:
            paths = get_path_CMIP5_data(model, 
                                        experiment, 
                                        realisation, 
                                        variable,
                                        latest=latest,
                                        freq=freq)
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
                        latest=True,
                        grid=None):        
        """
        Returns the remote ESGF path to the corresponding datasets they exist on ESGF.
        """
         # Checks model availability
        all_paths = esgf_search(variable_id=variable,
                                experiment_id=experiment, 
                                member_id=realisation,
                                frequency=freq,
                                source_id=model,
                                latest=latest,)
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
                        latest=True):        
        """
        Returns the remote ESGF path to the corresponding CMIP5 datasets they exist on ESGF.
        """
         # Checks model availability
        all_paths = esgf_search(project='CMIP5',
                                variable=variable,
                                experiment=experiment, 
                                ensemble=realisation,
                                model=model,
                                time_frequency=freq,
                                latest=latest)
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
