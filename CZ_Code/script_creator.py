import pandas as pd
from LJ_FUNCTION import script_basic, write_summary_job

# Read in case area information
case_area = pd.read_csv("Redundant_Data/Resource/case.csv")

###############################################Define Variables############################################
# Variables for cluster tracking (Area Box Size, Min Flashes Amount, Max Flashes Distance, Time Gap, Variable Case)
tuneable_var_cluster = "4,20,0.3,2,9"
# Variables for lightning jump (LJ Period Range, LJ Threshold, Time Gap, Variable Case)
tuneable_var_lj = "6,20,2,9"
# Variables for shi collection (LJ Bounding Box Size, SHI Collection Period Range, SHI Threshold, Variable Case)
tuneable_var_shi = '0.5,50,10,9'       

##########################################Write Individual Job Script######################################
# Loop through each input variable and write a unique job script (Cluster Tracking)
for case in range(case_area.shape[0]):
    with open(f"Job_Script/cluster_track_job_{case_area.iloc[case]['Area']}.qsub", "w") as job_file:
        # Write the template job script to the file, replacing the input variable with the current value
        case_variable = ','.join(str(x) for x in case_area.iloc[case].tolist())
        case_variable = case_variable + "," + tuneable_var_cluster
        script_basic(job_file)
        job_file.write('mpirun python3 /g/data/er8/lightning/chizhang/cluster_track.py -l "{var}" >& /g/data/er8/lightning/chizhang/output.log'.format(var=case_variable))

# Loop through each input variable and write a unique job script (Lightning Jump)
for case in range(case_area.shape[0]):
    with open(f"Job_Script/lightning_jump_job_{case_area.iloc[case]['Area']}.qsub", "w") as job_file:
        # Write the template job script to the file, replacing the input variable with the current value
        case_variable = case_area.iloc[case]["Area"] + "_," + case_area.iloc[case]["Date"] + "," + tuneable_var_lj
        script_basic(job_file)
        job_file.write('mpirun python3 /g/data/er8/lightning/chizhang/lightning_jump.py -l "{var}" >& /g/data/er8/lightning/chizhang/output.log'.format(var=case_variable))

# Loop through each input variable and write a unique job script (SHI)
for case in range(case_area.shape[0]):
    with open(f"Job_Script/shi_collection_job_{case_area.iloc[case]['Area']}.qsub", "w") as job_file:
        # Write the template job script to the file, replacing the input variable with the current value
        case_variable = case_area.iloc[case]["Area"] + "_," + case_area.iloc[case]["Date"] + "," + "".join(case_area.iloc[case]["Date"].split("-")) + "," + tuneable_var_shi
        script_basic(job_file)
        job_file.write('mpirun python3 /g/data/er8/lightning/chizhang/shi_collection.py -l "{var}" >& /g/data/er8/lightning/chizhang/output.log'.format(var=case_variable))

##########################################Write Summarised Job Script######################################
# Write the summarise script that process all the sub-script of each group of jobs
write_summary_job("cluster_track_job.qsub", "cluster_track_job", case_area)
write_summary_job("lightning_jump_job.qsub", "lightning_jump_job", case_area)
write_summary_job("shi_collection_job.qsub", "shi_collection_job", case_area)