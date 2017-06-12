#!/usr/bin/env python
import ConfigParser
from os.path import expanduser

Config = ConfigParser.ConfigParser()
Config.read(expanduser('~/.rbh-monitoring.ini'))

try:
    carbon_server = Config.get('rbh-monitoring_api', 'carbon_server')
except:
    carbon_server = ''

try:
    carbon_port = Config.getint('rbh-monitoring_api', 'carbon_port')
except:
    carbon_port = ''

try:
    db_host = Config.get('rbh-monitoring_api', 'db_host')
except:
    db_host = ''

try:
    db_user = Config.get('rbh-monitoring_api', 'db_user')
except:
    db_user = ''

try:
    db_pwd = Config.get('rbh-monitoring_api', 'db_pwd')
except:
    db_pwd = ''

try:
    db = Config.get('rbh-monitoring_api', 'db')
except:
    db = ''

try:
    path_graph = Config.get('rbh-monitoring_api', 'path_graph')
except:
    path_graph = ''

logAgeTab = ['modif', 'last_mod', 'acs', 'last_access', 'creat', 'creation_time', 'db', 'last_mdchange']
timespanTab = [('15min', 900), ('1h', 3600), ('12h', 43200), ('1d', 86400), ('1w', 604800), ('1m', 2592000), ('6m', 15552000), ('1y', 31104000), ('over1y', 0)]
