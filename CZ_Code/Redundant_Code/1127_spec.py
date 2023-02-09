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
from sklearn.cluster import DBSCAN

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
year = start_date[0:4]

# Special Distance for Clustering 10km in lat/lon
dist = 0.06742

# Construct the specific polygon
min_lon, max_lon, min_lat, max_lat, area_polygon = polygon_func(152.6333333, -29.35, 8)

#directory with the data
dirin='/g/data/er8/lightning/data/wz_ltng/'

# Obtain the csv file name and only read the 'date' data for preprocessing
filename='wz_ltng_'+year+'.csv'

# Read in the preprocessed CSV of lightning count of each day
light_date = pd.read_csv("Preprocess_CSV/date_num.csv")
for i in range(light_date.shape[0]):
    if light_date.iloc[i]["Date"] == "2014-11-27":
        break
    else:
        end_row += light_date.iloc[i]["Lightning_Count"]

df_date = pd.read_csv(dirin+filename, sep=',', skiprows = range(start_row, end_row), nrows = light_date.iloc[i]["Lightning_Count"])
path = light_date.iloc[i]["Date"] + "_Visualisation"
# os.makedirs(path)

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
IC_list = []
CG_list = []
ICCG_list = []
IC_amp = []
CG_amp = []
ICCG_amp = []
IC_abs_amp = []
CG_abs_amp = []
ICCG_abs_amp = []

def cluster_plot(df, type):
    # Plot the visulisation for specific groups of lightning in the specified region
    for i in range(df.shape[0]):
        if df.iloc[i]["Cluster_Label"] != -1:
            plt.plot(df.iloc[i]["longitude"], df.iloc[i]["latitude"], markersize=2, marker='o', color=plt.cm.RdYlBu(df.iloc[i]["Cluster_Label"]/10))
    return None

record = 0
activate = False

with open('1127_spec_cluster.txt', 'w') as f:
    for j in range(hrs * mins):
        IC, CG, ICCG = ICCG_Collect(current_start_time, current_end_time, df_date, area_polygon)
        current_end_time += timedelta(minutes = gap)
        current_start_time += timedelta(minutes = gap)

        coordinate_list = (np.array(ICCG["coordinate"].tolist()))
        try:
            clustering = DBSCAN(eps = 0.24, min_samples = 10).fit(coordinate_list)
            ICCG["Cluster_Label"] = clustering.labels_
            try:
                check_cluster = list(set(clustering.labels_))
                check_cluster.remove(-1)
                f.write(str(check_cluster))
                f.write("\n")
            except:
                f.write("No Outlier")
                f.write("\n")

            if activate == False:
                if len(check_cluster) >= 1:
                    activate = True
                else:
                    continue
            else:
                if len(check_cluster) >= 1:
                    record = 0
                else:
                    record += 1
        except:
            if activate == False:
                f.write("No Valid Cluster")
                f.write("\n")
                continue
            else:
                record += 1
                f.write("No Lightning Observed")
                f.write("\n")
                continue

        # Plot all the lightning on a single day on a map
        ax = plt.axes(projection = ccrs.PlateCarree())
        plt.suptitle("Brisbane Lightning" + '\n' + str(current_start_time))
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], ccrs.PlateCarree())

        cluster_plot(ICCG, "Total")

        ax.coastlines(resolution='110m')
        plt.legend(loc='lower left')

        plt.savefig('split_cluster_test/' + str(j) + '_test.png')

        if record == 5:
            f.write("Stop at " + str(j) + "th minute")
            f.write("\n")
            activate = False
            record = 0
            continue
        '''
        IC_list.append(IC.shape[0])
        CG_list.append(CG.shape[0])
        ICCG_list.append(IC.shape[0] + CG.shape[0])

        IC_amp.append(round(sum((IC["amp"])), 3))
        CG_amp.append(round(sum((IC["amp"])), 3))
        ICCG_amp.append(round(sum((IC["amp"])) + sum((CG["amp"])), 3))

        IC_abs_amp.append(round(sum(abs(IC["amp"])), 3))
        CG_abs_amp.append(round(sum(abs(CG["amp"])), 3))
        ICCG_abs_amp.append(round(sum(abs(IC["amp"])) + sum(abs(CG["amp"])), 3))

        # Plot all the lightning on a single day on a map
        ax = plt.axes(projection = ccrs.PlateCarree())
        plt.suptitle("Brisbane Lightning" + '\n' + str(current_start_time))
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], ccrs.PlateCarree())

        # Plot CG, IG instance point on a map
        plot_func(CG_test, "CG")
        plot_func(IC_test, "IC")
        ax.coastlines(resolution='110m')
        plt.legend(loc='lower left')

        # Save the Image
        plt.savefig(path + "/" + "map_" + str(j) + '.png')
        plt.show()
        '''
    '''
    # CSV Generating Code
    df_ICCG = [IC_list, CG_list, ICCG_list, IC_amp, CG_amp, ICCG_amp, IC_abs_amp, CG_abs_amp, ICCG_abs_amp]
    df = pd.DataFrame(df_ICCG).transpose()
    df.columns = ['IC', 'CG', "Total", 'IC_amp', 'CG_amp', "Total_amp", 'IC_abs_amp', 'CG_abs_amp', "Total_abs_amp"]
    df.to_csv('Lightning_TSCSV/20141127_Brisbane_8.csv', index=False, header=True)
    '''