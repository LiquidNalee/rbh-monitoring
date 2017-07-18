#!/usr/bin/env python
import ConfigParser
import json
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
    db_host = json.loads(Config.get('rbh-monitoring_api', 'db_host'))
except:
    db_host = []

try:
    db_user = json.loads(Config.get('rbh-monitoring_api', 'db_user'))
except:
    db_user = []

try:
    db_pwd = json.loads(Config.get('rbh-monitoring_api', 'db_pwd'))
except:
    db_pwd = []

try:
    db = json.loads(Config.get('rbh-monitoring_api', 'db'))
except:
    db = []

try:
    path_graph = Config.get('rbh-monitoring_api', 'path_graph')
except:
    path_graph = []
