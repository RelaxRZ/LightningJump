import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import cartopy.crs as ccrs
import netCDF4
import re
import matplotlib as mpl
import itertools
import json
import seaborn as sns
from geopy.distance import geodesic
from scipy.stats import gaussian_kde
import mpl_scatter_density # adds projection='scatter_density'
from matplotlib.colors import LinearSegmentedColormap
from astropy.visualization import LogStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from matplotlib import cm
from matplotlib.colors import Normalize 
from scipy.interpolate import interpn
from LJ_FUNCTION import polygon_func

# https://stackoverflow.com/questions/20105364/how-can-i-make-a-scatter-plot-colored-by-density-in-matplotlib
# "Viridis-like" colormap with white background
WHITE_VIRIDIS = LinearSegmentedColormap.from_list('white_viridis', [
    (0, '#ffffff'),
    (1e-20, '#440053'),
    (0.2, '#404388'),
    (0.4, '#2a788e'),
    (0.6, '#21a784'),
    (0.8, '#78d151'),
    (1, '#fde624'),
], N=256)


# https://stackoverflow.com/questions/20105364/how-can-i-make-a-scatter-plot-colored-by-density-in-matplotlib/53865762#53865762
def density_scatter( x , y, ax = None, sort = True, bins = 20, fig = None , **kwargs )   :
    if ax is None :
        fig , ax = plt.subplots()
    data , x_e, y_e = np.histogram2d( x, y, bins = bins) #, density = True 
    z = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , data , np.vstack([x,y]).T , method = "splinef2d", bounds_error = False)

    #To be sure to plot all data
    z[np.where(np.isnan(z))] = 0.0

    # Sort the points by density, so that the densest points are plotted last
    if sort :
        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]
    
    ax.scatter( x, y, c=z, **kwargs )

    norm = Normalize(vmin = np.min(z), vmax = np.max(z))
    cbar = fig.colorbar(cm.ScalarMappable(norm = norm), ax=ax)
    cbar.ax.set_ylabel('Counts')

    return ax

# Given a filename, return the date, city, cluster
def name_extract(filename):
    '''
    # collect the cluster number from the file
    pattern = r'Cluster\d+'
    match = re.search(pattern, filename)
    cluster = match.group(0)
    '''
    # collect city
    city = filename.split('_', 1)[0]
    
    # collect the day string from the file
    date_pattern = r'[\d]{4}-[\d]{2}-[\d]{2}'
    match2 = re.search(date_pattern, filename)
    day = match2.group(0)

    return day, city


# Add datetime function used with df.apply
def add_datetime(time, date):
    return datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), int(time[0:2]), int(time[3:5]), 0)


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
    bris_lat, bris_long = -29.35,152.63
    min_lon, max_lon, min_lat, max_lat, ploy = polygon_func(bris_long, bris_lat, 6)

    # Recovering the float values from the coordinates column in the df
    lats = []
    longs = []
    for index, row in lj.iterrows():
        # Appending lats and longs 
        longs.append(row["Coordinate"][0])
        lats.append(row["Coordinate"][1])

    # Creating new columns with the float values
    lats = np.array(lats)
    longs = np.array(longs)
    



    # Create base cartopy plot with coastline
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())  
    ax.coastlines()
    
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    plt.title(f"2d Hist tester.png")

    
    # plt.hist2d(lj["longs"], lj["lats"], bins = 100, cmap = cmap_reversed)
    # density_scatter( longs , lats, ax = ax, sort = True, bins = 100, fig=fig, s=1)  
    x = longs
    y = lats
    data , x_e, y_e = np.histogram2d( x, y, bins = 50, density = True )
    z = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , data , np.vstack([x,y]).T , method = "splinef2d", bounds_error = False)

    #To be sure to plot all data
    z[np.where(np.isnan(z))] = 0.0

    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]
    

    plt.scatter( x, y, c=z, s = 3 )

    norm = Normalize(vmin = np.min(z), vmax = np.max(z))
    cbar = fig.colorbar(cm.ScalarMappable(norm = norm), ax=ax)
    cbar.ax.set_ylabel('Density')

    # Showing the colorbar
    # plt.colorbar(shrink = 0.4)
    plt.savefig(f"test_2dhist_magma.png", dpi = 1000)
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
    

