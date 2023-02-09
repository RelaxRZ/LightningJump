import all_plots
import pandas as pd
import similarity
from ast import literal_eval
import os
from progress import printProgressBar
import numpy as np
import similarity
import sys


path = '/g/data/er8/lightning/chizhang/Cluster_InfoCSV/Variable_Case_2'

file_to_run="/g/data/er8/lightning/jonathan/run_file.sh"
run_file = open(file_to_run, "w")
if not os.path.exists("/g/data/er8/lightning/jonathan/jobs2"):
    os.mkdir("/g/data/er8/lightning/jonathan/jobs2")

if not os.path.exists("/g/data/er8/lightning/jonathan/daily_data_v2"):
    os.mkdir("/g/data/er8/lightning/jonathan/daily_data_v2")

if not os.path.exists("/g/data/er8/lightning/jonathan/daily_data_v2/valid"):
    os.mkdir("/g/data/er8/lightning/jonathan/daily_data_v2/valid")

if not os.path.exists("/g/data/er8/lightning/jonathan/daily_data_v2/invalid"):
    os.mkdir("/g/data/er8/lightning/jonathan/daily_data_v2/invalid")

# Iterate through all the folders containing daily information about lightning clusters and create a script for each day
for dirs in os.listdir(path):
    print(dirs)
    
    script = open("/g/data/er8/lightning/jonathan/jobs2/"+dirs+"_script.qsub", "w")
    print("/g/data/er8/lightning/jonathan/"+dirs+"_script.qsub")
    script.write('#!/bin/bash \n')
    script.write('#PBS -l walltime=00:30:00 \n')
    script.write('#PBS -l mem=10GB \n')
    script.write('#PBS -l ncpus=1 \n')
    script.write('#PBS -l storage=gdata/k10+gdata/hh5+scratch/k10+gdata/er8+scratch/er8+gdata/ra22+gdata/rq0 \n')
    
    script.write('#PBS -l other=hyperthread \n')
    script.write('#PBS -q normal \n')
    script.write('#PBS -P er8 \n')

    script.write('module use /g/data3/hh5/public/modules \n')
    script.write('module load conda/analysis3 \n')
    script.write('conda \n')

    script.write(f"python /g/data/er8/lightning/jonathan/file_processing.py "+path+"/"+dirs)

    script.close()
    run_file.write("qsub " +"/g/data/er8/lightning/jonathan/jobs2/"+dirs+"_script.qsub \n")

run_file.close()




