# Standard libraries
from netCDF4 import Dataset
import numpy as np
from matplotlib import pyplot as plt
import cftime
import sys
import cartopy.crs as ccrs
import math
import numpy.ma as ma
import pandas as pd
import json
from collections import Counter
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon
from ast import literal_eval
from datetime import datetime, timedelta, time
# Configuration

# hail directory
level2_root = '/g/data/rq0/level_2'
#Read this from file
radar_id = '50' #see the reference file for all radars: https://dapds00.nci.org.au/thredds/fileServer/rq0/radar_site_list.csv
#read this from file
date_str = '20211014' #format of YYYYMMDD
#timestep1 = 42 #timestep in file to access data
#timestep2 = 43
#timestep3 = 47
var_name = 'shi' #reflectivity is the reflectivity at an altitude of 2.5km above the radar site, see reference file for radar altitude.

#jump_1 = 'jump_7'
#jump_2 = 'jump_8'
#jump_3 = 'jump_9'
#read in lightning jump data
df = pd.read_csv('/g/data/er8/lightning/shared/Cluster_InfoCSV/Variable_Case_1/Armidale_2021-10-14/Armidale_2021-10-14_Cluster1.csv')
target_lj_coor_list = []
target_lj_time_list = []
target_shi_time_list = []
target_radar_list = []
lj_coor_list = df["Coordinate"].tolist()
lj_time_list = df["Time"].tolist()
shi_time_list = df["time_SHI"].tolist()
lj_list = df["LJ"].tolist()
radar_list = df["radar_ID"].tolist()
# print(lj_list)
record = 0
maxrec=2 # number to plot

#loop over list to identify plots
for i in range(len(lj_list)):
    if record > maxrec:
        break
    if "Jump" in str(lj_list[i]):
        #check that it matched to a hail cluster in the radar data if an integer radar id is matched.
        if "_" in radar_list[i] or type(radar_list) == float:
            continue
        else:
            target_lj_coor_list.append(literal_eval(lj_coor_list[i]))
            target_lj_time_list.append(lj_time_list[i])
            target_shi_time_list.append(literal_eval(shi_time_list[i])[0])
            target_radar_list.append(radar_list[i])
            record += 1

for i in range(len(target_lj_coor_list)):
    print(target_lj_coor_list[i], target_lj_time_list[i], target_shi_time_list[i], target_radar_list[i])
    radar_id = target_radar_list[i]
    #     lj_lon = target_lj_coor_list[i][0]
    #     lj_lat = target_lj_coor_list[i][1]
    #     lj_time = target_lj_time_list[i]
    level2_ffn = level2_root+'/'+radar_id+'/'+var_name.upper()+'/'+radar_id+'_'+date_str+'_'+var_name+'.nc'
    color_list = ["red", "blue", "green"]
    color_list_shi = ["Reds", "Blues", "Greens"]
  
    #print('ffn',level2_ffn)
    with Dataset(level2_ffn, mode='r') as fh:
        #loop over the csv file
        lat_grid = fh.variables['latitude'][:]
        lon_grid = fh.variables['longitude'][:]
        #plotting figure  
        extent = (np.min(lon_grid), np.max(lon_grid), np.min(lat_grid), np.max(lat_grid))
        fig = plt.figure(figsize=(12, 20), facecolor='w')    
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        for j in range(len(target_lj_coor_list)):
            nsteps=np.count_nonzero(fh.variables[var_name][:,1,1])

        #data for lightning jump 1,2,3

        #timestep data for lightning jump 1
            fh_time_list = fh.variables["time"][:].tolist()
            time_list = target_shi_time_list[j].split(":")
            total_second = int(time_list[0]) * 60 * 60 + int(time_list[1]) * 60 + int(time_list[2])
            target_time_index = fh_time_list.index(total_second)
            time_step = cftime.num2date(fh.variables['time'][target_time_index], fh.variables['time'].getncattr('units'))

            cmap1 = plt.get_cmap(color_list_shi[j])
            refl_data = fh.variables[var_name][target_time_index,:,:]

            cs1 = ax.contourf(lon_grid, lat_grid, refl_data, np.arange(0,61), transform=ccrs.PlateCarree(),cmap = cmap1, extend = "max")


            ax.set_extent(extent, ccrs.PlateCarree())
            plt.colorbar(cs1,label = time_step,extend = "both",shrink=0.4,pad=.04,fraction=.05,aspect=30)
            ax.scatter(target_lj_coor_list[j][0], target_lj_coor_list[j][1],color=color_list[j], transform=ccrs.PlateCarree())
            for i, txt in enumerate(target_lj_time_list):
               ax.annotate(txt, xy=(target_lj_coor_list[i][0], target_lj_coor_list[i][1]), 
                 xytext=(-10, 15), textcoords='offset points', fontsize = 8)
             # put under for i ..ax.text(target_lj_coor_list[i][0], target_lj_coor_list[i][1], txt)
  


            plt.title("Lightning Jump Armidale 2021-10-14")
            ax.coastlines()
            gl = ax.gridlines(draw_labels=True, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False

    #'''All the plots will be stored under the path radar_plot/radar_plot_x_timestep/png, x refers to the timestep at the current stage'''
    plt.savefig('plot_test/' + 'Armidale_radar' + target_radar_list[i] + "_timestep.png")
 


