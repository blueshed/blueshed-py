#!/usr/bin/env python

from setuptools import setup, find_packages
import sys, os

version = '0.30'

setup(name='blueshed-py',
      version=version,
      packages=['blueshed'],
      package_dir={'blueshed': 'src/blueshed'},
      include_package_data = True, 
      exclude_package_data = { '': ['*tests/*','*examples/*'] },
      install_requires = [
        'setuptools',
        'tornado>=4.2',
        'sqlalchemy>=1.0.5',
        'pymysql>=0.6.6',
        "Pillow>=2.7.0",
        "boto==2.36.0"
      ],)