# -*- coding: utf-8 -*-
"""
visualize small descrambled dataset

# load environment python3 environment on cfeld-percival02
source /home/prcvlusr/PercAuxiliaryTools/Anaconda3/Anaconda3/bin/activate root
# or load environment on maxwell
source /usr/share/Modules/init/sh
module load anaconda/3

python3 ./xxx.py
or:
start python
# execfile("xxx.py") # this is in python 2.7
exec(open("./xxx.py").read()); print('Python3 is horrible')
"""

#%% imports and useful constants
from APy3_auxINIT import *
numpy.seterr(divide='ignore', invalid='ignore')
# ---
# 
def percDebug_plot_interactive_base(data_GnCrsFn,manyImgFlag):
    (NImg,ignSR,ignR,ignC,ign3)= data_GnCrsFn.shape
    thisImg=-1
    APy3_GENfuns.printcol("[number] of raw image / [N]ext raw image / [P]revious raw image / [E]nd", 'black')
    if manyImgFlag: nextstep = input()
    else: nextstep = APy3_GENfuns.press_any_key()
    #
    while nextstep not in ['e','E','q','Q']:
        matplotlib.pyplot.close()
        #
        if nextstep in ['n','N', ' ']: thisImg+=1
        elif nextstep in ['p','P']: thisImg-=1
        elif nextstep.isdigit(): thisImg= int(nextstep); 
        #
        if (thisImg>=NImg): thisImg= thisImg%NImg
        if (thisImg<0): thisImg= thisImg%NImg
        APy3_GENfuns.printcol("showing Raw: Img {0}, close image to move on".format(thisImg), 'black')
        #
        aux_title = "Img " + str(thisImg)
        aux_err_below = -0.1
        APy3_P2Mfuns.percDebug_plot_6x2D(data_GnCrsFn[thisImg,iSmpl,:,:,iGn],data_GnCrsFn[thisImg,iSmpl,:,:,iCrs],data_GnCrsFn[thisImg,iSmpl,:,:,iFn],
                                data_GnCrsFn[thisImg,iRst,:,:,iGn], data_GnCrsFn[thisImg,iRst,:,:,iCrs], data_GnCrsFn[thisImg,iRst,:,:,iFn],
                                aux_title, aux_err_below)
        matplotlib.pyplot.show(block=True) # to allow for interactive zoom
        #
        APy3_GENfuns.printcol("[number] of raw image / [N]ext raw image / [P]revious raw image / [E]nd", 'black')
        if manyImgFlag: nextstep = input()
        else: nextstep = APy3_GENfuns.press_any_key()
        if nextstep in ['e','E','q','Q']: APy3_GENfuns.printcol("end plotting", 'blue') 
    return
#---
interactiveFlag= False; interactiveFlag= True
# ---
#
#%% parameters
dflt_file2show='/gpfs/cfel/fsds/labs/percival/2019/experiment/20191210_000_Petra3_P04_JPLBSI04/processed/2019.12.11.15.23_first_5um_pinhole/examplesForWill/2020.01.xx_dataElaboration/'+'dataElaboration_example1_step1_10Img_DLSraw.h5'
dflt_img2proc_str= ":" # using the sensible matlab convention; "all",":","*" means all
dflt_cleanMemFlag= 'Y'
dflt_verboseFlag= 'Y'
#---
#%% parameter loading
if interactiveFlag:
    # interactive GUI
    GUIwin_arguments= []
    GUIwin_arguments+= ['file to show'];         GUIwin_arguments+= [dflt_file2show] 
    GUIwin_arguments+= ['images [first:last]'];  GUIwin_arguments+= [dflt_img2proc_str]
    GUIwin_arguments+= ['clean mem when possible [Y/N]'];  GUIwin_arguments+= [str(dflt_cleanMemFlag)]
    GUIwin_arguments+= ['verbose? [Y/N]'];                 GUIwin_arguments+= [str(dflt_verboseFlag)]
    #
    GUIwin_arguments=tuple(GUIwin_arguments)
    dataFromUser= APy3_GENfuns.my_GUIwin_text(GUIwin_arguments)
    #
    i_param=0
    file2show= dataFromUser[i_param]; i_param+=1
    img2proc_str= dataFromUser[i_param]; i_param+=1
    cleanMemFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    verboseFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
else:
    file2show= dflt_file2show
    img2proc_str= dflt_img2proc_str
    cleanMemFlag= APy3_GENfuns.isitYes(str(dflt_cleanMemFlag))
    verboseFlag= APy3_GENfuns.isitYes(str(dflt_verboseFlag))
# ---
# what's up doc
if verboseFlag:
    APy3_GENfuns.printcol('will read file {0}'.format(file2show),'blue')
    APy3_GENfuns.printcol('using images {0}'.format(img2proc_str),'blue')
    if cleanMemFlag: APy3_GENfuns.printcol('will clean mem when possible','blue')
    APy3_GENfuns.printcol('verbose','blue')
    APy3_GENfuns.printcol('-','blue')
# ---
# load
if APy3_GENfuns.notFound(file2show): APy3_GENfuns.printErr('not found: '+file2show)
if verboseFlag:  APy3_GENfuns.printcol('reading all images from file'.format(img2proc_str),'blue')
if img2proc_str in APy3_GENfuns.ALLlist: 
    (inSmpl,inRst)= APy3_GENfuns.read_2xh5(file2show, '/data/', '/reset/')
else:
    aux_img2proc= APy3_GENfuns.matlab_like_range(img2proc_str)
    (inSmpl,inRst)= APy3_GENfuns.read_partial_2xh5(file2show, '/data/', '/reset/', aux_img2proc[0], aux_img2proc[-1])
(NImg,ignNRow,ignNCol)= inSmpl.shape
if verboseFlag: APy3_GENfuns.printcol('{0} image read from file'.format(NImg),'green')
# ---
# DLSraw => GnCrsFn
data_GnCrsFn= APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(inSmpl,inRst, APy3_P2Mfuns.ERRDLSraw,APy3_P2Mfuns.ERRint16)
# APy3_P2Mfuns.ERRDLSraw, (=> ERRint16) is a number that cannot come from the chip. it is used to tag packages not received 
if cleanMemFlag: del inSmpl; del inRst
# ---
# interactive show
if verboseFlag:  APy3_GENfuns.printcol('interactive plot','blue')
percDebug_plot_interactive_base(data_GnCrsFn,
                                False #manyImgFlag
                                )
#---
# that's all folks
if verboseFlag:  
    for i_aux in range(3): APy3_GENfuns.printcol('---------','blue')



