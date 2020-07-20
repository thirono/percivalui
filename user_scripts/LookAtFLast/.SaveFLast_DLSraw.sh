# load environment on cfeld-perc02
# source /home/prcvlusr/PercAuxiliaryTools/Anaconda3/Anaconda3/bin/activate root
#
# load environment on maxwell
source /usr/share/Modules/init/sh
module load anaconda/3
#
# execute
echo " "
echo "find last scrambled img set, descramble, save as DLSraw"
python3 ./SaveFLast_DLSraw.py

