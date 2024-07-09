from __future__ import print_function
import requests
import xml.etree.ElementTree as ET

# Author: Unknown
# Script copied from the PANGEO project website: 
# http://gallery.pangeo.io/repos/pangeo-gallery/cmip6/search_and_load_with_esgf_opendap.html#

# API AT: https://github.com/ESGF/esgf.github.io/wiki/ESGF_Search_REST_API#results-pagination

# "https://esgf-data.dkrz.de/esg-search/search" 
# "https://esgf-node.llnl.gov/esg-search/search"
# "https://aims2.llnl.gov/esg-search/search"
# "https://esgf-node.ipsl.upmc.fr/esg-search/search"
# 
def esgf_search(server= "https://esgf-data.dkrz.de/esg-search/search",
                files_type="OPENDAP", local_node=True, project="CMIP6",
                verbose=False, format="application%2Fsolr%2Bjson",
                use_csrf=False, **search):
    """
    Example:

    results = esgf_search(activity_id='RFMIP', 
                          table_id='Amon', 
                          variable_id='rlut',
                          experiment_id='piClim-histnat', 
                          source_id='IPSL-CM6A-LR')
    # results gives a list of files corresponding to the search
    ds = xr.open_dataset(results[0])

    Args:
        server (str, optional): _description_. Defaults to "https://esgf-node.llnl.gov/esg-search/search".
        files_type (str, optional): _description_. Defaults to "OPENDAP".
        local_node (bool, optional): _description_. Defaults to True.
        project (str, optional): _description_. Defaults to "CMIP6".
        verbose (bool, optional): _description_. Defaults to False.
        format (str, optional): _description_. Defaults to "application%2Fsolr%2Bjson".
        use_csrf (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    client = requests.session()
    payload = search
    payload["project"] = project
    payload["type"]= "File"
    if local_node:
        payload["distrib"] = "false"
    if use_csrf:
        client.get(server)
        if 'csrftoken' in client.cookies:
            # Django 1.6 and up
            csrftoken = client.cookies['csrftoken']
        else:
            # older versions
            csrftoken = client.cookies['csrf']
        payload["csrfmiddlewaretoken"] = csrftoken

    payload["format"] = format

    offset = 0
    numFound = 10000
    all_files = []
    files_type = files_type.upper()
    while offset < numFound:
        payload["offset"] = offset
        url_keys = []
        for k in payload:
            url_keys += ["{}={}".format(k, payload[k])]

        url = "{}/?{}".format(server, "&".join(url_keys))
        # print(url)
        r = client.get(url)
        r.raise_for_status()
        resp = r.json()["response"]
        numFound = int(resp["numFound"])
        resp = resp["docs"]
        offset += len(resp)
        for d in resp:
            if verbose:
                for k in d:
                    print("{}: {}".format(k,d[k]))
            url = d["url"]
            for f in d["url"]:
                sp = f.split("|")
                if sp[-1] == files_type:
                    all_files.append(sp[0].split(".html")[0])
    # print(f'{len(all_files)} files found on ESGF')
    return sorted(all_files)