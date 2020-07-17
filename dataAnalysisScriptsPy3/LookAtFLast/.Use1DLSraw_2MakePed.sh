# load environment on cfeld-perc02
# source /home/prcvlusr/PercAuxiliaryTools/Anaconda3/Anaconda3/bin/activate root
#
# load environment on maxwell
source /usr/share/Modules/init/sh
module load anaconda/3
#
# execute
echo " "
echo "1 descrambled img set in folder -> CDS avg, save (useful to make pedestal)"
python3 ./Use1DLSraw_2MakePed.py

