# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys, os
import datetime
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../lenapy'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'cmipaccess'
copyright = '2024, Robin Guillaume-Castel'
author = 'Robin Guillaume-Castel'
release = '0.3.0'


# import os
# import sys 
# sys.path.insert(_index:0, os.path.abspath('..'))
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary'
]



# autosummaries from source-files : use .. autosummary::
autosummary_generate = True
# Inherit docstrings from parent classes
autodoc_inherit_docstrings = True
# autodoc don't show __init__ docstring
autoclass_content = "both"
# sort class members by their order in the source
autodoc_member_order = 'bysource'

# show all members of a class in the Methods and Attributes sections automatically
numpydoc_show_class_members = True
# create a Sphinx table of contents for the lists of class methods and attributes
numpydoc_class_members_toctree = True
# show all inherited members of a class in the Methods and Attributes sections
numpydoc_show_inherited_class_members = True


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
