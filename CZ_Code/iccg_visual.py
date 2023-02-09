import os
import math
import pandas as pd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from LJ_FUNCTION import spec_year, start_end_row, ICCG_Collect, plot_func, polygon_func, initial_centroid, next_moment_cluster, blank_plot, target_cluster_plot, centroid_record, centroid_record_func

###############################################Define Variables############################################
gap = 2
hrs = 24
mins = 60
date_range = 365
time_interval = int(hrs * mins / gap)
case_lat = -20.758
case_lon = 148.607
case_range = 5
DBSCAN_scale = 10
DBSCAN_dist = 0.24
case_area = "Mackay"
case_date = "2021-10-17"
date_format = "%Y-%m-%d"
case_study = case_area + "_" + case_date

# Create directory for storing the ICCG plot of the case study
if not os.path.isdir(os.path.join("ICCG_Plot/", case_study)):
    os.makedirs(os.path.join("ICCG_Plot/", case_study))

# Construct the specific polygon
min_lon, max_lon, min_lat, max_lat, area_polygon = polygon_func(case_lon, case_lat, case_range)

################################################Read In Data###############################################
# Obtain the csv file name and only read the 'date' data for preprocessing
# filename='/g/data/er8/lightning/data/wz_ltng/wz_ltng_' + case_date[0:4] + '.csv'

# # Compute the start and end rows of the case study from the csv and extract the data
# start_row, end_row, light_date, i_date = start_end_row(case_date)
# df_date = pd.read_csv(filename, sep=',', skiprows = range(start_row, end_row), nrows = light_date.iloc[i_date]["Lightning_Count"])
df_date = pd.read_csv("/g/data/er8/lightning/chizhang/Preprocess_CSV/" + case_date[0:4] + "/" + "data_num_" + case_date + ".csv", sep=',')


# Create the coordinate, timestamp information for each instance
df_date["coordinate"] = df_date[["longitude", "latitude"]].apply(list, axis = 1)
df_date["datetime"] = df_date['date'] + " " + df_date["time"]
df_date["datetime"] = pd.to_datetime(df_date["datetime"])

# Collect the lightning within each minutes in the target area
## First set the default datetime with the given dataframe (e.g. 2014-01-01 00:00:00)
datetime_default = datetime.strptime(df_date.iloc[0]["date"], date_format)

## Then set time gap to split the dataframe (e.g. 1 minute)
## In this code, we investigate on the selected date data within each minute (24 * 60 groups of data)
current_start_time = datetime_default
current_end_time = datetime_default + timedelta(minutes = gap)

################################################Read In Data###############################################
# Start Iterative Plotting
for j in range(time_interval):
    IC_test, CG_test, ICCG_test = ICCG_Collect(current_start_time, current_end_time, df_date, area_polygon)
    current_end_time += timedelta(minutes = gap)
    current_start_time += timedelta(minutes = gap)

    # Plot all the lightning on a single day on a map
    ax = plt.axes(projection = ccrs.PlateCarree())
    plt.suptitle('Lightning Australia 2022' + "\n" + str(current_start_time))
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], ccrs.PlateCarree())

    # Plot CG, IG instance point on a map
    plot_func(CG_test, "CG")
    plot_func(IC_test, "IC")
    ax.coastlines(resolution='110m')
    plt.legend(loc='lower left')

    # Save the Image
    plt.savefig("ICCG_Plot/" + case_study + "/" + "map_" + str(j) + '.png')
    plt.show()