# Given df, day, cluster, and city, plot all the ljs on top of a topographic map
def clean_lj_topo(df):
    # Reading in the DEM data
    path_netcdf = '/g/data/er8/lightning/data/Data_9secDEM_D8/20230111000000000-P1S-ABOM_GEOM_AUSDEM_PRJ_LONLAT_1000-LJ.nc'
    dem_data = netCDF4.Dataset(path_netcdf, "r")

    # Removing the empty data entries for lj column
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    # Removing the empty data entries for coordinate column
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

    # Lat long bounds for given df
    minlon, maxlon = np.min(longs), np.max(longs)
    minlat, maxlat = np.min(lats), np.max(lats)
    
    # Plotting the DEM
    # Setting bounds with extent
    extent = (minlon-4, maxlon+4, minlat-4, maxlat+4)
    fig = plt.figure(figsize=(12, 15), facecolor='w')    
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Plotting topography
    plt.contourf(lon_grid, lat_grid, dem, np.arange(-15,1500),
                        transform=ccrs.PlateCarree())
    ax.set_extent(extent, ccrs.PlateCarree())
    plt.colorbar(shrink = 0.4)

    # Plotting LJs
    for index, row in lj.iterrows():
        # Splitting the coordinates column bc it is a string not list
        coord = row["Coordinate"].split(",")
        longitude = (float(coord[0][1:]))
        lat = (float(coord[1][:-1]))
        plt.plot(longitude, lat, markersize=2, marker='o', color='red')
        
    '''
    # create folder
    if not os.path.isdir(f"LJ_plots/{}_lj_topo"):
        # not present then create it.
        os.makedirs(f"LJ_plots/{}_lj_topo")
        '''

    # Plotting title and coastlines
    plt.title(f"Lighting jumps on top of topographic map")
    ax.coastlines()

    # Saving plot
    plt.savefig(f"LJ_plots/validated_lj_sw.png")
    plt.close()
    
    # Close the file
    dem_data.close()


# Given df, day, cluster, and city, plot probability of detection against success ratio
def pod_x_sr(df):

    # Removing the empty data entries for lj column
    df = df.mask(df["LJ"] == '')
    df.dropna(subset=['LJ'], inplace=True)

    # Mapping the rows to their respective bins based on sigma values
    step = 0.5
    to_bin = lambda x: '%0.2f' % (np.floor(x / step) * step)
    df["bin"] = df['Sigma'].map(to_bin)

    # creating random shi values
    shi_vals = np.random.rand(len(df))
    df['SHI'] = shi_vals

    # Appending the row data to their respective bins (based on sigma vals)
    bins = {}
    for i, r in df.iterrows():
        key = float(r['bin'])
        val = [r['Sigma'], r['LJ'], r['SHI']] # r['SHI']
        if key not in bins.keys():
            bins[key] = [val]
        else:
            bins[key].append(val)

    plt.figure(figsize = (12, 6), dpi = 300)
    colors = itertools.cycle(['white','darkblue', 'teal', 'lightblue', 'darkgreen', 'lightgreen',
                                'yellow','orange', 'darkorange', 'red', 'darkred'])
    
    # key is the sigma value bin, val are the rows that fall within the bin
    for key, val in sorted(bins.items()):
    
        # print(type(key))
        # print(f'{key}: {val}')
        a = 0    # Yes LJ, Yes Hail
        b = 0    # Yes LJ, No Hail
        c = 0    # No LJ, Yes Hail
        for row in val:
            if (row[1] != 'False') and (row[2] > 0.5):
                a += 1
            elif (row[1] != 'False') and (row[2] < 0.5):
                b += 1
            elif (row[1] == 'False') and (row[2] > 0.5):
                c += 1
        # print(a, b, c)
        
        # X is the Success Ratio
        # Y is the Probability of Detection
        # Checking for dividing by 0
        x = 0 if a == 0 and b == 0 else a/(a+b)
        y = 0 if a == 0 and c == 0 else a/(a+c)

        plt.scatter(x, y, marker='o', color = next(colors), label = f'{key} \u03C3')

    
    # plt.legend(loc='upper left')
    plt.title("Probability of Detection against Success Ratio")
    plt.xlabel('Success Ratio (1 - FAR)')
    plt.ylabel('Probability of Detection (POD)')
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01, 1),
                         loc='upper left', borderaxespad=0.)
    plt.savefig('pod_x_sr.png')
    plt.close()


