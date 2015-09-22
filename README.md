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

Building with setuptools will attempt to use pip to download and install dependencies locally first. The python dependencies are listed in requirements.txt:

* setuptools
* future>=0.14
* numpy>=1.7.0
* h5py>=2.5.0
* nose>=1.3
* coverage

## Installation ##

Download the sources of this repository using git. If your site network goes through a HTTP(S) proxy server, you may need to set the environment variables http_proxy and https_proxy:

    export http_proxy=mysite.proxy.server:port
    export https_proxy=mysite.proxy.server:port
    
    git clone https://github.com/percival-detector/percivalui.git
    
If you have a github account, you can load your public ssh key into your profile and enjoy key-authenticated, passwordless access (if you later need to push changes up) via the ssh protocol (no proxy environment settings required):

    git@github.com:percival-detector/percivalui.git


Building and installing the sources and scripts can be done with the usual python package build system (i.e. setuptools):

	cd percivalui
	
    # Do a local build
    python setup.py build
    
    # Install into the system environment or specify a --prefix
    python setup.py install
    

## Docs ##

Documentation is (optionally) built using Sphinx. If your site uses a http/https proxy server then you may need to set your http_proxy and https_proxy environment variables before building the docs.

Documentation build instructions:

    cd docs/
    make html

The built documentation will be located in `docs/build/html/index.html`
