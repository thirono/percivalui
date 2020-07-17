# load environment on cfeld-perc02
# source /home/prcvlusr/PercAuxiliaryTools/Anaconda3/Anaconda3/bin/activate root
#
# load environment on maxwell
source /usr/share/Modules/init/sh
module load anaconda/3
#
# execute
echo " "
echo "all descrambled img set in folder: Gn-dependent avg, save ad h5"
python3 ./SaveAvgGnDependent_FromAllDLSrawInFolder_3.py

