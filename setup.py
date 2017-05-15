#! /usr/bin/env python

from setuptools import setup, find_packages

# Extracts the __version__
VERSION = [
    l for l in open('rbhMetric/__init__.py').readlines()
    if l.startswith('__version__ = ')
][0].split("'")[1]

setup(
    name='rbhMetric',
    version=VERSION,
    packages=find_packages(),
    description='rbh Monitoring tool using graphite',
    keywords='rbh robinhood graphite metric monitoring',
    author='Sami BOUCENNA',
    author_email='sami.boucenna@cfm.fr',
    entry_points={'console_scripts': ['rbhMetric-monitoring = rbhMetric.rbhMonitor:graph']},
    install_requires=['MySQL-python'],
)
