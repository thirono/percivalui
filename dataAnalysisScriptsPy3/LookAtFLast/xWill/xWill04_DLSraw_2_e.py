# -*- coding: utf-8 -*-
"""
descrambled dataset: 
apply ADCcorrection
if requested, apply CMA on Gn0 data
if requested, apply CDS on Gn0 data (otherwise use Smpl data). note that img 0 will be discarded
subtract pedestal & apply Gn multiplication (Lateral Overflow)
save the processed image set (data in e)

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
#
def percDebug_plot_interactive_e_nd_Gn(data_e,data_Gn,mode_str,manyImgFlag):
    (NImg,ignR,ignC)= data_e.shape
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
        aux_fig= APy3_GENfuns.plot_2x2D(data_e[thisImg,:,:], data_Gn[thisImg,:,:].astype(float), 
                               True, False,
                               'row', 'col',
                               mode_str+' [e]','Gn level',
                               True)
        aux_fig.canvas.set_window_title('Img {0}'.format(thisImg))
        APy3_GENfuns.showIt() # to allow for interactive zoom
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
dflt_file2show= dflt_mainFolder+'dataElaboration_example2_step1_2Img_DLSraw.h5'
dflt_img2proc_str= ":" # using the sensible matlab convention; "all",":","*" means all
dflt_ADCcor_file= dflt_mainFolder+'BSI04_Tminus20_dmuxSELsw_2019.11.20_ADCcor.h5'
dflt_multiGnCal_file=dflt_mainFolder+'BSI04_Tm20_dmuxSELHi_biasBSI04_04_PGABBB_2019.12.02_Gn012_MultiGnCal.h5'
#
dflt_alternFile_Ped_Gn0_ADU= dflt_mainFolder+"2019.12.11.22.54.45_BSI04_7of7_3GPGABBB_120ms_0399eV_5um_1kdrk_Gn0_CDS_avg.h5" 
#
dflt_CMAFlag= 'Y'
dflt_cols2CMA = '1152:1183' #note this is matlab convention: [1024,1025,...,1055] 
# normally, columns 0:31 would be used as reference columsn for CMA, but we are still unable to read them.
#
dflt_CDSFlag= 'Y'
#
dflt_saveFlag_e= 'Y'
dflt_outFileName_e= dflt_mainFolder+'dataElaboration_example2_step4_1Img_e.h5'
#
dflt_highMemFlag='Y'
dflt_cleanMemFlag= 'Y'
dflt_verboseFlag= 'Y'
#---
#%% parameter loading
if interactiveFlag:
    # interactive GUI
    GUIwin_arguments= []
    GUIwin_arguments+= ['file to show'];         GUIwin_arguments+= [dflt_file2show] 
    GUIwin_arguments+= ['images [first:last]'];  GUIwin_arguments+= [dflt_img2proc_str]
    GUIwin_arguments+= ['ADC correction (Smpl/Rst,Crs/Fn,slope/offset): file'];      GUIwin_arguments+= [dflt_ADCcor_file]
    GUIwin_arguments+= ['Lateral Overflow (pedestal & e/ADU for Gn0/1/2): file'];    GUIwin_arguments+= [dflt_multiGnCal_file]
    GUIwin_arguments+= ['PedestalADU [Gn0] file [none not to use it]'];              GUIwin_arguments+= [dflt_alternFile_Ped_Gn0_ADU]
    #
    GUIwin_arguments+= ['apply CMA on Gn0 data [Y/N]'];    GUIwin_arguments+= [str(dflt_CMAFlag)]
    GUIwin_arguments+= ['  if CMA on Gn0: which columns to use as a reference? [first:last]'];    GUIwin_arguments+= [dflt_cols2CMA]
    GUIwin_arguments+= ['apply CDS on Gn0 data [Y/N]'];    GUIwin_arguments+= [str(dflt_CDSFlag)]

    GUIwin_arguments+= ['save Lateral Overflow values (in electrons) to h5 file?  [Y/N]'];    GUIwin_arguments+= [str(dflt_saveFlag_e)]
    GUIwin_arguments+= ['  if saveLatOvflw: filename for it'];    GUIwin_arguments+= [dflt_outFileName_e]
    #
    GUIwin_arguments+= ['high mem usage? [Y/N]'];          GUIwin_arguments+= [str(dflt_highMemFlag)] 
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
    multiGnCal_file= dataFromUser[i_param]; i_param+=1
    #
    alternFile_Ped_Gn0_ADUFile= dataFromUser[i_param]; i_param+=1; 
    if alternFile_Ped_Gn0_ADUFile in APy3_GENfuns.NOlist: flagUseAlternPed=False
    else: flagUseAlternPed=True
    #
    CMAFlag=APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    cols2CMA_mtlb= dataFromUser[i_param]; i_param+=1
    if CMAFlag: cols2CMA=APy3_GENfuns.matlabLike_range(cols2CMA_mtlb)
    else: cols2CMA=numpy.array([])    
    CDSFlag=APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    #
    saveFlag_e= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    outFileName_e= dataFromUser[i_param]; i_param+=1
    #
    highMemFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    cleanMemFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
    verboseFlag= APy3_GENfuns.isitYes(dataFromUser[i_param]); i_param+=1
else:
    file2show= dflt_file2show
    img2proc_str= dflt_img2proc_str
    ADCcor_file= dflt_ADCcor_file
    multiGnCal_file= dflt_multiGnCal_file
    #
    alternFile_Ped_Gn0_ADUFile= dflt_alternFile_Ped_Gn0_ADUFile
    if alternFile_Ped_Gn0_ADUFile in APy3_GENfuns.NOlist: flagUseAlternPed=False
    else: flagUseAlternPed=True
    #
    CMAFlag=APy3_GENfuns.isitYes(str(dflt_CMAFlag))
    cols2CMA_mtlb= dflt_cols2CMA
    if CMAFlag: cols2CMA=APy3_GENfuns.matlabLike_range(cols2CMA_mtlb)
    else: cols2CMA=numpy.array([])    
    CDSFlag=APy3_GENfuns.isitYes(str(dflt_saveFlag_CDS))
    #
    saveFlag_eS=APy3_GENfuns.isitYes(str(dflt_saveFlag_e))
    outFileName_e=dflt_outFileName_e
    #
    highMemFlag= dflt_highMemFlag
    cleanMemFlag= APy3_GENfuns.isitYes(str(dflt_cleanMemFlag))
    verboseFlag= APy3_GENfuns.isitYes(str(dflt_verboseFlag))
# ---
# what's up doc
if verboseFlag:
    APy3_GENfuns.printcol('will read file {0}'.format(file2show),'blue')
    APy3_GENfuns.printcol('  using images: {0}'.format(img2proc_str),'blue')
    APy3_GENfuns.printcol('will ADC-correct using ADC param file {0}'.format(ADCcor_file),'blue')
    APy3_GENfuns.printcol('will apply Gn multiplication using Lateral-OverFlow param file {0}'.format(multiGnCal_file),'blue')
    if flagUseAlternPed: APy3_GENfuns.printcol('will take Gn0 Pedestal from {0}'.format(alternFile_Ped_Gn0_ADUFile),'blue')
    else: APy3_GENfuns.printcol('will use Gn0 pedestal from multiGnCal_file','blue')
    #
    if CMAFlag: APy3_GENfuns.printcol('will apply CommonModeAveraging (CMA) to Gn0 images, using {0}:{1} as reference columns'.format(cols2CMA[0],cols2CMA[-1]),'blue')
    if CDSFlag: APy3_GENfuns.printcol('will apply CorrelatedDoubleSampling (CDS) to Gn0 images, and use Sample for Gn1/2 images','blue')
    else: APy3_GENfuns.printcol('will use Sample for Gn0/1/2 images','blue')
    #
    if saveFlag_e:  APy3_GENfuns.printcol('will save Lateral-Overflow-calibrated results (in electrons) to h5 file: '+outFileName_e,'blue')
    #
    if highMemFlag: APy3_GENfuns.printcol('will maximize speed by elaborating many img in parallel','blue') 
    else: APy3_GENfuns.printcol('will minimize RAM by elaborating 2 img ata a time','blue') 
    if cleanMemFlag: APy3_GENfuns.printcol('will clean mem when possible','blue')
    APy3_GENfuns.printcol('verbose','blue')
    APy3_GENfuns.printcol('-','blue')

# ---
# load
if APy3_GENfuns.notFound(ADCcor_file): APy3_GENfuns.printErr('not found: '+ADCcor_file)
(ADCparam_Smpl_crs_slope,ADCparam_Smpl_crs_offset, ADCparam_Smpl_fn_slope,ADCparam_Smpl_fn_offset,
 ADCparam_Rst_crs_slope, ADCparam_Rst_crs_offset,  ADCparam_Rst_fn_slope, ADCparam_Rst_fn_offset)= APy3_P2Mfuns.read_ADUh5(ADCcor_file)
#
if APy3_GENfuns.notFound(multiGnCal_file): APy3_GENfuns.printErr('not found: '+multiGnCal_file)
(PedestalADU_multiGn,e_per_ADU_multiGn)= APy3_GENfuns.read_2xh5(multiGnCal_file, '/Pedestal_ADU/', '/e_per_ADU/')
#
if flagUseAlternPed:
    if APy3_GENfuns.notFound(alternFile_Ped_Gn0_ADUFile): APy3_GENfuns.printErr('not found: '+ alternFile_Ped_Gn0_ADUFile)
    PedestalADU_multiGn[0,:,:]= APy3_GENfuns.read_1xh5(alternFile_Ped_Gn0_ADUFile, '/data/data/')
#
if APy3_GENfuns.notFound(file2show): APy3_GENfuns.printErr('not found: '+file2show)
if verboseFlag:  APy3_GENfuns.printcol('reading images from file'.format(img2proc_str),'blue')
if img2proc_str in APy3_GENfuns.ALLlist: 
    (inSmpl,inRst)= APy3_GENfuns.read_2xh5(file2show, '/data/', '/reset/')
else:
    aux_img2proc= APy3_GENfuns.matlab_like_range(img2proc_str)
    (inSmpl,inRst)= APy3_GENfuns.read_partial_2xh5(file2show, '/data/', '/reset/', aux_img2proc[0], aux_img2proc[-1])
(NImg,ignNRow,ignNCol)= inSmpl.shape
if verboseFlag: APy3_GENfuns.printcol('{0} image read from file'.format(NImg),'green')
# ---
if verboseFlag: APy3_GENfuns.printcol("elaborating DLSraw file", 'blue')
data_e= APy3_P2Mfuns.convert_DLSraw_2_e_wLatOvflw(inSmpl,inRst, CDSFlag, CMAFlag,cols2CMA,
                                                ADCparam_Smpl_crs_slope,ADCparam_Smpl_crs_offset,ADCparam_Smpl_fn_slope,ADCparam_Smpl_fn_offset,
                                                ADCparam_Rst_crs_slope,ADCparam_Rst_crs_offset,ADCparam_Rst_fn_slope,ADCparam_Rst_fn_offset,
                                                PedestalADU_multiGn,e_per_ADU_multiGn,
                                                highMemFlag,cleanMemFlag,verboseFlag)
# ---
# this is just to allow you to see Gn values, it might be skipped otherwise
# DLSraw => GnCrsFn
if highMemFlag: data_GnCrsFn= APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(inSmpl,inRst, APy3_P2Mfuns.ERRDLSraw,APy3_P2Mfuns.ERRint16)
else:
    (NImg, ignNRow,ignNCol)= inSmpl.shape
    data_GnCrsFn= numpy.zeros((NImg,APy3_P2Mfuns.NSmplRst,APy3_P2Mfuns.NRow,NCol,APy3_P2Mfuns.NGnCrsFn), dtype='int16')
    for thisImg in range(NImg):
        thisSmpl_DLSraw= inSmpl[thisImg,:,:].reshape((1, NRow,NCol))
        thisRst_DLSraw=  inRst_DLSraw[thisImg,:,: ].reshape((1, NRow,NCol))
        this_dscrmbld_GnCrsFn= APy3_P2Mfuns.convert_DLSraw_2_GnCrsFn(thisSmpl_DLSraw,thisRst_DLSraw, ERRDLSraw,ERRint16)
        dscrmbld_GnCrsFn[thisImg,:, :,:, :]= this_dscrmbld_GnCrsFn[0,:, :,:, :]    
        if verboseFlag: APy3_GENfuns.dot_every10th(thisImg,NImg)
        del thisSmpl_DLSraw; del thisRst_DLSraw; del this_dscrmbld_GnCrsFn
#
aux_badMap= data_GnCrsFn[1:,iSmpl,:,:,iGn]==APy3_P2Mfuns.ERRint16
data_Gn2show= data_GnCrsFn[1:,iSmpl,:,:,iGn].astype(float) # also Gn[i+1] refers to Smpl[i+1] => refers to CDS[i]
data_Gn2show[aux_badMap]= numpy.NaN
if cleanMemFlag: del inSmpl; del inRst
#---
# interactive show for e (& Gn) values
mode_str=''
if CMAFlag: mode_str+="CMA,"
if CDSFlag: mode_str+='CDS'
else: mode_str+='Smpl'
if verboseFlag:  APy3_GENfuns.printcol('interactive plot','blue')
percDebug_plot_interactive_e_nd_Gn(data_e,data_Gn2show,mode_str,
                                False #manyImgFlag
                                )
#---
if saveFlag_e: 
    APy3_GENfuns.printcol('saving Lateral-Overflow-calibrated values (in electron) to h5 file','blue')
    APy3_GENfuns.write_1xh5(outFileName_e, data_e, '/data/data/')
    APy3_GENfuns.printcol('Lateral-Overflow-calibrated values saved in '+outFileName_e,'green')
#---
# that's all folks
if verboseFlag:  
    for i_aux in range(3): APy3_GENfuns.printcol('---------','blue')



