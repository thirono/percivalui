#!/bin/bash

# load environment on maxwell
source /usr/share/Modules/init/sh
module load anaconda/3

# look at data descrambled and converted to e using sbatch_rawraw_2_e_1k_4x250_ 1File/AllInFolder _fast_Launcher.sh
# use:
# ./xxx.sh

python3 special_rawraw_2_e_1k_4x250_PostViewer.py

