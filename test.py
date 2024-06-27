from cmipspirit.CMIP_path_search import get_path_CMIP5_data_esgf

print(get_path_CMIP5_data_esgf('IPSL-CM5A-LR','piControl', 'r1i1p1', 'areacello'))

from pyesgf.search import SearchConnection
conn = SearchConnection('https://esgf-data.dkrz.de/esg-search', distrib=True)