#!/bin/bash

#SBATCH --partition=cfel
#SBATCH --nodes=1                                 # Number of nodes: 1,2,3 do not work (not all file created, no error reported). 4 ndes does not work 2/5
#SBATCH --job-name  perc_raw2e_2n_jplusj
#####SBATCH --chdir   /home/marras/PercAuxiliaryTools/LookAtFLast/sbatch_slurmWaste    # directory must already exist!
#SBATCH --chdir   ./sbatch_slurmWaste    # directory must already exist!
#
#SBATCH --output    perc_raw2e_2n_jplusj-%j.out   # File to which STDOUT will be written
#SBATCH --error    perc_raw2e_2n_jplusj-%j.err   # File to which STDERR will be written
#SBATCH --mail-type ALL                 # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --mail-user alessandro.marras@desy.de  # Email to which notifications will be sent
#
cd ..
source /usr/share/Modules/init/sh
module load anaconda/3
#
#1 input folder
#2 prefix file
#3,4 scrmbld suffix
#5 output folder
#6,7  Img to process     "000:249","248:499"  or   "498:749","748:999"
#8 ADCcor file
#9 MultiGn file
#{10} Gn0 alternate pedestal
#{11} Gn0 CMA?
#{12} Gn0 CDS?
#
waitingtime="5s"
#
## lauches a 250 images descramling, wait for it to finish (+ few secs), then launch the next 250 image descrambling 
echo " job on $2 $6 ... started, will wait until it ends"
python3 ./sbatch_rawraw_2_e_partialset_xb.py $1 $2 $3 $4 $5 $6 $8 $9 ${10} ${11} ${12} 
wait 
## wait for it to finish
sleep $waitingtime
## wait few sec more
##
echo " job on $2 $7 ... started, will wait until it ends"
python3 ./sbatch_rawraw_2_e_partialset_xb.py $1 $2 $3 $4 $5 $7 $8 $9 ${10} ${11} ${12} 
wait 
sleep $waitingtime
#
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