# Plot the leadtimes of severe weather against sigma values
def leadtime_x_sigma(df):

    time_diff = [] # a list containing the lead times of valid lightning jumps and hail (SHI > 26.6)
    sigma = [] # a list of the respective sigma values to the lead times

    # Extracting the time difference between lightning jump and severe weather
    for index, row in df.iterrows():
        # t = literal_eval(row["time_SHI"]) # use either depending on whether or not the list string has become a proper list
        t = row['time_SHI']
        shi = row["max_SHI"]

        # Iterating through the list of max SHI values to see if there is severe weather (SHI > 26.6)
        # Taking note of the index
        ind = -1
        for i in range(len(shi)):
            if shi[i] > 26.6:
                ind = i
                break
        # If no shi value greater than 26.6 it is not counted as severe, thus continue
        if ind == -1: continue

        # start time is the time of the lightning jump
        start = row['datetime']

        # end time is the first instance of the severe weather
        end = datetime(start.year, start.month, start.day, 
                           int(t[ind][0:2]), int(t[ind][3:5]), int(t[ind][6:8]))

        # record the difference
        time_diff.append((end-start).total_seconds()/60)

        # record the sigma
        sigma.append(row['Sigma'])

    sigma = [np.log(x) for x in sigma]

    time_diff = np.array(time_diff)
    sigma = np.array(sigma)

    density_scatter( time_diff, sigma, bins = [50,50], s = 10 )
    # plt.figure(figsize=(7.5, 10))
    
    plt.title("Lead Time vs log(Sigma)")
    plt.plot([0, 50], [np.log(2), np.log(2)], color='red', label = "Min Sigma value log(2)")
    plt.legend()

    plt.xlabel("Lead Time (mins)")
    plt.ylabel("log(Sigma)")
    plt.grid()
    plt.savefig('leadtime_test.png', dpi = 600)
    plt.close()


# Plot the percentage of LJ with (ljev: with event, ljnoev: with no event)
def hourly_dist(valid, invalid, **kwargs):
    # Extracting the times of ljnoev
    ljnoev = [] # lightning jumps with no severe weather event
    for index, row in invalid.iterrows():
        if row['Sigma'] < 2: continue
        if (row['time_SHI'] != row['time_SHI']):
            ljnoev.append(int(row['Time'][0:2]))
    # Extracting the times of ljev
    ljev = [] # lightning jumps with a severe weather even
    for index, row in valid.iterrows():
        ljev.append(int(row['Time'][0:2]))

    # Allocating into arrays to be plotted
    data = [ljnoev, ljev]
    colors = ['red', 'blue']
    names = ['LJnoSW', 'LJSW']

    plt.figure(figsize=(10, 5))
    plt.hist(data, color = colors, label = names, bins = range(25), alpha = 0.5, **kwargs) # , density = True
    plt.xticks(np.arange(0, 24, 1.0))
    plt.legend()

    plt.title("Hourly Counts of Lightning Jumps")
    plt.xlabel("UTC Time")
    plt.ylabel("Number of Lightning Jumps")
    plt.savefig("Hourly_count.png")
    plt.close()

    return

