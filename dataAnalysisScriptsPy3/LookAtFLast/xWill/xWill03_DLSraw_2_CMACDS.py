# -*- coding: utf-8 -*-
"""
descrambled dataset: 
apply ADCcorrection
if requested, apply CMA on Gn0 data
if requested, apply CDS on Gn0 data (otherwise use Smpl data). note that img 0 will be discarded.
save the processed image set

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
#
#
def percDebug_plot_interactive_CDSCMA(data_CDSCMA,data_Gn,mode_str,manyImgFlag):
    (NImg,ignR,ignC)= data_CDSCMA.shape
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
        percDebug_plot_3x2D(data_Gn[thisImg,:,:].astype(float), data_CDSCMA[thisImg,:,:],  APy3_GENfuns.numpy_NaNs((NRow,NCol)),
                            'Gn level',           mode_str+' [ADU]', 'ignore this',
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

dflt_saveFlag_ADU= 'N'
dflt_outFileName_ADU= dflt_mainFolder+'xxx'
#
dflt_CMAFlag= 'Y'
dflt_cols2CMA = '1024:1055' #note this is matlab convention: [1024,1025,...,1055] 
# normally, columns 0:31 would be used as reference columsn for CMA, but we are still unable to read them.
#
dflt_CDSFlag= 'Y'
#
dflt_saveFlag_CDS= 'Y'
dflt_outFileName_CDS= dflt_mainFolder+'dataElaboration_example1_step3_9Img_CMA_CDS.h5'
#
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
    GUIwin_arguments+= ['save ADC-corrected value to h5 file?  [Y/N]'];    GUIwin_arguments+= [str(dflt_saveFlag_ADU)]
    GUIwin_arguments+= ['  if save ADC-corrected: filename for it'];    GUIwin_arguments+= [dflt_outFileName_ADU]
    #
    GUIwin_arguments+= ['apply CMA on Gn0 data [Y/N]'];    GUIwin_arguments+= [str(dflt_CMAFlag)]
    GUIwin_arguments+= ['  if CMA on Gn0: which columns to use as a reference? [first:last]'];    GUIwin_arguments+= [dflt_cols2CMA]
    GUIwin_arguments+= ['apply CDS on Gn0 data [Y/N]'];    GUIwin_arguments+= [str(dflt_CDSFlag)]

    GUIwin_arguments+= ['save CMA,CDS-corrected value to h5 file?  [Y/N]'];    GUIwin_arguments+= [str(dflt_saveFlag_CDS)]
    GUIwin_arguments+= ['  if saveCMA,CDS-corrected: filename for it'];    GUIwin_arguments+= [dflt_outFileName_CDS]
    #
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
    #
    saveFlag_ADU= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    outFileName_ADU= dataFromUser[i_param]; i_param+=1
    #
    CMAFlag=APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    cols2CMA_mtlb= dataFromUser[i_param]; i_param+=1
    if CMAFlag: cols2CMA=APy3_GENfuns.matlabLike_range(cols2CMA_mtlb)
    else: cols2CMA=numpy.array([])    
    CDSFlag=APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    #
    saveFlag_CDS= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    outFileName_CDS= dataFromUser[i_param]; i_param+=1
    #
    cleanMemFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    verboseFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
else:
    file2show= dflt_file2show
    img2proc_str= dflt_img2proc_str
    ADCcor_file= dflt_ADCcor_file
    saveFlag_ADU= APy3_GENfuns.isitYes(dflt_saveFlag_ADU); i_param+=1
    outFileName_ADU= dflt_outFileName_ADU
    #
    CMAFlag=APy3_GENfuns.isitYes(str(dflt_CMAFlag))
    cols2CMA_mtlb= dflt_cols2CMA
    if CMAFlag: cols2CMA=APy3_GENfuns.matlabLike_range(cols2CMA_mtlb)
    else: cols2CMA=numpy.array([])    
    CDSFlag=APy3_GENfuns.isitYes(str(dflt_saveFlag_CDS))
    #
    saveFlag_CDS=APy3_GENfuns.isitYes(str(dflt_saveFlag_CDS))
    outFileName_CDS=dflt_outFileName_CDS
    #
    cleanMemFlag= APy3_GENfuns.isitYes(str(dflt_cleanMemFlag))
    verboseFlag= APy3_GENfuns.isitYes(str(dflt_verboseFlag))
# ---
# what's up doc
if verboseFlag:
    APy3_GENfuns.printcol('will read file {0}'.format(file2show),'blue')
    APy3_GENfuns.printcol('using images {0}'.format(img2proc_str),'blue')
    APy3_GENfuns.printcol('will ADC-correct using ADC param file {0}'.format(ADCcor_file),'blue')
    if saveFlag_ADU: APy3_GENfuns.printcol('will save ADC-corrected to h5 file: '+outFileName_ADU,'blue')
    #
    if CMAFlag: APy3_GENfuns.printcol('will apply CommonModeAveraging (CMA) to Gn0 images, using {0}:{1} as reference columns'.format(cols2CMA[0],cols2CMA[-1]),'blue')
    if CDSFlag: APy3_GENfuns.printcol('will apply CorrelatedDoubleSampling (CDS) to Gn0 images, and use Sample for Gn1/2 images','blue')
    else: APy3_GENfuns.printcol('will use Sample for Gn0/1/2 images','blue')
    #
    if saveFlag_CDS:  APy3_GENfuns.printcol('will save CDS,CMA-corrected to h5 file: '+outFileName_CDS,'blue')
    #
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
# interactive show for ADU values
#if verboseFlag:  APy3_GENfuns.printcol('interactive plot','blue')
#percDebug_plot_interactive_ADCcorr(data_ADU,data_Gn2show,False )
#---
if saveFlag_ADU: 
    APy3_GENfuns.printcol('saving ADC-corrected to h5 file','blue')
    APy3_GENfuns.write_2xh5(outFileName_ADU, data_ADU[:,iSmpl,:,:], '/data/', data_ADU[:,iRst,:,:], '/reset/')
    APy3_GENfuns.printcol('ADC-corrected values saved in '+outFileName_ADU,'green')
#---
data_CMACDS= APy3_GENfuns.numpy_NaNs((NImg,NRow,NCol)) # note that this is NImg, but in the end the 1st img will be discarded, and the array will be reduced to (NImg-1)
#
for thisGn in range(3):
    if verboseFlag: APy3_GENfuns.printcol('checking data Gn{0}'.format(thisGn),'green')
    data_ADU_xGn= numpy.copy(data_ADU)
    GnX_map= data_Gn[:,:,:]==thisGn
    data_ADU_xGn[:,iSmpl,:,:][~GnX_map]= numpy.NaN
    #
    data_CDS_xGn= APy3_GENfuns.numpy_NaNs((NImg,NRow,NCol)) # note that this is NImg, but in the end the 1st img will be discarded
    #
    if thisGn==0:
        mode_str=""
        if CMAFlag:
            if verboseFlag: APy3_GENfuns.printcol('  CMA-ing','blue')
            data_ADU_xGn[:,iSmpl,:,:]= APy3_P2Mfuns.CMA(data_ADU_xGn[:,iSmpl,:,:] ,cols2CMA)
            data_ADU_xGn[:,iRst,:,:]=  APy3_P2Mfuns.CMA(data_ADU_xGn[:,iRst,:,:]  ,cols2CMA)
            data_ADU_xGn[:,:,:,(cols2CMA[0]):(cols2CMA[1]+1)]=numpy.NaN # delete the cols used as a reference
            mode_str+="CMA,"
        #
        if CDSFlag: 
            if verboseFlag: APy3_GENfuns.printcol('  CDS-ing Gn0','blue')
            data_CDS_xGn[1:,:,:]= APy3_P2Mfuns.CDS(data_ADU_xGn)
            mode_str+='CDS'
        else: 
            if verboseFlag: APy3_GENfuns.printcol('  using Smpl for Gn0','blue')
            data_CDS_xGn[1:,:,:]= data_ADU_xGn[1:,iSmpl,:,:]
            mode_str+='Smpl'
            #
    else:
        if verboseFlag: APy3_GENfuns.printcol('  using Smpl for Gn1/2','blue')
        data_CDS_xGn[1:,:,:]= data_ADU_xGn[1:,iSmpl,:,:]
    data_CMACDS[GnX_map]= data_CDS_xGn[GnX_map]
    #
    if cleanMemFlag: del data_CDS_xGn; del data_ADU_xGn; del GnX_map
#
data_CMACDS=  data_CMACDS[1:,:,:] # discard 1st img, which is NAN anyway (useless, as it is saturated)
data_Gn2show= data_Gn2show[1:,:,:] # discard 1st img, which is NAN anyway (useless, as it is saturated)
#---
# interactive show for CMA,CDS values
if verboseFlag:  APy3_GENfuns.printcol('interactive plot','blue')
percDebug_plot_interactive_CDSCMA(data_CMACDS,data_Gn2show,mode_str,
                                False #manyImgFlag
                                )
#---
if saveFlag_CDS: 
    APy3_GENfuns.printcol('saving CMA,CDS-corrected to h5 file','blue')
    APy3_GENfuns.write_1xh5(outFileName_CDS, data_CMACDS, '/data/data/')
    APy3_GENfuns.printcol('CMA,CDS-corrected values saved in '+outFileName_CDS,'green')
#---
# that's all folks
if verboseFlag:  
    for i_aux in range(3): APy3_GENfuns.printcol('---------','blue')



