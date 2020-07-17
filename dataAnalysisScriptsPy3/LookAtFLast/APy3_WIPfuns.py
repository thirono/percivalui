# -*- coding: utf-8 -*-
"""
general functions and fitting
(a half-decent language would have those functions already). Python is worth what it costs.
"""
#%% imports
#
import sys # command line argument, print w/o newline, version
import time # to have time
import numpy
from scipy import stats # linear regression
from scipy.optimize import curve_fit # non-linear fit
import math
import scipy
import matplotlib
import matplotlib.pyplot
matplotlib.pyplot.rcParams['image.cmap'] = 'jet'
import os # list files in a folder
import glob # to find last file
import re # to sort naturally
import h5py # deal with HDF5
import tkinter
#
import ast # execute command
import collections # len(collections.Counter(A).keys()) n of distinct
#
from mpl_toolkits.mplot3d import Axes3D
#
#
#
#%% constant
VERYBIGNUMBER= 1e18
#


    Xvect=numpy.arange(Nx)
    Xsurf, Ysurf = numpy.meshgrid(Xvect,Yvect)
    Zsurf = array2D.reshape(Xsurf.shape)
    #
    # plot_surface is a mess: the only way to limit z axis is clipping data
    Zsurf[Zsurf<Zaxmin]= numpy.nan
    # plot_surface is a mess: the only way to logscale z data is to numpy.log10 it and adjust the ticks
    def log_tick_formatter(val, pos=None):
        return "{:.1e}".format(10**val)
    if logScaleFlag: 
        surf = ax.plot_surface(Xsurf, Ysurf, numpy.log10(Zsurf), vmin=Zaxmin, facecolors=matplotlib.pyplot.cm.jet(numpy.log10(Zsurf)/numpy.nanmax(numpy.log10(Zsurf))), linewidth=0.1, antialiased=False, shade=False)
        #surf = ax.plot_surface(Xsurf, Ysurf, numpy.log10(Zsurf), vmin=Zaxmin, linewidth=0.1, antialiased=False, shade=False)
        ax.zaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    else: surf = ax.plot_surface(Xsurf, Ysurf, Zsurf, vmin=Zaxmin, facecolors=matplotlib.pyplot.cm.jet(Zsurf/numpy.nanmax(Zsurf)), linewidth=0.1, antialiased=False, shade=False)
    #
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    matplotlib.pyplot.title(label_title)
    if (invertx_flag==True): matplotlib.pyplot.gca().invert_xaxis();
    #
    matplotlib.pyplot.show(block=False)
    return (fig)
###########################################
import matplotlib
import matplotlib.cm as cmx
from mpl_toolkits.mplot3d import Axes3D
def scatter3d(x,y,z, cs, colorsMap='jet'):
    cm = plt.get_cmap(colorsMap)
    cNorm = matplotlib.colors.Normalize(vmin=min(cs), vmax=max(cs))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(x, y, z, c=scalarMap.to_rgba(cs))
    scalarMap.set_array(cs)
    fig.colorbar(scalarMap)
    plt.show()

#x = np.random.rand(30)
#y = np.random.rand(30)
#z = np.random.rand(30)
#scatter3d(x,y,z, z, colorsMap='jet')
