#!/usr/bin/env python

import socket
import time
import argparse
from sys import exit
from rbhMetric import config
import MySQLdb


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
            print 'ERROR: missing Carbon server address from config file !'
            exit(1)

    if args.port:
        CARBON_PORT = args.port
    else:
        if config.carbon_port:
            CARBON_PORT = config.carbon_port
        else:
            print 'ERROR: missing Carbon port from config file !'
            exit(1)

    if args.host:
        DB_HOST = args.host
    else:
        if config.db_host:
            DB_HOST = config.db_host
        else:
            print 'ERROR: missing database host name from config file !'
            exit(1)

    if args.user:
        DB_USER = args.user
    else:
        if config.db_user:
            DB_USER = config.db_user
        else:
            print 'ERROR: missing database user name from config file !'
            exit(1)

    if args.password:
        DB_PWD = args.password
    else:
        if config.db_pwd:
            DB_PWD = config.db_pwd
        else:
            print 'ERROR: missing database password from config file !'
            exit(1)

    if args.database:
        DB = args.database
    else:
        if config.db:
            DB = config.db
        else:
            print 'ERROR: missing database from config file !'
            exit(1)

    if args.path:
        PATH_GRAPH = args.path
    else:
        if config.path_graph:
            PATH_GRAPH = config.path_graph
        else:
            print 'ERROR: missing path to graphite folder from config file !'
            exit(1)

    begin = time.time()
    total = [0, 0]
    message = ''

    try:
        connection = MySQLdb.connect(DB_HOST, DB_USER, DB_PWD, DB)
    except:
        print 'Error: Unable to connect'
        exit(1)
    else:
        db = connection.cursor()

    try:
        db.execute("""SELECT COUNT(size) AS cnt, SUM(size) AS vol FROM ENTRIES""")
    except:
        print 'Error: Query failed to execute'
        exit(1)
    else:
        row = db.fetchone()
        total = row

    try:
        db.execute("""
        SELECT modif, cntM, volM, cntA, volA, cntC, volC, cntD, volD FROM
            (SELECT modif, SUM(c) AS cntM, SUM(v) AS volM FROM (
                SELECT c, v, CASE
                    WHEN log_age < ROUND(LOG(10,900),5) THEN '15min'
                    WHEN log_age < ROUND(LOG(10,3600),5) THEN '1h'
                    WHEN log_age < ROUND(LOG(10,43200),5) THEN '12h'
                    WHEN log_age < ROUND(LOG(10,86400),5) THEN '1d'
                    WHEN log_age < ROUND(LOG(10,604800),5) THEN '1w'
                    WHEN log_age < ROUND(LOG(10,2592000),5) THEN '1m'
                    WHEN log_age < ROUND(LOG(10,15552000),5) THEN '6m'
                    WHEN log_age < ROUND(LOG(10,31104000),5) THEN '1y'
                    ELSE 'over1y'
                    END
                AS modif FROM (
                    SELECT ROUND(LOG(10,UNIX_TIMESTAMP(NOW())-last_mod),5) AS log_age,
                    COUNT(*) AS c,
                    IFNULL(SUM(size),0) AS v
                    FROM ENTRIES GROUP BY log_age)
                AS ps )
            AS stats GROUP BY modif ) modif_tb
            LEFT JOIN
            (SELECT acs, SUM(c) AS cntA, SUM(v) AS volA FROM (
                SELECT c, v, CASE
                    WHEN log_age < ROUND(LOG(10,900),5) THEN '15min'
                    WHEN log_age < ROUND(LOG(10,3600),5) THEN '1h'
                    WHEN log_age < ROUND(LOG(10,43200),5) THEN '12h'
                    WHEN log_age < ROUND(LOG(10,86400),5) THEN '1d'
                    WHEN log_age < ROUND(LOG(10,604800),5) THEN '1w'
                    WHEN log_age < ROUND(LOG(10,2592000),5) THEN '1m'
                    WHEN log_age < ROUND(LOG(10,15552000),5) THEN '6m'
                    WHEN log_age < ROUND(LOG(10,31104000),5) THEN '1y'
                    ELSE 'over1y'
                    END
                AS acs FROM (
                    SELECT ROUND(LOG(10,UNIX_TIMESTAMP(NOW())-last_access),5) AS log_age,
                    COUNT(*) AS c,
                    IFNULL(SUM(size),0) AS v
                    FROM ENTRIES GROUP BY log_age)
                AS ps )
            AS stats GROUP BY acs ) acs_tb ON acs_tb.acs = modif_tb.modif
            LEFT JOIN
            (SELECT crt, SUM(c) AS cntC, SUM(v) AS volC FROM (
                SELECT c, v, CASE
                    WHEN log_age < ROUND(LOG(10,900),5) THEN '15min'
                    WHEN log_age < ROUND(LOG(10,3600),5) THEN '1h'
                    WHEN log_age < ROUND(LOG(10,43200),5) THEN '12h'
                    WHEN log_age < ROUND(LOG(10,86400),5) THEN '1d'
                    WHEN log_age < ROUND(LOG(10,604800),5) THEN '1w'
                    WHEN log_age < ROUND(LOG(10,2592000),5) THEN '1m'
                    WHEN log_age < ROUND(LOG(10,15552000),5) THEN '6m'
                    WHEN log_age < ROUND(LOG(10,31104000),5) THEN '1y'
                    ELSE 'over1y'
                    END
                AS crt FROM (
                    SELECT ROUND(LOG(10,UNIX_TIMESTAMP(NOW())-creation_time),5) AS log_age,
                    COUNT(*) AS c,
                    IFNULL(SUM(size),0) AS v
                    FROM ENTRIES GROUP BY log_age)
                AS ps )
            AS stats GROUP BY crt ) crt_tb ON crt_tb.crt = modif_tb.modif
            LEFT JOIN
            (SELECT chng, SUM(c) AS cntD, SUM(v) AS volD FROM (
                SELECT c, v, CASE
                    WHEN log_age < ROUND(LOG(10,900),5) THEN '15min'
                    WHEN log_age < ROUND(LOG(10,3600),5) THEN '1h'
                    WHEN log_age < ROUND(LOG(10,43200),5) THEN '12h'
                    WHEN log_age < ROUND(LOG(10,86400),5) THEN '1d'
                    WHEN log_age < ROUND(LOG(10,604800),5) THEN '1w'
                    WHEN log_age < ROUND(LOG(10,2592000),5) THEN '1m'
                    WHEN log_age < ROUND(LOG(10,15552000),5) THEN '6m'
                    WHEN log_age < ROUND(LOG(10,31104000),5) THEN '1y'
                    ELSE 'over1y'
                    END
                AS chng FROM (
                    SELECT ROUND(LOG(10,UNIX_TIMESTAMP(NOW())-last_mdchange),5) AS log_age,
                    COUNT(*) AS c,
                    IFNULL(SUM(size),0) AS v
                    FROM ENTRIES GROUP BY log_age)
                AS ps )
            AS stats GROUP BY chng ) chngdb_tb ON chngdb_tb.chng = modif_tb.modif
        """)
    except:
        print 'Error: Query failed to execute'
        exit(1)
    else:
        try:
            row = db.fetchone()
            while (row is not None):
                if (row[1] is not None):
                    message += '%s.modTempGraph.cnt.%s %i %s\n' % (PATH_GRAPH, row[0], row[1], begin)
                    message += '%s.modTempGraph.cntAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[1] / total[0], begin)
                    message += '%s.modTempGraph.size.%s %i %s\n' % (PATH_GRAPH, row[0], row[2], begin)
                    message += '%s.modTempGraph.sizeAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[2] / total[1], begin)
                if (row[3] is not None):
                    message += '%s.acsTempGraph.cnt.%s %i %s\n' % (PATH_GRAPH, row[0], row[3], begin)
                    message += '%s.acsTempGraph.cntAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[3] / total[0], begin)
                    message += '%s.acsTempGraph.size.%s %i %s\n' % (PATH_GRAPH, row[0], row[4], begin)
                    message += '%s.acsTempGraph.sizeAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[4] / total[1], begin)
                if (row[5] is not None):
                    message += '%s.creatTempGraph.cnt.%s %i %s\n' % (PATH_GRAPH, row[0], row[5], begin)
                    message += '%s.creatTempGraph.cntAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[5] / total[0], begin)
                    message += '%s.creatTempGraph.size.%s %i %s\n' % (PATH_GRAPH, row[0], row[6], begin)
                    message += '%s.creatTempGraph.sizeAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[6] / total[1], begin)
                if (row[7] is not None):
                    message += '%s.dbTempGraph.cnt.%s %i %s\n' % (PATH_GRAPH, row[0], row[7], begin)
                    message += '%s.dbTempGraph.cntAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[7] / total[0], begin)
                    message += '%s.dbTempGraph.size.%s %i %s\n' % (PATH_GRAPH, row[0], row[8], begin)
                    message += '%s.dbTempGraph.sizeAvg.%s %s %s\n' % (PATH_GRAPH, row[0], row[8] / total[1], begin)
                row = db.fetchone()
        except:
            print 'Error: Data failed to be processed'
            exit(1)

    try:
        db.execute("""SELECT varname, value FROM VARS WHERE varname LIKE 'ChangelogCount_%'""")
    except:
        print 'Error: Query failed to execute'
        exit(1)
    else:
        row = db.fetchone()
        while (row is not None):
            message += '%s.chnglogActivity.%s %s %s\n' % (PATH_GRAPH, row[0], row[1], begin)
            row = db.fetchone()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((CARBON_SERVER, CARBON_PORT))
    except:
        print 'Error: Connection to carbon server failed'
        exit(1)

    try:
        sock.sendall(message)
        message = '%s.execTime %s %s' % (PATH_GRAPH, time.time() - begin, begin)
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
