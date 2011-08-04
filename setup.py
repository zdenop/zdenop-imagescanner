#!/usr/bin/env python

import os
import platform
from setuptools import setup, find_packages
from distutils.core import Extension

REQUIREMENTS = [
    'autoconnect', 
    'importlib',
    'PIL',
]
EXT_MODULES = []

if os.name == 'posix': 
    if platform.system() == 'Darwin':
        scanning_module = Extension('_scanning', 
                            sources=['imagescanner/backends/osx/_scanning.m'])
        EXT_MODULES.append(scanning_module)
    else:
        REQUIREMENTS.append('pysane')


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

