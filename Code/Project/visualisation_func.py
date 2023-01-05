import os
import sys
import math
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
from statistics import stdev
from collections import Counter
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon
from datetime import datetime, timedelta, time

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
    instance_block = df_source.loc[(df_source["datetime"] >= start) & (df_source["datetime"] <= end)]

    # Create two groups of data for IC and CG lightning
    IC_df = instance_block.loc[(instance_block["stroke_type"] == "IC")]
    CG_df = instance_block.loc[(instance_block["stroke_type"] == "CG")]
    IC_df = IC_df.reset_index()
    CG_df = CG_df.reset_index()
    del IC_df["index"]
    del CG_df["index"]
    IC_df["within"] = False
    CG_df["within"] = False
    IC_df["type"] = "IC"
    CG_df["type"] = "CG"

    # Check the whether the instance's coordinate is within the Polygon or not (convert to sub-funciton later)
    for i in range(IC_df.shape[0]):
        if polygon_range.contains(Point(IC_df.iloc[i]["coordinate"])):
            IC_df.loc[i, "within"] = True
    for i in range(CG_df.shape[0]):
        if polygon_range.contains(Point(CG_df.iloc[i]["coordinate"])):
            CG_df.loc[i, "within"] = True

    IC_df = IC_df.loc[(IC_df["within"] == True)]
    CG_df = CG_df.loc[(CG_df["within"] == True)]
    ICCG = [IC_df, CG_df]
    ICCG_df = pd.concat(ICCG)

    # Return IC, CG instance dataframe for visualisation usage
    return IC_df, CG_df, ICCG_df

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

'''Function for generating the initial centroid of the major cluster'''
def initial_centroid(total_data, cluster_label_list):
    # Generate the centroid of the initial major cluster
    counter_list = Counter(cluster_label_list)
    major_value, major_count = counter_list.most_common()[0]
    ini_cluster = total_data.loc[total_data['Cluster_Label'] == major_value]
    points = MultiPoint(ini_cluster["coordinate"].tolist())
    centroid = points.centroid
    return centroid, False, ini_cluster.shape[0], major_value

'''Function for computing centroids of the current minutes (except initial moment)'''
def next_moment_cluster(total_data, check_cluster):
    # Generate the centroid(s) of the current minute's clusters
    centroids = []
    for i in check_cluster:
        current_cluster = total_data.loc[total_data["Cluster_Label"] == i]
        points = MultiPoint(current_cluster["coordinate"].tolist())
        centroid = points.centroid
        centroids.append([centroid.x, centroid.y])
    return centroids

'''Function for plotting the cluster(s) TS tracking plot'''
def cluster_track(filename, start_min, end_min, valid_jump):
    # Read in the CSV file for plotting
    path = 'Cluster_TSCSV/' + filename + ".csv"
    TS_data = pd.read_csv(path)

    # Plot the curve and save it as time-series visulisation
    # Set the X-axis Label
    timestamp_list = (pd.date_range("00:00", "23:59", freq="2min").time).tolist()
    for t in range(len(timestamp_list)):
        timestamp_list[t] = timestamp_list[t].strftime('%H:%M')
    label_time = timestamp_list.copy()
    for t in range(len(label_time)):
        if t % 100 == 0:
            continue
        else:
            label_time[t] = ""
    X_axis = [*range(start_min, end_min, 1)]

    # Plot the Graph
    for i in range(TS_data.shape[1]):

        # Record the lightning jump point for the target cluster
        target_cluster = str(i)
        LJ_happen = False
        LJ_happen_index = 0
        start_window = 0
        end_window = 6
        initial_LJ = True

        # Record the LJ Marker for TS Plotting
        jump_list = []
        cluster_list = TS_data[target_cluster].tolist()
        while end_window + 1 < len(cluster_list):
            feature = cluster_list[start_window:end_window]
            test = cluster_list[end_window-1:end_window+1]
            if LJ_Detection(feature, test, valid_jump) == True:
                if initial_LJ == True:
                    LJ_happen_index = end_window
                    initial_LJ = False
                    LJ_happen = True
                    jump_list.append(end_window)
                    print(str(i) + " LJ Happens " + str(end_window), timestamp_list[end_window])
                else:
                    if end_window - LJ_happen_index > 10:
                        LJ_happen_index = end_window
                        LJ_happen = True
                        jump_list.append(end_window)
                        print(str(i) + " LJ Happens " + str(end_window), timestamp_list[end_window])
                    else:
                        if LJ_happen == True:
                            LJ_happen_index = end_window
                            print(str(i) + " LJ Continues " + str(end_window), timestamp_list[end_window])
            else:
                if LJ_happen == True:
                    if cluster_list[end_window] <= 100:
                        print(str(i) + " LJ Stops " + str(end_window), timestamp_list[end_window])
                        LJ_happen = False
            start_window += 1
            end_window += 1

        # Plot the TS Plot of the Lightning Cluster with Point-Mark for Lightning Jump
        plt.plot(X_axis, TS_data[start_min:end_min][str(i)].tolist(), '-bo', markevery = jump_list, mfc='red', mec='k', label = "curve " + str(i))
        plt.legend()
        plt.xticks(X_axis, label_time, rotation='vertical')
        plt.savefig("Cluster_TSPlot/" + filename + "_" + str(i) + ".png")
        plt.close()

