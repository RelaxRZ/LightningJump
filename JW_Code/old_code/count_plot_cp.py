import matplotlib.pyplot as plt
import pandas as pd
import csv
from datetime import datetime
import sys
import numpy as np
import cartopy.crs as ccrs
import netCDF4
import re





def count_plot(folder, file):
    '''
    # initialising the year, month, date
    
    year = int(file[9:13])
    month = int(file[14:16])
    date = int(file[17:19])
    
    n_file = folder + file
    df = pd.read_csv(n_file)

    # Creating datetime column, removing the empty data entries
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    time = []
    for index, row in df.iterrows():
        b = datetime(year, month, date, int(row["Time"][0:2]), int(row["Time"][4:6]))
        time.append(b)
    df["DT"] = time
    '''
    df = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster0.csv')
    for i in range(19):
        cluster_num = i + 1
        temp = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster{cluster_num}.csv')
        df = pd.concat([df, temp])

    print(df)
    # Creating datetime column, removing the empty data entries
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)
    # Choosing the lightning jumps

    lj = df.loc[df["LJ"] != "False"]

    aus_min_lat = -44.
    aus_min_lon = 114.
    aus_max_lat = -11.
    aus_max_lon = 154.

    # longs are seperated into 4501
    # lats are seperated into 3501
   #Create a grid using .02 steps
    step=.02
    lon_v=np.arange(aus_min_lon, aus_max_lon,step)
    lat_v=np.arange(aus_min_lat, aus_max_lat,step)

    nlat=len(lat_v)
    nlon=len(lon_v)
    count_array=np.zeros((nlon,nlat))
    # Recovering the float values from the coordinates column in the df
    lats = []
    longs = []
    for index, row in lj.iterrows():
        coord = row["Coordinate"].split(",")
        longs.append(float(coord[0][1:]))
        lats.append(float(coord[1][:-1]))
        loni=(float(coord[0][1:]))
        lati=(float(coord[1][:-1]))
        # find
        #calculate the difference array
        difference_array_lat = np.absolute(lat_v- lati )
        difference_array_lon = np.absolute(lat_v- loni )
    
        # find the index of minimum element from the array
        index_lat = difference_array_lat.argmin()
        index_lon = difference_array_lon.argmin()
        count_array[index_lon,index_lat]=count_array[index_lon,index_lat]+1
        
    lj["lats"] = lats
    lj["longs"] = longs

 
    #plot the map with counts
    map_proj = ccrs.PlateCarree()
    data_proj = ccrs.PlateCarree()
    geodetic_proj = ccrs.PlateCarree()
    
    fig = plt.figure(figsize=(5,3.25))
    
    ax = fig.add_subplot(111, projection=map_proj)
    ax.coastlines(color='red')

    print(lon_v.shape)
    print(lat_v.shape)
    print(count_array.shape)
    
    
    count_plot = ax.pcolormesh(lon_v,\
                              lat_v,\
                              count_array,vmin=0,vmax=10,\
                              transform=data_proj)
    ax.set_extent([149,160,0,20])
    
    # add colorbar
    axpos = ax.get_position()
    cbar_ax = fig.add_axes([axpos.x1+0,axpos.y0,0.03,axpos.height])
    cbar = fig.colorbar(count_plot, cax=cbar_ax)
    cbar.ax.tick_params(labelsize=12)
    cbar.set_label('counts', fontsize=12)



    plt.savefig('test3.png')
    sys.exit()
    
    
    
    

    step = 0.01
    to_bin = lambda x: '%0.2f' % (np.floor(x / step) * step)
    lj["bin"] = lj['lats'].map(to_bin) + 'x' + \
                lj['longs'].map(to_bin)
    
    print(lj)
    # Counting the number of ljs in each bin
    bins = {}
    for i, r in lj.iterrows():
        key = (float(r['bin'][0:6]), float(r['bin'][7:]))
        if key not in bins.keys():
            bins[key] = 1
        else:
            bins[key] += 1    

    # Recovering the binned lat longs
    b_lat =[]
    b_long = []
    b_counts_scat = []
    for key, value in bins.items():
        b_lat.append(key[0])
        b_long.append(key[1])
        b_counts_scat.append(value)

    # Creating 2D array for pcolormesh
    b_long = np.array(b_long)
    b_lat = np.array(b_lat)
    b_counts = np.zeros((len(b_lat), len(b_lat)))

    for i in range(len(b_lat)):
        for j in range(len(b_long)):
            if (i==j):
                key = (b_lat[i], b_long[j])
                b_counts[i][j] = bins[key]
            else:
                b_counts[i][j] = None
    
    
    # Create base cartopy plot with coastline
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    # plt.title(f"Brisbane_LJ_{year}-{month}-{date}.png")
    plt.title(f"test.png")
    ax.set_extent([aus_min_lon, aus_max_lon, aus_min_lat, aus_max_lat], crs=ccrs.PlateCarree())


    cmap_reversed = plt.cm.get_cmap('viridis_r')
    # plt.pcolormesh(b_long, b_lat, b_counts, cmap = cmap_reversed, transform=ccrs.PlateCarree())


    # plt.scatter(b_long, b_lat, s = 1, c = b_counts_scat, transform=ccrs.PlateCarree(), marker = 'P', cmap = cmap_reversed)
    # plt.contourf(b_long, b_lat, b_counts, np.arange(0, 2), transform=ccrs.PlateCarree())
    plt.colorbar(shrink = 0.4)
    plt.savefig(f"test_scatter_dens.png", dpi = 2000)
    plt.close()
    
    
    
file = "Brisbane_2014-11-27_Cluster7.csv"
folder = "/g/data/er8/lightning/jonathan/Cluster_InfoCSV/Brisbane_2014-11-27/"
count_plot(folder, file)
#



