#this routine reads in th wzltn files, plots a map
#inputs
#arg1=datein YYYYMMDD    
#note this file needs to be run in interactive mode because it is quite memory hungry
#orginal version Caroline Poulsen 12/12/2022
#

#import required libraries
import pandas as pd
import sys
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt


# read in value from command line
narg=len(sys.argv)
if narg > 1:
    datein=(sys.argv[1])
else:
    datein='20141127'

year=datein[0:4]
month=datein[4:6]
day=datein[6:8]

#directory with the data
dirin='/g/data/er8/lightning/data/wz_ltng/'
#note takes a while to read

filename='wz_ltng_'+year+'.csv'

#read in file
df = pd.read_csv(dirin+filename)

print(df)


dateins= year+'-'+month+'-'+day

#mask the data frame for the specific day

day_mask_all = df[df["date"] == dateins].reset_index()
day_mask_cg = df[(df["date"] == dateins) & (df["stroke_type"] == "CG")]
day_mask_ic = df[(df["date"] == dateins) & (df["stroke_type"] == "IC")]


# note the need to reset the indexing of the data frame after it is masked otherwise you cannot loop through the data
day_mask_cg=day_mask_cg.reset_index()
day_mask_ic=day_mask_ic.reset_index()


#convert time stamp into a datetime index and add a column to the data frame this will make it easier to plot a time series
import datetime
num_cg=len(day_mask_cg["longitude"])

cg_datetime =[]
#loop over day and convert date and time to a datetime object
for  i in range (num_cg):
    
    cg_time=str(day_mask_cg["time"][i])
    offset=0
    hour=cg_time[offset+0:offset+2]
    minutes=cg_time[offset+3:offset+5]
    secs=cg_time[offset+6:offset+8]

    #append data to create a new list
    cg_datetime.append(datetime.datetime(int(year), int(month), int(day),hour=int(hour),minute=int(minutes), second=int(secs)))
#print('cg_dateime',cg_datetime)

# Using DataFrame.insert() to add a column
day_mask_cg.insert(2, "Datetime", cg_datetime, True)


#print(day_mask_cg)
#data is ordered like this
#    date      time   latitude   longitude     amp stroke_type  ic_height  num_sensors
#e.g. 2014-01-01,00:00:10,-23.759951,158.995169,    -8.272,IC,      14.5,          8


#plot all lightning on a single day in Brisbane 
ax1 = plt.axes(projection=ccrs.PlateCarree())
ax1.set_extent([148, 153, -22, -32], ccrs.PlateCarree())
plt.title('Lightning Brisbane '+dateins)
#loop over intra cloud and plot
num_ic=len(day_mask_ic["longitude"])
for  i in range (num_ic-1):
    if i == 1:
        plt.plot(day_mask_ic["longitude"][i], day_mask_ic["latitude"][i],  markersize=.2, marker='o', color='blue',label='IC')
    else:
        plt.plot(day_mask_ic["longitude"][i], day_mask_ic["latitude"][i],  markersize=.2, marker='o', color='blue')

#loop over cloud to ground and plot
num_cg=len(day_mask_cg["longitude"])
for i in range (num_cg-1):
    if i == 1:
        plt.plot(day_mask_cg["longitude"][i], day_mask_cg["latitude"][i],  markersize=1, marker='o', color='yellow',label='CG')
    else:
        plt.plot(day_mask_cg["longitude"][i], day_mask_cg["latitude"][i],  markersize=1, marker='o', color='yellow')
        ax1.coastlines(resolution='110m')

plt.legend(loc='lower left')
plt.savefig(dateins+'Brisbane_map.png')
plt.show()
