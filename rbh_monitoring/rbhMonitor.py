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
        query += "WHEN '%s' THEN %s\n" % (timespanTab[j][0], j + 1)
        j += 1
    query += "ELSE %s\nEND" % (j + 1)
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
        '-H', '--host', required=False, action='store', nargs='*', help='Database host name'
    )
    parser.add_argument(
        '-u', '--user', required=False, action='store', nargs='*', help='Database user name'
    )
    parser.add_argument(
        '-x', '--password', required=False, action='store', nargs='*', help='Database password'
    )
    parser.add_argument(
        '-d', '--database', required=False, action='store', nargs='*', help='Database name'
    )
    parser.add_argument(
        '-p', '--path', required=False, action='store', help='Path to data in Graphite'
    )
    parser.add_argument(
        '--verbose', required=False, action='store_true', help='Output steps to stdout'
    )
    parser.add_argument(
        '--dry-run', required=False, action='store_true', help='Output steps to stdout without pushing metrics'
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

    if args.verbose:
        print 'CARBON_SERVER: %s' % CARBON_SERVER

    if args.port:
        CARBON_PORT = args.port
    else:
        if config.carbon_port:
            CARBON_PORT = config.carbon_port
        else:
            print 'Error: missing Carbon port from config file !'
            exit(1)

    if args.verbose:
        print 'CARBON_PORT: %s' % CARBON_PORT

    if args.host:
        DB_HOST = args.host
    else:
        if config.db_host:
            DB_HOST = config.db_host
        else:
            print 'Error: missing database host name from config file !'
            exit(1)

    if args.verbose:
        print 'DB_HOST: %s' % DB_HOST

    if args.user:
        DB_USER = args.user
    else:
        if config.db_user:
            DB_USER = config.db_user
        else:
            print 'Error: missing database user name from config file !'
            exit(1)

    if args.verbose:
        print 'DB_USER: %s' % DB_USER

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

    if args.verbose:
        print 'DATABASE: %s' % DB

    if args.path:
        PATH_GRAPH = args.path
    else:
        if config.path_graph:
            PATH_GRAPH = config.path_graph
        else:
            print 'Error: missing path to graphite folder from config file !'
            exit(1)

    if args.verbose:
        print 'PATH_GRAPH: %s' % PATH_GRAPH

    if args.dry_run:
        dry_run = args.dry_run
        print '[DRY RUN]'
    else:
        dry_run = False

    if (len(DB_HOST) is not len(DB_USER)) or (len(DB_HOST) is not len(DB_PWD)) or (len(DB_HOST) is not len(DB)):
        print 'Error: Mismatch in database information list length\nVerify your arguments/conf.file list of databases'
        exit(1)

    logAgeTab = ['modif', 'last_mod', 'acs', 'last_access', 'creat', 'creation_time', 'db', 'last_mdchange']
    timespanTab = [('15min', 900), ('1h', 3600), ('12h', 43200), ('1d', 86400), ('1w', 604800), ('1m', 2592000), ('6m', 15552000), ('1y', 31104000), ('over1y', 0)]
    ite = 0

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((CARBON_SERVER, CARBON_PORT))
        if args.verbose:
            print 'Connecting to %s using port(%s) [TCP]' % (CARBON_SERVER, CARBON_PORT)
    except socket.error, exc:
        print 'Error: Connection to carbon server failed', exc
        exit(1)

    while (ite < max(len(DB_HOST), len(DB_USER), len(DB_PWD), len(DB))):

        timestamp = time.time()
        total = [0, 0]
        message = ''

        if args.verbose:
            print '\nStart time for %s: %s' % (DB_HOST[ite], timestamp)

        try:
            connection = MySQLdb.connect(DB_HOST[ite], DB_USER[ite], DB_PWD[ite], DB[ite])
            if args.verbose:
                print 'Connecting to %s as %s on %s (using password:%s)' % (DB[ite], DB_USER[ite], DB_HOST[ite], ('YES' if DB_PWD[ite] else 'NO'))
        except MySQLdb.Error as e:
            print 'Error: Connection to MySQL Database failed\n', e[0], e[1]
            exit(1)
        else:
            db = connection.cursor()

        try:
            db.execute("""SELECT COUNT(size) AS cnt, SUM(size) AS vol FROM ENTRIES""")
            if args.verbose:
                print '\nexecute => SELECT COUNT(size) AS cnt, SUM(size) AS vol FROM ENTRIES'
        except MySQLdb.Error as e:
            print 'Error: Query failed to execute [Retrieving COUNT(size) and SUM(size)]\n', e[0], e[1]
            exit(1)
        else:
            total = db.fetchone()

        i = 0
        length = len(timespanTab)
        while (i < len(logAgeTab)):
            try:
                query = buildQuery(i, length, logAgeTab, timespanTab)
                db.execute(query)
                if args.verbose:
                    print 'execute => %s' % query
            except MySQLdb.Error as e:
                print 'Error: Query failed to execute [BUILDING table]\n', e[0], e[1]
                exit(1)
            else:
                j = 0
                row = [0, 0]
                nextRow = db.fetchone()

                if args.verbose:
                    print '=================================='

                while (j < length):

                    if (nextRow is not None and nextRow[0] == timespanTab[j][0]):
                        row = (nextRow[1] + row[0], nextRow[2] + row[1])
                        nextRow = db.fetchone()

                    try:
                        message += '%s.%sTempGraph.cnt.%s %i %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j][0], row[0], timestamp)
                        message += '%s.%s.%sTempGraph.cntAvg.%s %s %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j][0], row[0] / (total[0] if total[0] else 1), timestamp)
                        message += '%s.%s.%sTempGraph.size.%s %i %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j][0], row[1], timestamp)
                        message += '%s.%s.%sTempGraph.sizeAvg.%s %s %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j][0], row[1] / (total[1] if total[1] else 1), timestamp)
                        message += '%s.%s.%sTempGraph.sizeFileAvg.%s %s %s\n' % (PATH_GRAPH, logAgeTab[i], timespanTab[j][0], row[1] / (row[0] if row[0] else 1), timestamp)

                        if args.verbose:
                            print '%s' % message
                    except:
                        print 'Error: Message failed to be built from row = %s' % timespanTab[j][0]
                        exit(1)

                    try:
                        if not dry_run:
                            sock.sendall(message)
                    except:
                        print '\nError: Discussion with carbon server failed'
                        exit(1)

                    message = ''
                    j += 1
            if args.verbose:
                print '=================================='
            i += 2

        try:
            db.execute("""SELECT varname, value FROM VARS WHERE varname LIKE 'ChangelogCount_%'""")
            if args.verbose:
                print 'execute => SELECT varname, value FROM VARS WHERE varname LIKE \'ChangelogCount_%\''
        except MySQLdb.Error as e:
            print 'Error: Query failed to execute [Retrieving ChangelogCount]\n', e[0], e[1]
            exit(1)
        else:
            message = ''
            row = db.fetchone()
            while (row is not None):
                message += '%s.chnglogActivity.%s %s %s\n' % (PATH_GRAPH, row[0], row[1], timestamp)
                row = db.fetchone()
            try:
                if not dry_run:
                    sock.sendall(message)
                if args.verbose:
                    print '\n%s' % message
            except:
                print 'Error: Discussion with carbon server failed'
                exit(1)

        try:
            db.close()
            if args.verbose:
                print 'Closing connection to MySQL database'
                print 'Execution time for %s (in sec): %s' % (DB_HOST[ite], time.time() - timestamp)
        except:
            print 'Error: Connection to database failed to close'
            exit(1)

        ite += 1

    try:
        sock.close()
        if args.verbose:
            print 'Closing connection to Carbon server'
    except:
        print 'Error: Connection to carbon server failed to close'
        exit(1)
