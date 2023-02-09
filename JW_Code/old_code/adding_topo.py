import matplotlib.pyplot as plt
import pandas as pd
import csv
from datetime import datetime
import sys
import numpy as np
import cartopy.crs as ccrs
import pygmt
import netCDF4
import re

# Function to find the closest gridpoint to the inputted lat longs
def get_data(lat, lon, lat_input, long_input):

    # Finding closest grid locations
    lat_index  = np.nanargmin((lat-lat_input)**2)
    long_index = np.nanargmin((lon-long_input)**2)
    
    # Prints out the closest grid lat longs
    # print(lat[lat_index])
    # print(lon[long_index])
    return long_index,lat_index

# Given the inputted lat longs, returns the DEM of the closest gridpoint
def add_topo(latitude, longitude):
    # Reading the DEM netCDF file
    path_netcdf = '/g/data/er8/lightning/data/Data_9secDEM_D8/20230111000000000-P1S-ABOM_GEOM_AUSDEM_PRJ_LONLAT_1000-LJ.nc'
    f = netCDF4.Dataset(path_netcdf, "r")
    
    # Extracting the variables
    dem = f.variables['dem']
    lat = f.variables['lat'][:]
    lon = f.variables['lon'][:]
    print(dem)


    # Finding the closest grid index given the input lat longs
    ix_min, iy_min = get_data(lat, lon, latitude, longitude)
    print(ix_min)
    print(iy_min)

    # Read values out of the netCDF file for the closest grid point
    out = dem[iy_min, ix_min]

    # Close file
    f.close()
    
    return out

print(add_topo(-34., 151.))
'''
    n_path = folder + path
    print(n_path)
    df = pd.read_csv(n_path)
'''
