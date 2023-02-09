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
'''
module use /g/data/hh5/public/modules
module load conda/analysis3
'''
# plots lightning jumps and topography
def plot_lj(path, folder):
    # initialising the year, month, date
    
    year = int(path[9:13])
    month = int(path[14:16])
    date = int(path[17:19])
    
    n_path = folder + path
    print(n_path)
    df = pd.read_csv(n_path)

    # Creating datetime column, removing the empty data entries

    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    time = []
    for index, row in df.iterrows():
        b = datetime(year, month, date, int(row["Time"][0:2]), int(row["Time"][4:6]))
        time.append(b)
    
    # df["DT"] = datetime(year, month, date, int(row["Time"][0:2]), int(row["Time"][4:6]))
        
    df["DT"] = time

    
    # Choosing the lightning jumps

    lj = df.loc[df["LJ"] != "False"]

    # Create base cartopy plot with coastline
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    plt.title(f"Brisbane_LJ_{year}-{month}-{date}.png")
    ax.set_extent([150, 154, -30, -25], crs=ccrs.PlateCarree())

    # Plotting of the LJs
    for index, row in lj.iterrows():
        coord = row["Coordinate"].split(",")
        longitude = float(coord[0][1:])
        lat = float(coord[1][:-1])
        plt.plot(longitude, lat, markersize=.5, marker='o', color='blue')

    plt.savefig(f"LJ_plots/Brisbane_LJ_{year}-{month}-{date}.png")
    plt.close()


# PLots only the topography of Australia
def topo_LJ2():
    path = '/g/data/er8/lightning/data/Data_9secDEM_D8/20230111000000000-P1S-ABOM_GEOM_AUSDEM_PRJ_LONLAT_1000-LJ.nc'
    fh = netCDF4.Dataset(path, "r")

    # Reading in the lat longs and DEM
    lat_grid = fh.variables['lat'][:]
    lon_grid = fh.variables['lon'][:]
    dem_data = fh.variables['dem'][:]

    print('------min and max-----\n')
    print(np.min(dem_data), np.max(dem_data))
    print('-----------\n')
    
    # Lat long bounds for Brisbane/Queensland area
    minlon, maxlon = 150, 154
    minlat, maxlat = -30, -25
    
    # Plotting the DEM
    # Setting bounds with extent
    extent = (minlon, maxlon, minlat, maxlat)
    fig = plt.figure(figsize=(12, 15), facecolor='w')    
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.contourf(lon_grid, lat_grid, dem_data, np.arange(-10,1500),
                        transform=ccrs.PlateCarree())
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.colorbar(shrink = 0.4)
    plt.title('testers')
    ax.coastlines()

    plt.savefig("test.png")
    plt.close()
    
    # Close the file
    fh.close()

# Plots both lightning jumps and topography
def lj_topo_plot(path, folder):
    path_netcdf = '/g/data/er8/lightning/data/Data_9secDEM_D8/20230111000000000-P1S-ABOM_GEOM_AUSDEM_PRJ_LONLAT_1000-LJ.nc'
    fh = netCDF4.Dataset(path_netcdf, "r")

    # Initialising the year, month, date

    pattern = r'Cluster\d+'
    match = re.search(pattern, path)
    cluster = match.group(0)


    year = int(path[6:10])
    month = int(path[11:13])
    date = int(path[14:16])


    # Reading in the data frame
    df = pd.read_csv(folder + path)

    # Creating datetime column, removing the empty data entries
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    time = []
    for index, row in df.iterrows():
        b = datetime(year, month, date, int(row["Time"][0:2]), int(row["Time"][4:6]))
        time.append(b)
        
    df["DT"] = time
    
    # Choosing the lightning jumps
    lj = df.loc[df["LJ"] != "False"]

    # Reading in the lat longs and DEM
    lat_grid = fh.variables['lat'][:]
    lon_grid = fh.variables['lon'][:]
    dem_data = fh.variables['dem'][:]
    '''
    # Lat long bounds for Brisbane/Queensland area
    minlon, maxlon = 150, 154
    minlat, maxlat = -30, -25
    '''
    # Lat long bounds for Ouyen area
    minlon, maxlon = 135, 148
    minlat, maxlat = -38, -30
    
    # Plotting the DEM
    # Setting bounds with extent
    extent = (minlon, maxlon, minlat, maxlat)
    fig = plt.figure(figsize=(12, 15), facecolor='w')    
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Plotting topography
    plt.contourf(lon_grid, lat_grid, dem_data, np.arange(-15,1500),
                        transform=ccrs.PlateCarree())
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.colorbar(shrink = 0.4)

    # Plotting LJs
    
    for index, row in lj.iterrows():
        coord = row["Coordinate"].split(",")
        longitude = float(coord[0][1:])
        lat = float(coord[1][:-1])
        plt.plot(longitude, lat, markersize=2, marker='o', color='red')

    plt.title(f"LJ_plots/Brisbane_LJ_Topo_{year}-{month}-{date}_{cluster}.png")
    ax.coastlines()

    plt.savefig(f"LJ_plots/Brisbane_LJ_Topo_{year}-{month}-{date}_{cluster}.png")
    plt.close()
    
    # Close the file
    fh.close()



def clean_lj_topo(df, day, cluster, city):
    path_netcdf = '/g/data/er8/lightning/data/Data_9secDEM_D8/20230111000000000-P1S-ABOM_GEOM_AUSDEM_PRJ_LONLAT_1000-LJ.nc'
    dem_data = netCDF4.Dataset(path_netcdf, "r")

    # Removing the empty data entries
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    # Removing the empty data entries
    df['Coordinate'].replace('', np.nan, inplace=True)
    df.dropna(subset=['Coordinate'], inplace=True)
    
    # Choosing the lightning jumps
    lj = df.loc[df["LJ"] != "False"]

    # Reading in the lat longs and DEM
    lat_grid = dem_data.variables['lat'][:]
    lon_grid = dem_data.variables['lon'][:]
    dem = dem_data.variables['dem'][:]
    
    # Recovering the float values from the coordinates column in the df
    lats = []
    longs = []
    for index, row in lj.iterrows():
        # Splitting the coordinates column bc it is a string not list
        coord = row["Coordinate"].split(",")
        longs.append(float(coord[0][1:]))
        lats.append(float(coord[1][:-1]))

    # Lat long bounds for Ouyen area
    minlon, maxlon = np.min(longs), np.max(longs)
    minlat, maxlat = np.min(lats), np.max(lats)
    
    # Plotting the DEM
    # Setting bounds with extent
    extent = (minlon, maxlon, minlat, maxlat)
    fig = plt.figure(figsize=(12, 15), facecolor='w')    
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Plotting topography
    plt.contourf(lon_grid, lat_grid, dem, np.arange(-15,1500),
                        transform=ccrs.PlateCarree())
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.colorbar(shrink = 0.4)

    # Plotting LJs
    plt.plot(longs, lats, markersize=2, marker='o', color='red')

    # create folder
    if not os.path.isdir(f"LJ_plots/{city}_lj_topo"):
        # not present then create it.
        os.makedirs(f"LJ_plots/{city}_lj_topo")

    plt.title(f"LJ_plots/{city} LJ + Topo: {year}-{month}-{date}_{cluster}")
    ax.coastlines()

    plt.savefig(f"LJ_plots/{city}_LJ_Topo_{year}-{month}-{date}_{cluster}.png")
    plt.close()
    
    # Close the file
    dem_data.close()
