#! /usr/bin/env python

from setuptools import setup, find_packages

# Extracts the __version__
VERSION = [
    l for l in open('rbh_monitoring/__init__.py').readlines()
    if l.startswith('__version__ = ')
][0].split("'")[1]

setup(
    name='rbh-monitoring',
    version=VERSION,
    packages=find_packages(),
    description='rbh Monitoring tool using graphite',
    keywords='rbh robinhood graphite metric monitoring',
    author='Sami BOUCENNA',
    author_email='liquid.same@gmail.fr',
    entry_points={'console_scripts': ['rbh-monitoring = rbh_monitoring.rbhMonitor:graph']},
    install_requires=['MySQL-python'],
)