#  Plot the percentage of LJ with (ljev: with event, ljnoev: with no event)
def hourly_dist_IC(valid, invalid, **kwargs):
    
    # Extracting the times of ljnoev
    ljnoev = [] # lightning jumps with no severe weather event
    for index, row in invalid.iterrows():
        for i in range(int(row['IC_num'])):
            ljnoev.append(int(row['Time'][0:2]))

    # Extracting the times of ljev
    ljev = [] # lightning jumps with a severe weather even
    for index, row in valid.iterrows():
        for i in range(int(row['IC_num'])):
            ljev.append(int(row['Time'][0:2]))
    
    # Allocating into arrays to be plotted
    data = [ljnoev, ljev]
    colors = ['red', 'blue']
    names = ['LJnoSW', 'LJSW']

    plt.figure(figsize=(10, 5))
    plt.hist(data, color = colors, label = names, bins = range(25), alpha = 0.5, **kwargs)
    plt.xticks(np.arange(0, 24, 1.0))
    plt.legend()

    plt.title("Hourly Counts of Total IC Lightning Flashes")
    plt.xlabel("UTC Time")
    plt.ylabel("Total IC Lightning Flashes")
    plt.savefig("Hourly_Counts_IC.png")
    plt.close()

    return

#  Plot the percentage of LJ with (ljev: with event, ljnoev: with no event)
def hourly_dist_total_sigma(valid, invalid, **kwargs):
    
    # Extracting the times of ljnoev
    ljnoev = [] # lightning jumps with no severe weather event
    for index, row in invalid.iterrows():
        for i in range(int(row['Sigma'])):
            ljnoev.append(int(row['Time'][0:2]))

    # Extracting the times of ljev
    ljev = [] # lightning jumps with a severe weather even
    for index, row in valid.iterrows():
        for i in range(int(row['Sigma'])):
            ljev.append(int(row['Time'][0:2]))
    
    # Allocating into arrays to be plotted
    data = [ljnoev, ljev]
    colors = ['red', 'blue']
    names = ['LJnoSW', 'LJSW']

    plt.figure(figsize=(10, 5))
    plt.hist(data, color = colors, label = names, bins = range(25), alpha = 0.5, **kwargs)
    plt.xticks(np.arange(0, 24, 1.0))
    plt.legend()

    plt.title("Hourly Counts of Total Sigma")
    plt.xlabel("UTC Time")
    plt.ylabel("Total Sum of Sigma Values")
    plt.savefig("Hourly_Counts_total_sigma.png")
    plt.close()

    return


def monthly_dist_lj(valid, invalid, **kwargs):
    # Extracting the times of ljnoev
    ljnoev = [] # lightning jumps with no severe weather event
    for index, row in invalid.iterrows():
        if row['Sigma'] < 2: continue

        ljnoev.append(row['datetime'].month)

    # Extracting the times of ljev
    ljev = [] # lightning jumps with a severe weather even
    for index, row in valid.iterrows():
        ljev.append(row['datetime'].month)

    # Allocating into arrays to be plotted
    data = [ljnoev, ljev]
    colors = ['red', 'blue']
    names = ['LJnoSW', 'LJSW']

    plt.hist(data, color = colors, label = names, bins = range(1,14), alpha = 0.5, **kwargs)
    plt.xticks(np.arange(1, 13, 1.0))
    plt.legend()

    plt.title("Monthly Counts of Lightning Jumps")
    plt.xlabel("Month")
    plt.ylabel("Number of Lightning Jumps")
    plt.savefig("Monthly_Counts_LJ.png")
    plt.close()

    return

