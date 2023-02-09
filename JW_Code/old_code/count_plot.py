import matplotlib.pyplot as plt
import pandas as pd
import csv
from datetime import datetime
import sys
import numpy as np
import cartopy.crs as ccrs
import netCDF4
import re
import matplotlib as mpl
import os
# Given a dataframe, plot all ljs
def count_2dhist(df):

    # Remove empty data rows, for both lj and coordinates
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    df['Coordinate'].replace('', np.nan, inplace=True)
    df.dropna(subset=['Coordinate'], inplace=True)

    # Choosing the lightning jumps
    lj = df.loc[df["LJ"] != "False"]

    # Australias min max lat longs
    aus_min_lat = -44.
    aus_min_lon = 114.
    aus_max_lat = -11.
    aus_max_lon = 154.

    # Recovering the float values from the coordinates column in the df
    lats = []
    longs = []
    for index, row in lj.iterrows():
        # Splitting the coordinates column bc it is a string not list
        coord = row["Coordinate"].split(",")
        longs.append(float(coord[0][1:]))
        lats.append(float(coord[1][:-1]))

    # Creating new columns with the float values
    lj["lats"] = lats
    lj["longs"] = longs

    # Create base cartopy plot with coastline
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    plt.title(f"2d Hist tester.png")
    ax.set_extent([aus_min_lon, aus_max_lon, aus_min_lat, aus_max_lat], crs=ccrs.PlateCarree())

    # Reverse the viridis color map
    # cmap_reversed = p.cm.get_cmap('magma_r')

    # create own colormap
    cmap_me = mpl.colors.ListedColormap(['white','darkblue', 'teal', 'lightblue', 'darkgreen', 'lightgreen','yellow','orange', 'darkorange', 'red', 'darkred'])
    cmap_me.set_over('0.25')
    cmap_me.set_under('0.75')
    bounds = [-1,0,1, 2, 4, 7, 8,10,20,30,40]

    plt.hist2d(lj["longs"], lj["lats"], bins = 150, cmap = cmap_me)

    # Showing the colorbar
    plt.colorbar(shrink = 0.4)
    plt.savefig(f"test_2dhist.png", dpi = 1000)
    plt.close()

    '''
    This may become useful later, this code splits data into respective bins based on lat 
    and longs, then counts the number of ljs in each bin, to put in a dictionary
    key = latxlong
    value = num ljs in box

    # Mapping the ljs to their respective bins
    step = 0.01
    to_bin = lambda x: '%0.2f' % (np.floor(x / step) * step)
    lj["bin"] = lj['lats'].map(to_bin) + 'x' + \
                lj['longs'].map(to_bin)
    
    # Counting the number of ljs in each bin
    bins = {}
    for i, r in lj.iterrows():
        key = (float(r['bin'][0:6]), float(r['bin'][7:]))
        if key not in bins.keys():
            bins[key] = 1
        else:
            bins[key] += 1    

    # Recovering the binned lat longs, putting them into lists
    b_lat =[]
    b_long = []
    for key, value in bins.items():
        b_lat.append(key[0])
        b_long.append(key[1])
    '''
    


path = '/g/data/er8/lightning/shared/Cluster_InfoCSV'
# Given a directory, plot all the lightning jumps in a density plot
def clean_2dhist(path):
    # Holder df for all csv files within directory
    df_all = pd.DataFrame()

    # iterate through all dirs, subdirs and files
    for subdir, dirs, files in os.walk(path):
        for file in files:
            # collect the cluster number from the file
            pattern = r'Cluster\d+'
            match = re.search(pattern, file)
            cluster = match.group(0)

            # collect the day from the file
            date_pattern = r'[\d]{4}-[\d]{2}-[\d]{2}'
            match2 = re.search(date_pattern, file)
            day = match2.group(0)

            # collect the city from the file
            city = file.split('_', 1)[0]
            print(city)

            # join all the csv files
            df_temp = pd.read_csv(os.path.join(subdir, file))
            df_all = pd.concat([df_all, df_temp])

    # Plot the desity using 2dhist of all ljs
    count_2dhist(df_all)



clean_2dhist(path)









# Attempt at using pcolormesh
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

    # Concat all the clusters together into one dataframe
    df = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster0.csv')
    for i in range(19):
        cluster_num = i + 1
        temp = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster{cluster_num}.csv')
        df = pd.concat([df, temp])
    

    # Remove empty data rows
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    # Choosing the lightning jumps
    lj = df.loc[df["LJ"] != "False"]

    # Australias min max lat longs
    aus_min_lat = -44.
    aus_min_lon = 114.
    aus_max_lat = -11.
    aus_max_lon = 154.

    # longs are seperated into 4501
    # lats are seperated into 3501

    # Recovering the float values from the coordinates column in the df
    lats = []
    longs = []
    for index, row in lj.iterrows():
        # Splitting the coordinates column bc it is a string not list
        coord = row["Coordinate"].split(",")
        longs.append(float(coord[0][1:]))
        lats.append(float(coord[1][:-1]))

    # Creating new columns with the float values
    lj["lats"] = lats
    lj["longs"] = longs

    # Mapping the ljs to their respective bins
    step = 0.01
    to_bin = lambda x: '%0.2f' % (np.floor(x / step) * step)
    lj["bin"] = lj['lats'].map(to_bin) + 'x' + \
                lj['longs'].map(to_bin)
    

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



