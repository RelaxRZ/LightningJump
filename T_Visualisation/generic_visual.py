import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from datetime import datetime, timedelta
from visualisation_func import spec_year, ICCG_Collect, plot_func, polygon_func

# Variable define
date_range = 365
start_row = 1
end_row = 1
hrs = 24
mins = 60
gap = 1
file_begin = True
start_date = "2014-01-01"
date_format = "%Y-%m-%d"

# Construct the specific polygon
min_lon, max_lon, min_lat, max_lat, area_polygon = polygon_func(152.6333333, -27.35, 3)

# Data datetime information
datein = '20140101'
year = datein[0:4]
month = datein[4:6]
day = datein[6:8]

#directory with the data
dirin='/g/data/er8/lightning/data/wz_ltng/'

# Obtain the csv file name and only read the 'date' data for preprocessing
filename='wz_ltng_'+year+'.csv'

# Read in the preprocessed CSV of lightning count of each day
light_date = pd.read_csv("Preprocess_CSV/date_num.csv")

# Start extracting the instance within the specific date (save memory)
for i in range(light_date.shape[0]):
    if file_begin == True:
        # Extract instance from dataframe (first day)
        df_date = pd.read_csv(dirin+filename, sep=',', nrows = light_date.iloc[i]["Lightning_Count"])
        end_row += light_date.iloc[i]["Lightning_Count"]
        file_begin = False
        # Create Visualisation Folder
        path = light_date.iloc[i]["Date"] + "_Visualisation"
        os.makedirs(path)
        break
    else:
        # Extract instance from dataframe
        df_date = pd.read_csv(dirin+filename, sep=',', skiprows = range(start_row, end_row), nrows = light_date.iloc[i]["Lightning_Count"])
        end_row += light_date.iloc[i]["Lightning_Count"]
        # Create Visualisation Folder
        path = light_date.iloc[i]["Date"] + "_Visualisation"
        os.makedirs(path)

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

# Start Iterative Plotting
for j in range(hrs * mins):
    IC_test, CG_test = ICCG_Collect(current_start_time, current_end_time, df_date, area_polygon)
    current_end_time += timedelta(minutes = gap)
    current_start_time += timedelta(minutes = gap)

    # Plot all the lightning on a single day on a map
    ax = plt.axes(projection = ccrs.PlateCarree())
    plt.suptitle('Lightning Australia 2014' + "\n" + str(current_start_time))
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], ccrs.PlateCarree())

    # Plot CG, IG instance point on a map
    plot_func(CG_test, "CG")
    plot_func(IC_test, "IC")
    ax.coastlines(resolution='110m')
    plt.legend(loc='lower left')

    # Save the Image
    plt.savefig(path + "/" + "map_" + str(j) + '.png')
    plt.show()