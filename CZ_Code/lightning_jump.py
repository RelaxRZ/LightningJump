
import argparse
import numpy as np
from mpi4py import MPI
from LJ_FUNCTION import file_count, LJ_Info, remove_RLJ, LJ_ID

##########################################Read in Tuneable Variables######################################
# Accept input from the job submission
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--list', help='delimited list input', type=str)
args = parser.parse_args()

# Assign value to the tuneable variables
variable_list = [(item) for item in args.list.split(',')]
case_area = variable_list[0]
case_month = variable_list[1]
mins_range = int(variable_list[2])
LJ_threshold = int(variable_list[3])
time_interval = int(variable_list[4])
variable_case = variable_list[5]

############################################Define Local Variables########################################
# Start Parallel Processing
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Create the date-stamp of the case study
num_date = (np.array_split(range(size), size)[rank])
if (len(str(num_date[0] + 1)) == 1):
    num_date = "0" + str(num_date[0] + 1)
else:
    num_date = str(num_date[0] + 1)

# Define the 'Yearly' case study date with parallel processing
# case_date = case_month + num_date

# Define the 'Daily' case study date with multiple job submission
case_date = case_month

###########################################Define Lightning Jump##########################################
# Define the path to the case study for generating the LJ and Sigma Information
main_path = "/g/data/er8/lightning/chizhang/Cluster_InfoCSV/"
case_path = "Variable_Case_" + variable_case
main_path = main_path + case_path
case_study = case_area + case_date
dir_path = main_path + "/" + case_study
case_study = case_study + "_Cluster"
cluster_amount = file_count(dir_path)
LJ_Info(dir_path, case_study, cluster_amount, LJ_threshold)

# Remove the redundant lightning jump which happen within a 6 mins range
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5749929/
gap = int(mins_range / time_interval)
remove_RLJ(dir_path, case_study, cluster_amount, gap)

##########################################Assign Lightning Jump ID#########################################
# Assign ID for each seperated lightning jump within each cluster of the selected case study
LJ_ID(dir_path, case_study, cluster_amount, gap)

# End Parallel Processing
local_result = case_study
result = comm.gather(local_result, root=0)
if (rank == 0): print(result)