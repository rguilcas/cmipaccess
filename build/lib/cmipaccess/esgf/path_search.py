from .esgf_data_access import esgf_search
import numpy as np
from pyesgf.search import SearchConnection


def get_path_CMIP_data(model, 
                       experiment, 
                       realisation, 
                       variable,
                       grid=None,
                       freq='mon',
                       latest=True,
                       server=None,
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
                                   freq=freq,
                                   server=server)
    elif generation == 'CMIP5':
        return get_path_CMIP5_data(model, 
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
                                        server=server,
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
                        server=None,
                        grid='gn'):        
        """
        Returns the remote ESGF path to the corresponding datasets they exist on ESGF.
        """
         # Checks model availability
        
        def get_context(conn):
            facets = 'source_id,member_id,data_node'
            ctx = conn.new_context(
                        project='CMIP6',
                        source_id=model,
                        experiment_id=experiment,
                        variable=variable,
                        frequency=freq,
                        grid_label=grid,
                        latest=latest,
                        variant_label=realisation,
                        facets='facets',)
            return ctx
        data_source = ["https://esgf-node.llnl.gov/esg-search",
                    #    "https://esgf-data3.ceda.ac.uk/esg-search",
                    #    "https://aims2.llnl.gov/esg-search",
                       "https://esgf-node.ipsl.upmc.fr/esg-search",
                    #    "https://esg1.umr-cnrm.fr/esg-search",
                       "https://esgf-data.dkrz.de/esg-search" ,
                        ]
        for source in data_source:
            print(source)
            conn = SearchConnection(source, distrib=True)
            ctx = get_context(conn)
            hits = ctx.hit_count
            print(hits)
            if hits > 0:
                result_datasets = ctx.search()
                all_server_name = [dataset.dataset_id.split('|')[-1] for dataset in result_datasets]
                if server is None:
                    server_required = all_server_name[0]
                else:
                    server_required = [k for k in all_server_name if server in k]
                    if len(server_required) == 0:
                        print(f"Server not available on {source}. Available servers are :")
                        print(all_server_name)            
                        continue
                    else:
                        server_required = server_required[0]
                for dataset in result_datasets:#[0]
                    dataset_name = dataset.dataset_id.split('|')[-1]
                    if dataset_name == server_required:
                        files = dataset.file_context().search()
                        urls = []
                        for file in files:
                            urls.append(file.opendap_url)
                            return urls
            else:
                continue
        raise ValueError('Data not found on ESGF')


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
