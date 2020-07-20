#!/bin/bash
#SBATCH --partition=cfel
#SBATCH --nodes=1                                 # Number of nodes
#SBATCH --job-name  perc_SatCheck
#SBATCH --chdir   ./sbatch_slurmWaste    # directory must already exist!
#SBATCH --output    perc_SatCheck-%j.out   # File to which STDOUT will be written
#SBATCH --error     perc_SatCheck-%j.err   # File to which STDERR will be written
#SBATCH --mail-type ALL                 # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --mail-user alessandro.marras@desy.de  # Email to which notifications will be sent
##
cd ..
source /usr/share/Modules/init/sh
module load anaconda/3
python3 ./sbatch_rawraw_2_e_AllinFolder_SaturationCheck.py $1 $2 $3 $4 $5 $6
##
###launch in sbatch: 
###all files in folder:
#####calibrated files e, GnCrsFn files, fullwell file => saturation map
##
##1 inFolder="/asap3/fs-ds-percival/gpfs/percival.sys.1/2020/data/11010234/processed/example_of_data_processing/input_scrmbld/"
##2 e_filesuffix="_e.h5"
##3 GnCrsFn_filesuffix="_GnCrsFn.h5"
##4 Sat_filesuffix="_Saturated.h5"
##5 fullWell_file="/asap3/fs-ds-percival/gpfs/percival.sys.1/2020/data/11010234/shared/CalibParamToUse/BSI04/BSI04_Tm20/BSI04_Tm20_fixGnCal/BSI04_Tm20_7of7ADC_biasBSI04.05_fixGn0_PGA6_2020.06.06_fixGn_approxFullWell.h5"
##6 maxSmplCrs="30"
##
## could be used as:
## sbatch ./sbatch_rawraw_2_e_AllinFolder_SaturationCheck.sh "/asap3/fs-ds-percival/gpfs/percival.sys.1/2020/data/11010234/processed/example_of_data_processing/input_scrmbld/" "_e.h5" "_GnCrsFn.h5" "_Saturated.h5" "/asap3/fs-ds-percival/gpfs/percival.sys.1/2020/data/11010234/shared/CalibParamToUse/BSI04/BSI04_Tm20/BSI04_Tm20_fixGnCal/BSI04_Tm20_7of7ADC_biasBSI04.05_fixGn0_PGA6_2020.06.06_fixGn_approxFullWell.h5" "30"
