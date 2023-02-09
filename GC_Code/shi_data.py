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
from collections import Counter
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon
from datetime import datetime, timedelta, time
# Configuration
level2_root = '/g/data/rq0/level_2'
radar_id = '50' #see the reference file for all radars: https://dapds00.nci.org.au/thredds/fileServer/rq0/radar_site_list.csv
date_str = '20141127' #format of YYYYMMDD
timestep_range = 144 #timestep in file to access data
var_name = 'shi' #reflectivity is the reflectivity at an altitude of 2.5km above the radar site, see reference file for radar altitude.

# Load data
level2_ffn = level2_root+'/'+radar_id+'/'+var_name.upper()+'/'+radar_id+'_'+date_str+'_'+var_name+'.nc'
with Dataset(level2_ffn, mode='r') as fh:
    # print the vairables
    # print('xxx',var_name,timestep)
    # print(np.shape(fh.variables[var_name]))
    lat_grid = fh.variables['latitude'][:]
    lon_grid = fh.variables['longitude'][:]
    refl_data_temp = fh.variables[var_name]

 #Attempts to mask certain gridpoints to confirm they are within bounds of LJ gridbox   
#polygon function for gridded box around LJ coordinate
    def polygon_func(lon_coor, lat_coor, poly_range):

        ## Longitude & Latitude range
        min_lon = lon_coor - poly_range
        max_lon = lon_coor + poly_range
        min_lat = lat_coor - poly_range
        max_lat = lat_coor + poly_range
        lon_range = [min_lon, max_lon]
        lat_range = [min_lat, max_lat]

     # Prepare the target area's polygon (Perhaps a more efficient way)
        polygon_lst = []
        polygon_lst.append([lon_range[0], lat_range[0]])
        polygon_lst.append([lon_range[0], lat_range[1]])
        polygon_lst.append([lon_range[1], lat_range[1]])
        polygon_lst.append([lon_range[1], lat_range[0]])

        # Return the constructed polygon
        return min_lon, max_lon, min_lat, max_lat, Polygon(polygon_lst)

min_lon, max_lon, min_lat, max_lat, area_polygon = polygon_func(150, -28, 5)

lat_mask = (lat_grid> min_lat) & (lat_grid < max_lat)
lon_mask = (lon_grid>  min_lon) & (lon_grid <  max_lon)
latlon_mask=lat_mask&lon_mask


#for i in range(timestep_range):
for i in range(22,25):
    refl_data_temp = fh.variables[var_name][i,:,:]
    # print('XXX',(refl_data_temp.data[mask]))
    nsteps = fh.variables[var_name].shape[0]      #  '''I've just change the assigned value to nsteps with shape rather than magic number [:, 1, 1]'''
    total_mask= latlon_mask
   
    lenmaskarray = len(refl_data_temp.data[mask])
    # print('len',nsteps,lenmaskarray)


 # to find timesteps where hail exceeded shi threshold > 62 (MESH >= 40mm)
    if lenmaskarray > 3: 
         #calculate proportiaon of good hail in the bounding box
         ngood=np.count_nonzero(total_mask)
         nbad=len(total_mask)-ngood
         fraction=ngood/len(total_mask)
         if max(refl_data_temp) > 62:
            refl_data_temp = fh.variables[var_name][i,:,:]
            # print('shape',np.shape(refl_data))
            time_step = fh.variables['time'][i]
            time_step = cftime.num2date(fh.variables['time'][i], fh.variables['time'].getncattr('units'))
            #print('selected time is', time_step, 'UTC+0')
            print(max(refl_data_temp,fraction))
           
            