'''Function for detecting the lightning jump based on a sliding time-series window'''
'''https://louis.uah.edu/cgi/viewcontent.cgi?article=1232&=&context=uah-theses&=&sei-redir=1&referer=https%253A%252F%252Fscholar.google.com.au%252Fscholar%253Fhl%253Den%2526as_sdt%253D0%25252C5%2526q%253DAn%252Banalysis%252Bof%252Bthe%252Blightning%252Bjump%252Balgorithm%252Busing%252Bthe%252BGOES-16%252Bgeostationary%252Blightning%252Bmapper%2526btnG%253D#search=%22An%20analysis%20lightning%20jump%20algorithm%20using%20GOES-16%20geostationary%20lightning%20mapper%22'''
def LJ_Detection(prior_period, current_period, valid_jump):
    # Compute the sigma value (Standard Deviation of the previous 5 total changes)
    DFRDT = []
    DFRDT.append(prior_period[1] - prior_period[0])
    DFRDT.append(prior_period[2] - prior_period[1])
    DFRDT.append(prior_period[3] - prior_period[2])
    DFRDT.append(prior_period[4] - prior_period[3])
    DFRDT.append(prior_period[5] - prior_period[4])
    
    # Return True if there is a lightning jump detected based on the 2-sigma method
    if (current_period[1] >= valid_jump and current_period[0] >= 20):
        try:
            if (current_period[1] - current_period[0]) / stdev(DFRDT) >= 2:
                return True, (current_period[1] - current_period[0]) / stdev(DFRDT)
            else:
                return False, (current_period[1] - current_period[0]) / stdev(DFRDT)
        except:
            return False, 0
    else:
        return None, None
            
'''Function (sub) for plotting the blank map if there is no valid cluster at the investigated period'''
def blank_plot(target, minute, time, ax):
    # Plot all the lightning on a single day on a map
    ax.coastlines(resolution='110m')
    plt.legend(loc='lower left')
    plt.savefig('cluster_test/' + 'cluster_' + str(target) + '/' + str(minute) + "th_minute.png")

'''Function (sub) for plotting the cluster map if there is valid cluster at the investigated period'''
def cluster_plot(df, target, minute, ax):
    # Plot the visulisation for specific groups of lightning in the specified region
    for i in range(df.shape[0]):
        plt.plot(df.iloc[i]["longitude"], df.iloc[i]["latitude"], markersize=2, marker='o', color = "red")
    ax.coastlines(resolution='110m')
    plt.legend(loc='lower left')
    plt.savefig('cluster_test/' + 'cluster_' + str(target) + '/' + str(minute) + "th_minute.png")

'''Function (main) for plotting the cluster track visualisation'''
def target_cluster_plot(target, target_list, minute, time, ICCG, ax):
    # Plot all the lightning on a single day on a map
    if target_list[minute] == "NaN":
        blank_plot(target, minute, time, ax)
    else:
        # Select lightning instance based on the target cluster label
        df = ICCG.loc[ICCG["Cluster_Label"] == target_list[minute]]
        cluster_plot(df, target, minute, ax)

'''Function for recording the centroid (track) of the target cluster'''
def centroid_record(target_list, current_moment, ICCG, status):
    # If there is no lightning in the current time-interval, return NaN
    if status == False:
        return "NaN", 0, 0, 0, 0
    # If there is lightning in the current time-interval, return value based on different circumstance
    else:
        # If there is no valid cluster close to the previous investigated centroid, return NaN
        if target_list[current_moment] == "NaN":
            return "NaN", 0, 0, 0, 0
        # If there is a valid cluster, return the cluster centroid value as [x, y]
        else:
            df = ICCG.loc[ICCG["Cluster_Label"] == target_list[current_moment]]
            IC_num = (df.loc[df["stroke_type"] == "IC"]).shape[0]
            CG_num = (df.loc[df["stroke_type"] == "CG"]).shape[0]
            IC_amp = sum(abs((df.loc[df["stroke_type"] == "IC"])["amp"]))
            CG_amp = sum(abs((df.loc[df["stroke_type"] == "CG"])["amp"]))
            points = MultiPoint(df["coordinate"].tolist())
            centroid = points.centroid
            return [centroid.x, centroid.y], IC_num, CG_num, IC_amp, CG_amp

'''Function for counting the number of files in the target directory'''
def file_count(dir_path):
    count = 0
    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
    return count

'''Function for recording the LJ and Sigma Information for all cluster in the case study'''
def LJ_Info(dir_path, case_study, cluster_amount):
    # Record LJ and Sigma information for all cluster in the case study
    for i in range(cluster_amount):

        # Create Time Column
        timestamp_list = (pd.date_range("00:00", "23:59", freq="2min").time).tolist()
        for t in range(len(timestamp_list)):
            timestamp_list[t] = timestamp_list[t].strftime('%H:%M')

        # Define Variables
        fill_in_value = 0
        start_window = 0
        end_window = 6
        file_name = dir_path + "/" + case_study + str(i) + ".csv"
        
        # Read in the target cluster and generate the lightning amount list
        df_info = pd.read_csv(file_name)
        cluster_list = (df_info["IC_num"] + df_info["CG_num"]).tolist()

        # Initialise the list for recording the LJ and Sigma value
        LJ_list = [None] * end_window
        sig_list = [None] * end_window

        # Record the LJ and Sigma value base on LJ_Detection algorithm
        while end_window + 1 < len(cluster_list):
            feature = cluster_list[start_window:end_window]
            test = cluster_list[end_window-1:end_window+1]
            LJ, sig = LJ_Detection(feature, test, 20)
            LJ_list.append(LJ)
            sig_list.append(sig)
            start_window += 1
            end_window += 1
        
        # Write the LJ and Sigma column to the dataframe and store back to the CSV
        LJ_list.append(None)
        sig_list.append(None)
        df_info["LJ"] = LJ_list
        df_info["Sigma"] = sig_list
        df_info["Time"] = timestamp_list
        df_info.to_csv(file_name, index=False, header=True)