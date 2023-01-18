import pandas as pd
from datetime import datetime
from LJ_FUNCTION import file_count, radar_ID, shi_Collect

###############################################Define Variables############################################
# Define variables for extracting the target cluster
cluster_box_range = 0.5
main_path = "Cluster_InfoCSV"
case_study = "Brisbane_2014-11-27"
dir_path = main_path + "/" + case_study
case_study = case_study + "_Cluster"
cluster_amount = file_count(dir_path)

# Define variables for extracting the SHI netCDF file
shi_time = 50
var_name = 'shi'
date = '20141127'
date_datetime = datetime(int(date[:4]), int(date[4:6]), int(date[6:]))
last_moment = date_datetime.replace(hour=23, minute=59, second=59)
level2_root = '/g/data/rq0/level_2/'

##########################################Extra the Radar Coordinates######################################
df_radar = pd.read_csv("Redundant_Data/Resource/radar_site_list.csv")
radar_list = [1, 15, 2, 24, 29, 33, 39, 48, 52, 57, 65, 7, 74, 79, 95, 10, 16, 20, 25, 3, 34, 4, 44, 49, 53,
            58, 66, 70, 75, 8, 97, 11, 17, 21, 26, 30, 36, 40, 45, 5, 54, 6, 67, 71, 76, 9, 12, 18, 22, 27, 31,
            37, 41, 46, 50, 55, 63, 68, 72, 77, 93, 14, 19, 23, 28, 32, 38, 42, 47, 51, 56, 64, 69, 73, 78, 94, 43]

# Create dictionary for storing the level_2 radar station's coordinate information
radar_dict = dict(zip(radar_list, [None] * len(radar_list)))
for index, row in df_radar.iterrows():
    if row['id'] in radar_dict:
        radar_dict[row['id']] = [row['site_lon'], row['site_lat']]

###########################################Collect Radar Information#######################################
# Record radar ID of each lightning jump within each cluster
radar_ID(dir_path, case_study, cluster_amount, cluster_box_range, radar_dict)

############################################Collect SHI Information########################################
# Record SHI information from the target radar station of each lightning jump within each cluster
shi_Collect(cluster_amount, dir_path, case_study, cluster_box_range, level2_root, var_name, date, shi_time, last_moment)