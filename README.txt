I   - Introduction
II  - Compiling
III - Robinhood setup
IV  - First run
V   - Configuration file
VI  - Graphite Tree description

I - Introduction
================

Using the robinhood MySQL database and a carbon server,
rbh-monitoring provides a graphite with all the data to monitor
a Lustre filesystem :
- size, average size per file and number of inodes created by timestamp
- size, average size per file and number of inodes accessed by timestamp
- size, average size per file and number of inodes modified by timestamp
- size, average size per file and number of inodes modified in the database by timestamp
- number of changelogs consumed by the database

The command 'rbh-monitoring' is to be scheduled in a crontab to run
periodically.
See the associated grafana dashboard here : https://grafana.com/dashboards/2276
Or go to Grafana.com and import the rbh-monitoring.json file

II - Compiling
==============

2.1 - From source tarball
-------------------------

It is advised to build rbh-monitoring on your target system,
to ensure the best compatibility with your Lustre and MySQL versions.

Build requirements: python, mysql-python, pip

Unzip and untar the source distribution:
> tar xzvf rbh-monitoring-0.x.x.tar.gz
> cd rbh-monitoring-0.x.x

Build:
> python setup.py sdist
> pip install dist/rbh-monitoring-0.x.x.tar.gz

Compiled package is generated in the 'dist/' directory.
rbh-monitoring is now an available command.

2.2 - From git repository
-------------------------

# Install git and autotools stuff:
> yum install git automake autoconf libtool

# Retrieve rbh-monitoring sources:
> git clone https://github.com/LiquidSame/rbh-monitoring.git
> cd rbh-monitoring
> git checkout master (or other branch)

Then refer to section 2.1 for next compilation steps.

III - Robinhood setup
====================

In order to use rbh-monitoring, your filesystem needs to run
Robinhood-3.x, an open-source software available here :
    https://github.com/cea-hpc/robinhood.git

It is best to use the changelog reader with robinhood.
# On your MDT
lfs changelog_register <device>

# Save the changelog reader id to your robinhood conf.file
# Make sure to have the '--readlog' option for your daemon

# Set 'last_access_only_atime' to True in robinhood/src/common/global_config.c 
# Recommended to differentiate read and write operations using grafana dashboard

IV - First run
===============

Even if your filesystem is empty, you need to perform an initial scan
in order to initialize robinhood database.
This prevents from having entries in filesystem that it wouldn't know about.
robinhood --scan --once

# create a conf.file for rbh-monitoring (see 'V - Configuration file')
vim ~/.rbh-monitoring.ini
# or execute it with arguments (see 'rbh-monitoring --help')
rbh-monitoring -u robinhood -h localhost -P 3003 -p "loginX.rbhMonitoring"

Data with the appropriate timestamp will be sent to the chosen carbon server
or an error will be issued.

In order to have a continuous flow of data, add this line to your crontab :
* * * * * /bin/bash -l -c "/path/to/rbh-monitoring &>> /path/to/log/file 2>&1"

V - Configuration file
======================

(Can be changed on the fly)
template for '~/.rbh-monitoring.ini' :
[rbh-monitoring_api]
carbon_server = "..."
carbon_port = 2003
db_host = "..."
db_user = "robinhood"
db_pwd = "..."
db = "robinhood_lustre"
path_graph = "..."

(Will require the tar to be rebuilt)
In 'rbh-monitoring/rbh_monitoring/config.py' :
- you may change the timespanTab variable as follows
    => timespanTab = [(timespan_name (ex: '15min'), timespan_in_seconds (ex: 900)), ...]
    (timespanTab has to be sorted)

- you may change the logAgeTab variable if the timestamps column ID in ENTRIES were modified in the database
    (default : id, uid, gid, size, blocks, creation_time, last_access, last_mod, last_mdchange,
               type, mode, nlink, md_update, invalid, fileclass, class_update)

VI - Graphite Tree description
=================================

Default result for rbh-monitoring :
(all TempGraph folders contain the same tree)

-PATH_GRAPH/                        (Tree's root directory named <prefix> from arguments/config)
    -acsTempGraph/                  (Entries grouped by last_access_time)
        -cnt/                       (Number of inodes last accessed within a timespan)
            -12h                    (timespan = < 12 hours)
            -15min                  (timespan = < 15 minutes)
            -1d                     (timespan = < 1 day)
            -1h                     (timespan = < 1 hour)
            -1m                     (timespan = < 1 month)
            -1w                     (timespan = < 1 week)
            -1y                     (timespan = < 1 year)
            -6m                     (timespan = < 6 month)
            -over1y                 (timespan = > 1 year)
            
        -cntAvg/                    (Percentage of inodes last accessed within a timespan proportional to FS' total)
        -size/                      (Total volume last accessed within a timespan)
        -sizeAvg/                   (Percentage of total volume last accessed within a timespan proportional to FS' total)
        -sizeFileAvg/               (Average volume of files last accessed within a timespan)
        
    -chnglogActivity/               (Changelog event counters)
        -ChangelogCount_ATIME       (Access time update)
        -ChangelogCount_CLOSE       (Close file descriptor)
        -ChangelogCount_CREAT       (Regular file creation)
        -ChangelogCount_CTIME       (Creation time update)
        -ChangelogCount_HLINK       (Hard link creation)
        -ChangelogCount_HSM         ()
        -ChangelogCount_LYOUT       (Layout operation)
        -ChangelogCount_MARK        (Internal recordkeeping)
        -ChangelogCount_MIGRT       (File/directory migration)
        -ChangelogCount_MKDIR       (Directory creation)
        -ChangelogCount_MKNOD       (Other file creation)
        -ChangelogCount_MTIME       (Modification time update)
        -ChangelogCount_OPEN        (Open file descriptor)
        -ChangelogCount_RENME       (Rename from)
        -ChangelogCount_RMDIR       (Directory deletion)
        -ChangelogCount_RNMTO       (Rename to)
        -ChangelogCount_SATTR       (Set attribute)
        -ChangelogCount_SLINK       (Soft link creation)
        -ChangelogCount_TRUNC       (Truncate)
        -ChangelogCount_UNLNK       (Regular file removal)
        -ChangelogCount_XATTR       (Set extended attribute)
        
    -creatTempGraph/                (Entries grouped by creation time)
    -dbTempGraph/                   (Entries grouped by database update time)
    -modifTempGraph/                (Entries grouped by modification time)
