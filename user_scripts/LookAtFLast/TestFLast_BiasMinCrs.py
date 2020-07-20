# -*- coding: utf-8 -*-
"""
Descramble and visualize small scrambled dataset (seq Mod)

load environmentL on cfeld-perc02 is:
source /home/prcvlusr/PercAuxiliaryTools/Anaconda3/Anaconda3/bin/activate root

python3 ./LookAtFLast.py
or:
start python
# python2.7
# execfile("WIP_UseFLastDLSraw_Fingerplot_WIP.py") # this is in python 2.7
#
python3
exec(open("./TestFLast_BiasMinCrs.py").read()); print('Python3 is horrible')
"""
#%% imports and useful constants
from APy3_auxINIT import *
from APy3_descrambleLast import descrambleLast
#---
#%% Flags
swapSmplRstFlag= True
seqModFlag= False # this actually mean: SeqMod image taken with a stdMod mezzfirm, so that only hal image is relevand data
refColH1_0_Flag = True # True if refcol data are streamed out as H1<0> data.
#
showFlag= True
saveFlag= False # this actually mean: save DLSraw file [Nimg,Row,Col], /data/,/reset/, uint16
cleanMemFlag= True # this actually mean: save descrambled image (DLSraw standard)
#
ADCcorrFlag=False
CDSFlag=False
avgFlag=False
#
pedSubtractFlag=False
#
saveAvgFlag=False
#
detailFlag= False
#---
#
#%% auxiliary functs 
#---
#
#%% data from here
mainFolder='/gpfs/cfel/fsds/labs/percival/2019/experiment/20190301_000_Petra3_P04_BSI02/scratch/P04/'
if mainFolder[-1]!='/': mainFolder+='/'
#---
#%% profile it
#import cProfile
#cProfile.run('aux_data= descrambleLast(mainFolder, ...)', sort='cumtime')
#APy3_GENfuns.printcol("scripts took {0} sec".format(aux_length),'green')
#---
#%% or just execute it
auxAr= descrambleLast(mainFolder, 
                          swapSmplRstFlag,seqModFlag,refColH1_0_Flag, 
                          ADCcorrFlag,CDSFlag,avgFlag,pedSubtractFlag,saveAvgFlag,
                          showFlag,saveFlag, detailFlag,cleanMemFlag)
#
iGn=0; iCrs=1; iFn=2
#
APy3_GENfuns.printcol("biasTest of H0",'green')
auxAr2= auxAr[1:,:,:,32:704,iCrs] # H0
auxind= auxAr2== -256
auxAr2[auxind]=+255
(mImg,mSR,mRow,mCol)=APy3_GENfuns.argmin_xD(auxAr2)
#print(str(auxAr2.shape))
print("min Crs found at "+str((mImg,mSR,mRow,mCol)))
print("min Crs values is "+str(auxAr2[mImg,mSR,mRow,mCol]))
APy3_GENfuns.printcol("--  --  --  --",'green')

#auxAr= numpy.copy(dscrmbld_GnCrsFn[0:,:,:,1408:1440,iCrs]) # Refcol as H1<0>
#auxAr= numpy.copy(dscrmbld_GnCrsFn[1:,:,:678,1408:1440,iCrs]) # Refcol as H1<0>
#auxAr= numpy.copy(dscrmbld_GnCrsFn[1:,:,683:749,1408:1440,iCrs]) # Refcol as H1<0>
#auxAr= numpy.copy(dscrmbld_GnCrsFn[1:,:,753:,1408:1440,iCrs]) # Refcol as H1<0>


