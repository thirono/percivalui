# load environment on cfeld-perc02
# source /home/prcvlusr/PercAuxiliaryTools/Anaconda3/Anaconda3/bin/activate root
#
# load environment on maxwell
source /usr/share/Modules/init/sh
module load anaconda/3
#
# execute
echo " "
echo "find last scrambled img set, descramble, show (eventually also CDS,PedSub,avg)"
#python3 ./LookAtFLast.py
python3 ./LookAtFLast_10.py
