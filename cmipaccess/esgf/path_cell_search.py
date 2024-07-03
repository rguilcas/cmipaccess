import cmipaccess as cmip

def get_path_cell(model, 
                  variable, 
                  grid_label):
    """Finds the paths to a cell area file on esgf

    Args:
        model (str): Climate model
        variable (str): variable of the area file required. Can be areacello or areacella
        grid (str): grid label (usually gn, gr1, ...)

    Raises:
        ValueError: If the variable is not areacello or areacello raises this error

    Returns:
        str: html path to the area file
    """
    print('wo')
    if variable not in ['areacella','areacello']:
        raise ValueError('Variable can only be areacello or areacella')
    if variable=='areacella':
        table_id = 'fx'
    if variable=='areacello':
        table_id ='Ofx'
    
    for experiment in ['piControl', 'historical']:
        list_path_cell = cmip.esgf.esgf_search(variable_id=variable,
                                            experiment_id=experiment,
                                            table_id=table_id,
                                            grid_label=grid_label,
                                            source_id=model,)
        if len(list_path_cell)!=0:
            break
    if len(list_path_cell) == 0:
        raise ValueError('Area path not found in historical or piControl runs')
    return list_path_cell