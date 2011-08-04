#!/usr/bin/env python

import os
import platform
from distutils import version
from distutils.core import Extension

from setuptools import setup, find_packages


REQUIREMENTS = ['autoconnect', 'PIL']
EXT_MODULES = []

if os.name == 'posix': 
    if platform.system() == 'Darwin':
        scanning_module = Extension('_scanning', 
                            sources=['imagescanner/backends/osx/_scanning.m'])
        EXT_MODULES.append(scanning_module)
    else:
        REQUIREMENTS.append('pysane>=2.0.1')

# If python version < 2.7 the backport from pypi will be 
#   required 
if platform.python_version() < version.StrictVersion("2.7"):
    REQUIREMENTS.append('importlib')

setup(name='imagescanner',
      version='0.9',
      description='Multi-platform Python library to access scanner devices.',
      author='Sergio Oliveira',
      author_email='seocam@seocam.com',
      url='http://code.google.com/p/imagescanner/',
      packages=find_packages(),
      package_data={'': ['*.tiff']},
      install_requires=REQUIREMENTS,
      ext_modules=EXT_MODULES,
     )

