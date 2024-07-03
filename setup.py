from setuptools import setup
setup(name='cmipaccess',
version='0.6',
description='Easy access to CMIP5 and CMIP6 data from ESGF and SpiritX',
url='#',
author='Robin Guillaume-Castel',
author_email='r.guilcas@outlook.com',
license='MIT',
packages=['cmipaccess', 'cmipaccess.esgf', 'cmipaccess.spiritx', 'cmipaccess.local'],
zip_safe=False) 
 