# Plot the SHI value against the sigma value
def shi_x_sigma(df):
    # Masking empty LJ values
    df = df.mask(df["LJ"] == 'False')
    df.dropna(subset=['LJ'], inplace=True)

    # Finding lightning jumps with severe weather events
    df = df.mask(df['time_SHI'] == '')
    df.dropna(subset=['time_SHI'], inplace=True)

    df['avg'] = df['max_SHI'].apply(np.nanmean)
    df['Sigma'] = df['Sigma'].apply(np.log)
    df['avg'] = df['avg'].apply(np.log)  
    
    density_scatter( df['Sigma'], df['avg'], bins = [50,50], s = 10 )
    plt.title("SHI x Sigma")
    plt.xlabel("loge(Sigma)")
    plt.ylabel("loge(Average MAX SHI)")
    plt.grid()
    plt.savefig('Sigma_x_SHI.png', dpi = 500)
    plt.close()
    

# Plot the pdf of the leadtimes between ljs and severe weather
def leadtime_pdf(df):

    # Masking empty LJ values
    df = df.mask(df["LJ"] == 'False')
    df.dropna(subset=['LJ'], inplace=True)

    # Masking lightning jumps without severe weather
    df = df.mask(df['time_SHI'] == '')
    df = df.mask(df['time_SHI'] == 'No_File')
    df.dropna(subset=['time_SHI'], inplace=True)

    time_diff = []
    # Extracting the time difference between lightning jump and severe weather
    for index, row in df.iterrows():
        # t = literal_eval(row["time_SHI"])
        t = row['time_SHI']
        shi = row["max_SHI"]

        # iterating through the max shi values to see if there is a valid severe weather event (shi > 26.6)
        ind = -1
        for i in range(len(shi)):
            if shi[i] > 26.6:
                ind = i
                break
        # if not then continue 
        # if ind == -1: continue
            
        # start time is the time of the lightning jump
        start = row['datetime']

        # end time is the first instance of the severe weather
        end = datetime(start.year, start.month, start.day, 
                           int(t[ind][0:2]), int(t[ind][3:5]), int(t[ind][6:8]))

        # record the difference
        time_diff.append((end-start).total_seconds()/60)
 
    # plot data
    fig, ax = plt.subplots()

    sns.kdeplot(time_diff, ax = ax)
    ax2 = ax.twinx()
    sns.histplot(time_diff, ax = ax2, binwidth=1)
    plt.title('Count/PDF of Leadtime Values')
    ax.set_xlabel("Lead Time (mins)")
    ax.set_ylabel("Density")
    plt.tight_layout()
    plt.xlim([0, np.max(time_diff)])
    plt.xticks(np.arange(min(time_diff), max(time_diff)+1, 5.0))

    plt.grid()
    plt.savefig("validationlead_time_pdfv2.png", dpi = 500)
    plt.close()


# Plot lead time against max SHI
def leadtime_x_SHI(df):
    time_diff = []
    time_max = []

    first_shi = []
    max_shi = []
    for index, row in df.iterrows():
        # t = literal_eval(row["time_SHI"])
        t = row["time_SHI"]
        shi = row["max_SHI"]

        # iterating through the max shi values to see if there is a valid severe weather even (shi > 26.6)
        ind = -1
        for i in range(len(shi)):
            if shi[i] > 26.6:
                ind = i
                break
        # if not we continue
        # if ind == -1: continue
        
        # Recording the index of the max of the max shi values
        max_index = np.nanargmax(shi)

        # start time is the time of the lightning jump
        start = row['datetime']

        # end time is the first instance of the severe weather
        end1 = datetime(start.year, start.month, start.day, 
                           int(t[ind][0:2]), int(t[ind][3:5]), int(t[ind][6:8]))

        # time diff at the maximum SHI value within the 50 mins
        end2 = datetime(start.year, start.month, start.day, 
                           int(t[max_index][0:2]), int(t[max_index][3:5]), int(t[max_index][6:8]))

        time_diff.append((end1-start).total_seconds()/60) # lead time to the first instance of severe weather
        time_max.append((end2-start).total_seconds()/60) # lead time to the max instance of severe weather

        first_shi.append(row['max_SHI'][ind]) # respective shi values for both
        max_shi.append(np.log(row['max_SHI'][max_index]))
    
    time_diff = np.array(time_diff)
    time_max = np.array(time_max)
    first_shi = np.array(first_shi)
    max_shi = np.array(max_shi)

    density_scatter( time_diff, first_shi, bins = [50,50], s = 10 )
    plt.ylim([0, 700])
    plt.title('Lead Time vs SHI')

    plt.xlabel("Lead Time (mins)")
    plt.ylabel("SHI")
    plt.plot([0, 50], [26.6, 26.6], color='red', label = "Min SHI value 26.6", alpha = 0.5)
    plt.legend()
    plt.savefig("leadtime_x_shi.png", dpi = 500)
    plt.close()

    
