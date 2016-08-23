[![Build Status](https://travis-ci.org/percival-detector/percivalui.svg)](https://travis-ci.org/percival-detector/percivalui)
[![Coverage Status](https://coveralls.io/repos/percival-detector/percivalui/badge.svg?branch=master)](https://coveralls.io/r/percival-detector/percivalui?branch=master)
[![Code Health](https://landscape.io/github/percival-detector/percivalui/master/landscape.svg?style=flat)](https://landscape.io/github/percival-detector/percivalui/master)

# Percival UI #

The Percival detector python user interface.

Please see the central user and developer documentation on the [percival-detector github pages](http://percival-detector.github.io)

The percivalui project allow users and detector engineers to control the Percival detector system from a python based user interface. The userinterface is simply a python class where properties and methods can be manipulated to control the detector.


## Dependencies ##

This package is developed with Python 2.7, but with future upgrade to Python 3 in mind. Every git Push is tested using [travis-ci](https://travis-ci.org/percival-detector/percivalui) with Python 3.4.

System dependencies:
* Python (2.7)
* pip - python package manager
* HDF5 libraries (development package)
* ZeroMQ (development package)

Building with setuptools will attempt to use pip to download and install dependencies locally first. The python dependencies are listed in requirements.txt

## Installation ##

Download the sources of this repository using git. If your site network goes through a HTTP(S) proxy server, you may need to set the environment variables http_proxy and https_proxy:

    export http_proxy=mysite.proxy.server:port
    export https_proxy=mysite.proxy.server:port
    
    git clone https://github.com/percival-detector/percivalui.git
    
If you have a github account, you can load your public ssh key into your profile and enjoy key-authenticated, passwordless access (if you later need to push changes up) via the ssh protocol (no proxy environment settings required):

    git@github.com:percival-detector/percivalui.git


Building and installing the sources and scripts can be done with the usual python package build system (i.e. setuptools)
and it is recommended to setup a virtualenv first:

	cd percivalui
	
	# Setup your virtual python environment and activate it
	virtualenv --no-site-packages -p /path/to/python2.7 venv27
	source venv27/bin/activate
	
	# Point to your HDF5 installation if it is not in the system path
	export HDF5_DIR=/path/to/your/hdf5/installation
	
	# Install the python dependencies
	pip install -r requirements.txt
	
	# Run the unittests to ensure everything is setup in the environment
	# there should be no failures/errors reported (tested on Ubuntu Trusty, Precise and RHEL6)
	python setup.py nosetests
	
	# Optionally build the documentation
	python setup.py build_sphinx

Once you have everything working you can build and install the product. While the module is in development it is
recommended to install it into a virtual environment in development mode:

    cd percivalui
    
	# activate your virtual python environment 
	source venv27/bin/activate
    
    python setup.py develop

Updating the sources when the repository has new changes/fixes is then trivial:

    cd percivalui
    
	# activate your virtual python environment 
	source venv27/bin/activate
    
    # Clean up before updating
    python setup.py develop --uninstall
    
    git pull origin
    
    python setup.py develop

## Docs ##

The built documentation will be located in `docs/build/html/index.html`
