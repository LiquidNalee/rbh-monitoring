#!/usr/bin/env python

import socket
import time
import argparse
from sys import exit
from rbh_monitoring import config
import MySQLdb


def buildQuery(i, length, logAgeTab, timespanTab):

    query = "SELECT %s, IFNULL(SUM(c), 0) AS cnt, IFNULL(SUM(v), 0) AS vol FROM (\nSELECT c, v, CASE\n" % (logAgeTab[i])
    j = 0
    while (j < length - 1):
        query += "WHEN log_age < ROUND(LOG(10,%s),5) THEN '%s'\n" % (timespanTab[j][1], timespanTab[j][0])
        j += 1
    query += "ELSE '%s'\nEND\nAS %s FROM (\n" % (timespanTab[j][0], logAgeTab[i])
    query += "SELECT ROUND(LOG(10,UNIX_TIMESTAMP(NOW())-%s),5) AS log_age,\n" % (logAgeTab[i + 1])
    query += "COUNT(*) AS c,\nIFNULL(SUM(size),0) AS v\nFROM ENTRIES GROUP BY log_age)\nAS ps)\n"
    query += "AS stats GROUP BY %s\nORDER BY CASE %s\n" % (logAgeTab[i], logAgeTab[i])
    j = 0
    while (j < length - 1):
        query += "WHEN '%s' THEN %i\n" % (timespanTab[j][0], j + 1)
        j += 1
    query += "ELSE %i\nEND" % (j + 1)
    return(query)


def graph():

    parser = argparse.ArgumentParser(description='Retrieves data from MySQL database and sends it to graphite server')
    parser.add_argument(
        '-S', '--server', required=False, action='store', help='Carbon server address'
    )
    parser.add_argument(
        '-P', '--port', required=False, type=int, action='store', help='Carbon server port'
    )
    parser.add_argument(
        '-H', '--host', required=False, action='store', help='Database host name'
    )
    parser.add_argument(
        '-u', '--user', required=False, action='store', help='Database user name'
    )
    parser.add_argument(
        '-x', '--password', required=False, action='store', help='Database password'
    )
    parser.add_argument(
        '-d', '--database', required=False, action='store', help='Database name'
    )
    parser.add_argument(
        '-p', '--path', required=False, action='store', help='Path to data in Graphite'
    )

    args = parser.parse_args()

    if args.server:
        CARBON_SERVER = args.server
    else:
        if config.carbon_server:
            CARBON_SERVER = config.carbon_server
        else:
            print 'Error: missing Carbon server address from config file !'
            exit(1)

    if args.port:
        CARBON_PORT = args.port
    else:
        if config.carbon_port:
            CARBON_PORT = config.carbon_port
        else:
            print 'Error: missing Carbon port from config file !'
            exit(1)

    if args.host:
        DB_HOST = args.host
    else:
        if config.db_host:
            DB_HOST = config.db_host
        else:
            print 'Error: missing database host name from config file !'
            exit(1)

    if args.user:
        DB_USER = args.user
    else:
        if config.db_user:
            DB_USER = config.db_user
        else:
            print 'Error: missing database user name from config file !'
            exit(1)

    if args.password:
        DB_PWD = args.password
    else:
        if config.db_pwd:
            DB_PWD = config.db_pwd
        else:
            print 'Error: missing database password from config file !'
            exit(1)

    if args.database:
        DB = args.database
    else:
        if config.db:
            DB = config.db
        else:
            print 'Error: missing database from config file !'
            exit(1)

    if args.path:
        PATH_GRAPH = args.path
    else:
        if config.path_graph:
            PATH_GRAPH = config.path_graph
        else:
            print 'Error: missing path to graphite folder from config file !'
            exit(1)

    if config.timespanTab:
        timespanTab = config.timespanTab
    else:
        print 'Error: Timespan table has been unset in rbh_monitoring/config.py !'
        exit(1)

    if config.logAgeTab:
        logAgeTab = config.logAgeTab
    else:
        print 'Error: logAge table has been unset in rbh_monitoring/config.py !'
        exit(1)

    begin = time.time()
    total = [0, 0]
    message = ''

    try:
        connection = MySQLdb.connect(DB_HOST, DB_USER, DB_PWD, DB)
    except:
        print 'Error: Connection to MySQL Database failed'
        exit(1)
    else:
        db = connection.cursor()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((CARBON_SERVER, CARBON_PORT))
    except:
        print 'Error: Connection to carbon server failed'
        exit(1)

    try:
        db.execute("""SELECT COUNT(size) AS cnt, SUM(size) AS vol FROM ENTRIES""")
    except MySQLdb.Error, e:
        print 'Error: Query failed to execute [Retrieving COUNT(size) and SUM(size)]', e[0], e[1]
        exit(1)
    else:
        total = db.fetchone()

    i = 0
    length = len(timespanTab)
    while (i <= 6):
        try:
            db.execute(buildQuery(i, length, logAgeTab, timespanTab))
        except MySQLdb.Error, e:
            print 'Error: Query failed to execute [BUILDING]', e[0], e[1]
            exit(1)
        else:
            j = 0
            row = [0, 0]
            nextRow = db.fetchone()
            while (j < length):

                if (nextRow is not None and nextRow[0] == timespanTab[j]):
                    row = (nextRow[1] + row[0], nextRow[2] + row[1])
                    nextRow = db.fetchone()

                try:
                    message += '%s.%sTempGraph.cnt.%s %i %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j], row[0], begin)
                    message += '%s.%sTempGraph.cntAvg.%s %s %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j], row[0] / total[0], begin)
                    message += '%s.%sTempGraph.size.%s %i %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j], row[1], begin)
                    message += '%s.%sTempGraph.sizeAvg.%s %s %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j], row[1] / total[1], begin)
                    message += '%s.%sTempGraph.sizeFileAvg.%s %s %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j], row[1] / (row[0] if row[0] else 1), begin)
                except:
                    print 'Error: Data failed to be processed'
                    exit(1)

                try:
                    sock.sendall(message)
                except:
                    print 'Error: Discussion with carbon server failed'
                    exit(1)

                message = ''
                j += 1
        i += 2

    try:
        db.execute("""SELECT varname, value FROM VARS WHERE varname LIKE 'ChangelogCount_%'""")
    except MySQLdb.Error, e:
        print 'Error: Query failed to execute [Retrieving ChangelogCount]', e[0], e[1]
        exit(1)
    else:
        message = ''
        row = db.fetchone()
        while (row is not None):
            message += '%s.chnglogActivity.%s %s %s\n' % (PATH_GRAPH, row[0], row[1], begin)
            row = db.fetchone()
        try:
            sock.sendall(message)
        except:
            print 'Error: Discussion with carbon server failed'
            exit(1)

    try:
        sock.close()
        db.close()
    except:
        print 'Error: Connection to database/carbon server failed to close'
        exit(1)
