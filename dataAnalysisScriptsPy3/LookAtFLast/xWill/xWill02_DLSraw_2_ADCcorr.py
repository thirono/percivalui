# -*- coding: utf-8 -*-
"""
descrambled dataset => apply ADCcorrection

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
NRow= APy3_P2Mfuns.NRow
NCol= APy3_P2Mfuns.NCol
#
# ---
def percDebug_plot_3x2D(ShtLeft,ShtCenter,ShtRight, label_titleLeft,label_titleCenter,label_titleRight,label_titleAll):  
    ''' plot Gn, Smpl(ADU) & Rst(ADU) img''' 
    cmap = matplotlib.pyplot.cm.jet
    fig = matplotlib.pyplot.figure()
    fig.canvas.set_window_title(label_titleAll)
    label_x="col"; label_y="row"
    #
    matplotlib.pyplot.subplot(1,3,1); 
    matplotlib.pyplot.imshow(ShtLeft, interpolation='none', cmap=cmap,)
    matplotlib.pyplot.title(label_titleLeft)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y) 
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();   
    #
    matplotlib.pyplot.subplot(1,3,2); 
    matplotlib.pyplot.imshow(ShtCenter, interpolation='none', cmap=cmap)
    matplotlib.pyplot.title(label_titleCenter)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();  
    #
    matplotlib.pyplot.subplot(1,3,3); 
    matplotlib.pyplot.imshow(ShtRight, interpolation='none', cmap=cmap)
    matplotlib.pyplot.title(label_titleRight)
    matplotlib.pyplot.xlabel(label_x)
    matplotlib.pyplot.ylabel(label_y)
    matplotlib.pyplot.colorbar()
    matplotlib.pyplot.gca().invert_xaxis();
    #
    matplotlib.pyplot.show(block=False)
    return fig
#
def percDebug_plot_interactive_ADCcorr(data_ADU,data_Gn,manyImgFlag):
    (NImg,ignSR,ignR,ignC)= data_ADU.shape
    thisImg=-1
    APy3_GENfuns.printcol("[number] of image / [N]ext image / [P]revious image / [E]nd plotting", 'black')
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
        APy3_GENfuns.printcol("showing ADC-corrected: Img {0}, close image to move on".format(thisImg), 'black')
        #
        aux_title = "Img " + str(thisImg)
        percDebug_plot_3x2D(data_Gn[thisImg,:,:].astype(float), data_ADU[thisImg,iSmpl,:,:],  data_ADU[thisImg,iRst,:,:],
                            'Gn level',           'ADC-corrected Sample [ADU]', 'ADC-corrected Reset [ADU]',
                            aux_title)
        matplotlib.pyplot.show(block=True) # to allow for interactive zoom
        #
        APy3_GENfuns.printcol("[number] of image / [N]ext image / [P]revious image / [E]nd plotting", 'black')
        if manyImgFlag: nextstep = input()
        else: nextstep = APy3_GENfuns.press_any_key()
        if nextstep in ['e','E','q','Q']: APy3_GENfuns.printcol("end plotting", 'blue') 
    return
# ---
interactiveFlag= False; interactiveFlag= True
# ---
#
#%% parameters
dflt_mainFolder= '/gpfs/cfel/fsds/labs/percival/2019/experiment/20191210_000_Petra3_P04_JPLBSI04/processed/2019.12.11.15.23_first_5um_pinhole/examplesForWill/2020.01.xx_dataElaboration/'
dflt_file2show= dflt_mainFolder+'dataElaboration_example1_step1_10Img_DLSraw.h5'
dflt_img2proc_str= ":" # using the sensible matlab convention; "all",":","*" means all
dflt_ADCcor_file= dflt_mainFolder+'BSI04_Tminus20_dmuxSELsw_2019.11.20_ADCcor.h5'
dflt_saveFlag= 'Y'
dflt_outFileName_ADU= dflt_mainFolder+'dataElaboration_example1_step2_10Img_ADU.h5'
dflt_cleanMemFlag= 'Y'
dflt_verboseFlag= 'Y'
#---
#%% parameter loading
if interactiveFlag:
    # interactive GUI
    GUIwin_arguments= []
    GUIwin_arguments+= ['file to show'];         GUIwin_arguments+= [dflt_file2show] 
    GUIwin_arguments+= ['images [first:last]'];  GUIwin_arguments+= [dflt_img2proc_str]
    GUIwin_arguments+= ['ADC correction (Smpl/Rst,Crs/Fn,slope/offset): file'];    GUIwin_arguments+= [dflt_ADCcor_file]
    GUIwin_arguments+= ['save ADC-corrected value to h5 file  [Y/N]'];    GUIwin_arguments+= [str(dflt_saveFlag)]
    GUIwin_arguments+= ['  if save: filename'];    GUIwin_arguments+= [dflt_outFileName_ADU]
    GUIwin_arguments+= ['clean mem when possible [Y/N]'];  GUIwin_arguments+= [str(dflt_cleanMemFlag)]
    GUIwin_arguments+= ['verbose? [Y/N]'];                 GUIwin_arguments+= [str(dflt_verboseFlag)]
    #
    GUIwin_arguments=tuple(GUIwin_arguments)
    dataFromUser= APy3_GENfuns.my_GUIwin_text(GUIwin_arguments)
    #
    i_param=0
    file2show= dataFromUser[i_param]; i_param+=1
    img2proc_str= dataFromUser[i_param]; i_param+=1
    ADCcor_file= dataFromUser[i_param]; i_param+=1
    saveFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    outFileName_ADU= dataFromUser[i_param]; i_param+=1
    cleanMemFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    verboseFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
else:
    file2show= dflt_file2show
    img2proc_str= dflt_img2proc_str
    ADCcor_file= dflt_ADCcor_file
    saveFlag= APy3_GENfuns.isitYes(dflt_saveFlag); i_param+=1
    outFileName_ADU= dflt_outFileName_ADU
    cleanMemFlag= APy3_GENfuns.isitYes(str(dflt_cleanMemFlag))
    verboseFlag= APy3_GENfuns.isitYes(str(dflt_verboseFlag))
# ---
# what's up doc
if verboseFlag:
    APy3_GENfuns.printcol('will read file {0}'.format(file2show),'blue')
    APy3_GENfuns.printcol('using images {0}'.format(img2proc_str),'blue')
    APy3_GENfuns.printcol('will ADC-correct using ADC param file {0}'.format(ADCcor_file),'blue')
    if saveFlag: APy3_GENfuns.printcol('will save ADC-corrected to h5 file: '+outFileName_ADU,'blue')
    if cleanMemFlag: APy3_GENfuns.printcol('will clean mem when possible','blue')
    APy3_GENfuns.printcol('verbose','blue')
    APy3_GENfuns.printcol('-','blue')
# ---
# load
if APy3_GENfuns.notFound(ADCcor_file): APy3_GENfuns.printErr('not found: '+ADCcor_file)
(ADCparam_Smpl_crs_slope,ADCparam_Smpl_crs_offset, ADCparam_Smpl_fn_slope,ADCparam_Smpl_fn_offset,
 ADCparam_Rst_crs_slope, ADCparam_Rst_crs_offset,  ADCparam_Rst_fn_slope, ADCparam_Rst_fn_offset)= APy3_P2Mfuns.read_ADUh5(ADCcor_file)
#
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
if cleanMemFlag: del inSmpl; del inRst
(NImg,auxNSR,auxNRow,auxNCol,ignGCF)= data_GnCrsFn.shape
data_ADU= APy3_GENfuns.numpy_NaNs((NImg,auxNSR,auxNRow,auxNCol))
data_ADU[:,iSmpl,:,:]= APy3_P2Mfuns.ADCcorr_NoGain(data_GnCrsFn[:,iSmpl,:,:,iCrs],data_GnCrsFn[:,iSmpl,:,:,iFn],
                                          ADCparam_Smpl_crs_slope,ADCparam_Smpl_crs_offset,
                                          ADCparam_Smpl_fn_slope,ADCparam_Smpl_fn_offset, NRow,NCol) # Smpl            
data_ADU[:,iRst,:,:]=  APy3_P2Mfuns.ADCcorr_NoGain(data_GnCrsFn[:,iRst,:,:,iCrs],data_GnCrsFn[:,iRst,:,:,iFn],
                                          ADCparam_Rst_crs_slope,ADCparam_Rst_crs_offset,
                                          ADCparam_Rst_fn_slope,ADCparam_Rst_fn_offset, NRow,NCol) # Rst
data_Gn= numpy.copy(data_GnCrsFn[:,iSmpl,:,:,iGn])
#
# APy3_P2Mfuns.ERRDLSraw, (=> ERRint16) is a number that cannot come from the chip. it is used to tag packages not received 
aux_badMap= data_GnCrsFn[:,iSmpl,:,:,iGn]==APy3_P2Mfuns.ERRint16
data_ADU[:,iSmpl,:,:][aux_badMap]= numpy.NaN
data_Gn2show= numpy.copy(data_Gn).astype(float)
data_Gn2show[aux_badMap]= numpy.NaN
aux_badMap= data_GnCrsFn[:,iRst,:,:,iGn]==APy3_P2Mfuns.ERRint16
data_ADU[:,iRst,:,:][aux_badMap]= numpy.NaN
#
if cleanMemFlag: del data_GnCrsFn; del aux_badMap
# ---
# interactive show
if verboseFlag:  APy3_GENfuns.printcol('interactive plot','blue')
percDebug_plot_interactive_ADCcorr(data_ADU,data_Gn2show,
                                False #manyImgFlag
                                )
#---
if saveFlag: 
    APy3_GENfuns.printcol('saving ADC-corrected to h5 file','blue')
    APy3_GENfuns.write_2xh5(outFileName_ADU, data_ADU[:,iSmpl,:,:], '/data/', data_ADU[:,iRst,:,:], '/reset/')
    APy3_GENfuns.printcol('ADC-corrected values saved in '+outFileName_ADU,'green')
#---
# that's all folks
if verboseFlag:  
    for i_aux in range(3): APy3_GENfuns.printcol('---------','blue')



