I   - Compiling
II  - Install
III - Robinhood setup
IV  - First run

I - Compiling
=============

2.1 - From source tarball
-------------------------

It is advised to build RbhMonitoring on your target system, to ensure the best
compatibility with your Lustre and MySQL versions.

Build requirements: python, mysql-python

Unzip and untar the source distribution:
> tar xzvf rbhMonitoring-0.x.x.tar.gz
> cd rbhMonitoring-0.x.x

Build:
> python setup.py sdist

Compiled package is generated in the 'dist/' directory.

2.2 - From git repository
-------------------------

# Install git and autotools stuff:
yum install git automake autoconf libtool

# Retrieve rbhMonitoring sources:
git clone https://github.com/LiquidSame/rbhMonitoring.git
