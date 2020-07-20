#!/bin/bash

#launch in sbatch: 
#all files in folder
#calibrated files e, GnCrsFn files, fullwell file => saturation map

# use:
# ./<thisfile>.sh
# do NOT add spaces between = and variables!
# DO NOT use "xxx"+"yyy"

#using /asap3 files
inOutFolder="/asap3/fs-ds-percival/gpfs/percival.sys.1/2020/data/11010234/processed/example2_of_data_processing/output_electrons/"
e_filesuffix="_e.h5"
GnCrsFn_filesuffix="_GnCrsFn.h5"
Sat_filesuffix="_Saturated.h5"
fullWell_file="/asap3/fs-ds-percival/gpfs/percival.sys.1/2020/data/11010234/shared/CalibParamToUse/BSI04/BSI04_Tm20/BSI04_Tm20_fixGnCal/BSI04_Tm20_7of7ADC_biasBSI04.05_fixGn0_PGA6_2020.06.06_fixGn_approxFullWell.h5"
maxSmplCrs="30"
#
sbatch ./sbatch_rawraw_2_e_AllinFolder_SaturationCheck.sh $inOutFolder $e_filesuffix $GnCrsFn_filesuffix $Sat_filesuffix $fullWell_file $maxSmplCrs
echo " "
echo "all jobs submitted"
echo "  check status as:   squeue -u yourname"
echo "  then check for output files in $inOutFolder"
echo "--  --  --  --"
#
# to check:
# squeue -u marras
# or: 
# ~/Utili/sbatch_showJobs.sh
#
# logfiles in .../sbatch_slurmWaste
#
# to abort:
# scancel -t PENDING -u marras