# Plot distance vs lead time (also pdf)
def dist_x_leadtime(df):
    time_diff = [] # recording the leadtime of severe weather and lightning jumps
    dist_diff = [] # recording the distance between the lightning jump and the severe weather event
    
    for index, row in df.iterrows():
        # t = literal_eval(row["time_SHI"])
        t = row["time_SHI"]
        shi = row["max_SHI"]

        # iterating through the shi values to see if there is valid severe weather event
        ind = -1
        for i in range(len(shi)):
            if shi[i] > 26.6:
                ind = i
                break
        # if not then we continue
        # also checks that we have a valid coordinate
        # if (ind == -1) or (len(row['coor_SHI'])) == 0: continue
        
        # start time is the time of the lightning jump
        start = row['datetime']

        # end time is the first instance of the severe weather
        end = datetime(start.year, start.month, start.day, 
                           int(t[ind][0:2]), int(t[ind][3:5]), int(t[ind][6:8]))
        row['Coordinate'].reverse()

        time_diff.append((end-start).total_seconds()/60) # recording the time difference seconds
        dist = geodesic(row['coor_SHI'][ind], row['Coordinate']).km # recording the distance in km
        dist_diff.append(dist)
        
        print(f"{row['coor_SHI'][ind]},{row['Coordinate']}")

    
    # plt.scatter(time_diff, dist_diff)

    time_diff = np.array(time_diff)
    dist_diff = np.array(dist_diff)
    density_scatter( time_diff, dist_diff, bins = [50,50], s = 10 )

    plt.title("Lead Time vs Distance (between LJ and SW)")
    plt.xlabel('Lead Time (mins)')
    plt.ylabel('Distance (km)')
    plt.savefig("leadtime_x_distance", dpi = 400)


# Plot PDF of SHI values greater than 26.6
def shi_pdf(df):
    all_shi = [] # list containing all shi values greater than 26.6
    for index, row in df.iterrows():
        for shi in row['max_SHI']:
            if not np.isnan(shi):
                all_shi.append(shi)
    # plot data
    fig, ax = plt.subplots()

    sns.histplot(all_shi, ax = ax, binwidth=2.5)
    # ax2 = ax.twinx()
    # sns.kdeplot(all_shi, ax = ax2, bw_adjust=0.25, clip = (3, 250))
    plt.axvline(x = 26.6, color = 'red', label = 'Severe Weather Cutoff (SHI = 26.6)')
    plt.legend()

    plt.title("Severe Hail Index Counts (Validated)")

    
    ax.set_xlabel("Severe Hail Index")
    plt.tight_layout()
    
    plt.xlim([0, 250])
    plt.grid()
    plt.savefig("Severe_ALL_SHI_pdf.png", dpi = 300)
    plt.close()

