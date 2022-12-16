import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from datetime import datetime, timedelta

'''Function for creating date list based on the given year'''
def spec_year(year_start, year_len, datetime_format, df):

    # Record all the dates between the specified start and end day
    start = datetime.strptime(year_start, datetime_format)
    date_generated = pd.date_range(start, periods = year_len)
    date_strlist = date_generated.strftime("%Y-%m-%d").tolist()

    # Create the dictionary which records the number of lightning instance at each day
    date_num_dict = {}
    for i in date_strlist:
        date_num_dict[i] = df.loc[df["date"] == i].shape[0]

    # Return the date list including the amount of lightning recorded
    return date_num_dict

'''Function for creating polygon of specific area given the centroid coodinate information and the range'''
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

'''Function for extracting the instance given the start and end timestamp'''
def ICCG_Collect(start, end, df_source, polygon_range):

    # Extract the lightning instance within the timestamp range
    instance_block = df_source.loc[(df_source["datetime"] > start) & (df_source["datetime"] < end)]

    # Create two groups of data for IC and CG lightning
    IC_df = instance_block.loc[(instance_block["stroke_type"] == "IC")]
    CG_df = instance_block.loc[(instance_block["stroke_type"] == "CG")]
    IC_df = IC_df.reset_index()
    CG_df = CG_df.reset_index()
    del IC_df["index"]
    del CG_df["index"]
    IC_df["within"] = False
    CG_df["within"] = False

    # Check the whether the instance's coordinate is within the Polygon or not (convert to sub-funciton later)
    for i in range(IC_df.shape[0]):
        if polygon_range.contains(Point(IC_df.iloc[i]["coordinate"])):
            IC_df.loc[i, "within"] = True
    for i in range(CG_df.shape[0]):
        if polygon_range.contains(Point(CG_df.iloc[i]["coordinate"])):
            CG_df.loc[i, "within"] = True

    IC_df = IC_df.loc[(IC_df["within"] == True)]
    CG_df = CG_df.loc[(CG_df["within"] == True)]

    # Return IC, CG instance dataframe for visualisation usage
    return IC_df, CG_df

'''Function to plot the IC, CG lightning in specific area'''
def plot_func(lig_data, lig_type):
    
    # Set the plot dot color for each type of lightning
    if lig_type == "IC":
        col = 'blue'
    else:
        col = 'red'

    # Plot the visulisation for specific groups of lightning in the specified region
    for i in range(lig_data.shape[0]):
        if i == 0:
            plt.plot(lig_data.iloc[i]["longitude"], lig_data.iloc[i]["latitude"], markersize=2, marker='o', color=col,label=lig_type)
        else:
            plt.plot(lig_data.iloc[i]["longitude"], lig_data.iloc[i]["latitude"], markersize=2, marker='o', color=col)
    
    return None

'''Function for obtaining the TS plot of the selected type of lightning recorded in the specific region during a selected range of time'''
def TS_Plot(start_min, end_min, lightning_type, date, location, width):
    
    # Read in the lightning TS csv with selected path
    path = "Lightning_TSCSV/" + date + "_" + location + "_" + str(width) + ".csv"
    TS_data = pd.read_csv(path)

    # Collect the lightning TS data, including type IC, CG, and Total
    TS_type = TS_data[lightning_type]

    # Collect the data points for plotting the line curve from the range of selected time
    plot_TS_type = TS_type[start_min:end_min].tolist()

    # Plot the curve and save it as time-series visulisation
    # Set the X-axis Label
    X_axis = [*range(start_min, end_min, 1)]

    # Plot the Graph
    plt.plot(X_axis, plot_TS_type)
    # naming the x axis
    X_tag = 'Minute Starts from: ' + str(start_min) + '~' + str(end_min)
    plt.xlabel(X_tag)
    # naming the y axis
    plt.ylabel('Lightning Amount')
    # TS Plot of Lightning in Brisbane 2014.11.27
    title = lightning_type + " Lightning on " + str(date) + ' in ' + location
    plt.title(title)
    
    # Show the plot
    plt.savefig("Lightning_TSPlot/" + "TS_" + lightning_type + "/" + date + "_" + location + "_" + str(width) + "_" + lightning_type)
    plt.close()

'''Function for plotting the IC, CG Lightning TS curves in one graph for comparison'''
def ICCG_Comp_Plot(start_min, end_min, date, location, width):
    
    # Read in the lightning TS csv with selected path
    path = "Lightning_TSCSV/" + date + "_" + location + "_" + str(width) + ".csv"
    TS_data = pd.read_csv(path)

    # Collect the lightning TS data, including type IC, CG, and Total
    TS_IC = TS_data["IC"]
    TS_CG = TS_data["CG"]

    # Collect the data points for plotting the line curve from the range of selected time
    plot_TS_IC = TS_IC[start_min:end_min].tolist()
    plot_TS_CG = TS_CG[start_min:end_min].tolist()

    # Plot the curve and save it as time-series visulisation
    # Set the X-axis Label
    X_axis = [*range(start_min, end_min, 1)]

    # Plot the Graph
    plt.plot(X_axis, plot_TS_IC, label = "curve IC")
    plt.plot(X_axis, plot_TS_CG, label = "curve CG")
    plt.legend()

    # naming the x axis
    plt.xlabel('Minute Starts from: ' + str(start_min) + '~' + str(end_min))
    # naming the y axis
    plt.ylabel('Lightning Amount')
    # TS Plot of Lightning in Brisbane 2014.11.27
    plt.title('TS of ' + "IC vs. CG" + " Lightning on " + str(date) + ' in ' + location)
    
    # Show the plot
    plt.savefig("Lightning_TSPlot/ICCG_VS/" + date + "_" + location + "_" + str(width))
    plt.close()

'''Function for plotting the AMP Amount TS curve'''
def AMP_Plot(start_min, end_min, date, location, width, amp_type):
    
    # Read in the lightning TS csv with selected path
    path = "Lightning_TSCSV/" + date + "_" + location + "_" + str(width) + ".csv"
    TS_data = pd.read_csv(path)

    # Collect the lightning TS data, including type IC, CG, and Total
    amp_data = TS_data[amp_type]

    # Collect the data points for plotting the line curve from the range of selected time
    plot_amp = amp_data[start_min:end_min].tolist()

    # Plot the curve and save it as time-series visulisation
    # Set the X-axis Label
    X_axis = [*range(start_min, end_min, 1)]

    # Plot the Graph
    plt.plot(X_axis, plot_amp, label = "curve " + amp_type)
    plt.legend()

    # naming the x axis
    plt.xlabel('Minute Starts from: ' + str(start_min) + '~' + str(end_min))
    # naming the y axis
    plt.ylabel('Amp Amount')
    # TS Plot of Lightning in Brisbane 2014.11.27
    plt.title('TS of ' + amp_type + " of Lightning on " + str(date) + ' in ' + location)
    
    # Show the plot
    plt.savefig("Lightning_TSPlot/AMP/" + date + "_" + location + "_" + str(width) + " " + amp_type)
    plt.close()