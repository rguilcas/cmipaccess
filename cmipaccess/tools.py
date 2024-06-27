import pandas as pd
import re

def sort_realisations(list_realisations):
    split_strings = [re.split("[ripf]", realisation) for realisation in list_realisations]
    dataframe_strings = pd.DataFrame(split_strings, 
                                     columns = ['0','r','i','p','f']).iloc[:,1:]
    real_index = dataframe_strings.astype(int).sort_values(by=['f','p','i','r']).index
    sorted_realisations = [list_realisations[k] for k in real_index]
    return sorted_realisations