# no used
def ic_pdf_valid_x_invalid(valid, invalid):

    # plot data
    plt.figure(figsize=(10, 6.5))
  
    sns.histplot(invalid['IC_num'],
         alpha=0.5,
         label='invalid')

    sns.histplot(valid['IC_num'], 
         alpha=0.75, # the transaparency parameter
         label='valid')
        
    plt.legend()
    plt.xlim([0, 1500])
    plt.title('PDF: Invalid/Valid IC Lightning Flash Count')
    plt.xlabel('IC Lightning Flash Count')
    plt.savefig("IC_PDF_invalid")
    plt.close()

# Create a time series plot for average sigma value for hourly distribution
def time_series_avg_sigma(valid, invalid):
    
    # Extracting the times of ljnoev
    ljnoev = np.zeros(24) # lightning jumps with no severe weather event
    ljnoev_counts = np.zeros(24)
    for index, row in invalid.iterrows():
        if row['Sigma'] < 2:
            continue
        ljnoev[int(row['Time'][0:2])] += row['Sigma']
        ljnoev_counts[int(row['Time'][0:2])] += 1

    # Extracting the times of ljev
    ljev = np.zeros(24) # lightning jumps with a severe weather even
    ljev_counts = np.zeros(24)
    for index, row in valid.iterrows():
        ljev[int(row['Time'][0:2])] += row['Sigma']
        ljev_counts[int(row['Time'][0:2])] += 1
    
    for i in range(24):
        # if ljnoev[i] != 0:
        ljnoev[i] = ljnoev[i]/ljnoev_counts[i]
        # if ljev[i] != 0:
        ljev[i] = ljev[i]/ljev_counts[i]
        # if (ljnoev[i] < 2):
            # print(ljnoev[i])

    plt.figure(figsize=(10, 5))
    plt.plot(range(24), ljev, label='LJSW')
    plt.plot(range(24), ljnoev, label='LJNOSW')
    plt.xticks(np.arange(0, 24, 1.0))
    plt.yticks(np.arange(0, max(ljev)+1, 5.0))
    plt.legend()
    plt.plot([0, 24], [2, 2], color='red', label = "Min Sigma value 2", alpha=0.5)
    plt.legend()

    plt.xlabel("UTC Time")
    plt.ylabel("Average Sigma Values")
    plt.title("Time Series for Avg Sigma Values")

    plt.savefig("Avg_sigma_valid_and_invalid.png", dpi = 300)
    plt.close()

# Create a time series plot for average IC value for hourly distribution (not used)
def time_series_avg_IC(valid, invalid):
    
    # Extracting the times of ljnoev
    ljnoev = np.zeros(24) # lightning jumps with no severe weather event
    ljnoev_counts = np.zeros(24)
    for index, row in invalid.iterrows():
        ljnoev[int(row['Time'][0:2])] += row['CG_num']
        ljnoev_counts[int(row['Time'][0:2])] += 1

    # Extracting the times of ljev
    ljev = np.zeros(24) # lightning jumps with a severe weather even
    ljev_counts = np.zeros(24)
    for index, row in valid.iterrows():
        ljev[int(row['Time'][0:2])] += row['CG_num']
        ljev_counts[int(row['Time'][0:2])] += 1
    
    for i in range(24):
        if ljnoev[i] != 0:
            ljnoev[i] = ljnoev[i]/ljnoev_counts[i]
        if ljev[i] != 0:
            ljev[i] = ljev[i]/ljev_counts[i]

    plt.figure(figsize=(10, 5))
    plt.plot(range(24), ljev, label='LJSW')
    plt.plot(range(24), ljnoev, label='LJNOSW')
    plt.xticks(np.arange(0, 24, 1.0))
    plt.yticks(np.arange(0, max(ljev)+1, 100.0))
    plt.legend()

    plt.xlabel("UTC Time")
    plt.ylabel("Average CG Lightning Flashes")
    plt.title("Time Series for Avg CG Lightning Flashes")

    plt.savefig("Avg_CGnum_valid_and_invalid.png", dpi = 300)
    plt.close()





    

    

