from pyesgf.search import SearchConnection
from ..tools import sort_realisations

def find_models_experiment(experiment, 
                           variable='tas',
                           table='Amon'):
    """
    Finds the models where the experiment has been ran and where the variable is available
    """
    def get_models(conn):
        facets='source_id,member_id,data_node'
        ctx = conn.new_context(
            project='CMIP6',
            experiment_id=experiment,
            variable=variable,
            table_id=table,
            facets=facets)
        models = list(ctx.facet_counts['source_id'].keys())
        models.sort()
        return models
        
    try:
        conn = SearchConnection('https://esgf-node.llnl.gov/esg-search', distrib=True)
        return get_models(conn)
    except:
        conn = SearchConnection('https://esgf-data.dkrz.de/esg-search', distrib=True)
        return get_models(conn)

def find_realisations_experiment(model,
                                 experiment, 
                                 variable='tas',
                                 table='Amon'):
    """
    Finds the realisations where the experiment has been ran with the model and where the variable is available
    """
    def get_reals(conn):
        facets='source_id,member_id,data_node'
        ctx = conn.new_context(
            project='CMIP6',
            experiment_id=experiment,
            variable=variable,
            source_id=model,
            table_id=table,
            facets=facets)
        realisations = list(ctx.facet_counts['member_id'].keys())
        return sort_realisations(realisations)
    try:
        conn = SearchConnection('https://esgf-node.llnl.gov/esg-search', distrib=True)
        return get_reals(conn)
    except:
        conn = SearchConnection('https://esgf-data.dkrz.de/esg-search', distrib=True)
        return get_reals(conn)
    