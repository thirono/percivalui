[![Build Status](https://travis-ci.org/percival-detector/percivalui.svg)](https://travis-ci.org/percival-detector/percivalui)
[![Coverage Status](https://coveralls.io/repos/percival-detector/percivalui/badge.svg?branch=master)](https://coveralls.io/r/percival-detector/percivalui?branch=master)

# Percival UI #

The Percival detector python user interface.

Please see the central user and developer documentation on the [percival-detector github pages](http://percival-detector.github.io)

## Introduction ##

The percivalui project allow users and detector engineers to control the Percival detector system from a python based user interface. The userinterface is simply a python class where properties and methods can be manipulated to control the detector.

The project is currently in early development stages. First goal is to produce a mock-up which will provide the user-interface without controlling any real hardware.

## Installation ##

This is a python module in development. While the development is ongoing the recommended setup is simply to run the python interpreter inside the top-level directory alongside the source packages.

## Dependencies ##
* Python 2.7

Documentation is built using Sphinx. If your site uses a http/https proxy server
then you may need to set your http_proxy and https_proxy environment variables
before building the docs.

Documentation build instructions:

    cd docs/
    make html

The built documentation will be located in `docs/build/html/index.html`
