import os
import sys
import json
import math
import cftime
import numpy as np
import pandas as pd
import numpy.ma as ma
from geopy import distance
import cartopy.crs as ccrs
from netCDF4 import Dataset
from collections import Counter
import matplotlib.pyplot as plt
from shapely.geometry import Point
from statistics import stdev, mean
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

'''Function for computing the start and end rows' index for selecting the case study from csv directly'''
def start_end_row(case_date):
    start_row = 1
    end_row = 1
    light_date = pd.read_csv('/g/data/er8/lightning/chizhang/Preprocess_CSV/date_num_' + case_date[0:4] + '.csv')
    for i in range(light_date.shape[0]):
        if light_date.iloc[i]["Date"] == case_date:
            break
        else:
            end_row += light_date.iloc[i]["Lightning_Count"]
    return start_row, end_row, light_date, i

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

'''Function for Obtaining the Lightning Amount Time-Series Visualisation with Lightning Jump(s) Marked in Red'''
def ClusterTS_Plot(main_dir, case_dir, gap):
    # Create sub-directory in ClusterTSPlot folder
    if not os.path.isdir(os.path.join("Cluster_TSPlot/", case_dir)):
        os.makedirs(os.path.join("Cluster_TSPlot/", case_dir))

    # Obtain the number of cluster from the case_study directory
    cluster_amount = file_count(main_dir + case_dir)

    # Plot the curve and save it as time-series visulisation
    # Set the X-axis Label
    timestamp_list = (pd.date_range("00:00", "23:59", freq = (str(gap) + "min")).time).tolist()
    for t in range(len(timestamp_list)):
        timestamp_list[t] = timestamp_list[t].strftime('%H:%M')
    label_time = timestamp_list.copy()
    for t in range(len(label_time)):
        if t % 100 == 0:
            continue
        else:
            label_time[t] = ""
    X_axis = [*range(0, len(label_time), 1)]

    # Plot all cluster(s)' time-series of lightning amount with Lightning Jump marked in red
    for i in range(cluster_amount):
        jump_dict = {}
        case_path =  main_dir + case_dir + "/" + case_dir + "_Cluster" + str(i) + ".csv"
        case_df = pd.read_csv(case_path)
        Y_axis = case_df[['IC_num', "CG_num"]].sum(axis = 1).tolist()

        LJ_Info = case_df["LJ"].tolist()
        for j in range(len(LJ_Info)):            
            if LJ_Info[j] == "False" or LJ_Info[j] == False or type(LJ_Info[j]) == float:
                continue
            else:
                if LJ_Info[j] in jump_dict.keys():
                    continue
                else:
                    jump_dict[LJ_Info[j]] = j
        jump_list = list(jump_dict.values())

        # Plot the TS Plot of the Lightning Cluster with Point-Mark for Lightning Jump
        plt.plot(X_axis, Y_axis, '-bo', markevery = jump_list, mfc='red', mec='k', label = "curve " + str(i))
        plt.legend()
        plt.xticks(X_axis, label_time, rotation='vertical')
        plt.savefig("Cluster_TSPlot/" + case_dir + "/" + case_dir + "_" + str(i) + ".png")
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
                return True, round((current_period[1] - current_period[0]) / stdev(DFRDT), 5)
            else:
                return False, round((current_period[1] - current_period[0]) / stdev(DFRDT), 5)
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

'''Function for calculating the distance in KM from the cluster centroid to other point(s)'''
def point_dist(centroid, candidate):
    # Compute the distance between the centroid and the point within that cluster
    point_centroid = [centroid.y, centroid.x]
    point_candidate = [candidate[1], candidate[0]]
    return (distance.distance(point_centroid, point_candidate).km)

'''Function for recording the centroid (track) of the target cluster'''
def centroid_record(target_list, current_moment, ICCG, status):
    # If there is no lightning in the current time-interval, return NaN
    if status == False:
        return "NaN", 0, 0, 0, 0, 0, 0
    # If there is lightning in the current time-interval, return value based on different circumstance
    else:
        # If there is no valid cluster close to the previous investigated centroid, return NaN
        if target_list[current_moment] == "NaN":
            return "NaN", 0, 0, 0, 0, 0, 0
        # If there is a valid cluster, return the cluster centroid value as [x, y]
        else:
            df = ICCG.loc[ICCG["Cluster_Label"] == target_list[current_moment]]
            IC_num = (df.loc[df["stroke_type"] == "IC"]).shape[0]
            CG_num = (df.loc[df["stroke_type"] == "CG"]).shape[0]
            IC_amp = round(sum(abs((df.loc[df["stroke_type"] == "IC"])["amp"])), 3)
            CG_amp = round(sum(abs((df.loc[df["stroke_type"] == "CG"])["amp"])), 3)
            points = MultiPoint(df["coordinate"].tolist())
            centroid = points.centroid
            
            # Record the scale of the investigated cluster at the specific time-interval
            scale_list = []
            for poi in df["coordinate"].tolist():
                scale_list.append(point_dist(centroid, poi))
            
            # Compute the density of lightning in the specific cluster
            scale_rad = mean(scale_list)
            dense = round((IC_num + CG_num) / (scale_rad ** 2 * math.pi), 3)
            return [centroid.x, centroid.y], round(mean(scale_list), 3), dense, IC_num, CG_num, IC_amp, CG_amp

'''Function for recording the lightning cluster related information to a list of dictionary'''
def centroid_record_func(centroid_record_list, track_cluster, k, j, ICCG, valid_cluster):
    centroid, scale, TOTD, IC_num, CG_num, IC_amp, CG_amp = centroid_record(track_cluster[k], j, ICCG, valid_cluster)
    centroid_record_list[k]["Coordinate"].append(centroid)
    centroid_record_list[k]["Scale_KM"].append(scale)
    centroid_record_list[k]["TOT_dense"].append(TOTD)
    centroid_record_list[k]["IC_num"].append(IC_num)
    centroid_record_list[k]["CG_num"].append(CG_num)
    centroid_record_list[k]["IC_amp"].append(IC_amp)
    centroid_record_list[k]["CG_amp"].append(CG_amp)
    return centroid_record_list

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
def LJ_Info(dir_path, case_study, cluster_amount, LJ_threshold):
    # Record LJ and Sigma information for all cluster in the case study
    for i in range(cluster_amount):

        # Create Time Column
        timestamp_list = (pd.date_range("00:00:00", "23:59:59", freq="2min").time).tolist()
        for t in range(len(timestamp_list)):
            timestamp_list[t] = timestamp_list[t].strftime('%H:%M:%S')

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
            LJ, sig = LJ_Detection(feature, test, LJ_threshold)
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

'''Function for removing the redundant lightning jump within the defined time-gap'''
def remove_RLJ(dir_path, case_study, cluster_amount, gap):
    # Record LJ and Sigma information for all cluster in the case study
    for i in range(cluster_amount):

        # Define Variables
        file_name = dir_path + "/" + case_study + str(i) + ".csv"
        
        # Read in the target cluster and load the lightning jump information
        df_info = pd.read_csv(file_name)
        LJ_list = df_info["LJ"].tolist()

        # Remove redundant lightning jump
        LJ_index = 0
        
        while LJ_index < len(LJ_list):
            if LJ_list[LJ_index] != True:
                LJ_index += 1
            else:
                loop_end = False
                for k in range(gap):
                    try:
                        if LJ_list[LJ_index + 1 + k] != True:
                            LJ_list[LJ_index + 1 + k] = "LJ_Continues"
                            if (k == (gap - 1)):
                                LJ_index += 1
                            else:
                                continue
                        else:
                            LJ_index += (k + 1)
                            break
                    except:
                        LJ_index = len(LJ_list)
        
        # Stored the updated LJ information to CSV
        df_info["LJ"] = LJ_list
        df_info.to_csv(file_name, index=False, header=True)

'''Function for allocating ID to each Seperated Lightning Jump within the Investigated Cluster'''
def LJ_ID(dir_path, case_study, cluster_amount, gap):
    # Record LJ and Sigma information for all cluster in the case study
    for i in range(cluster_amount):

        # Define Variables
        file_name = dir_path + "/" + case_study + str(i) + ".csv"
        
        # Read in the target cluster and load the lightning jump information
        df_info = pd.read_csv(file_name)
        LJ_list = df_info["LJ"].tolist()

        # Assign ID to each lightning jump (treat the lightning jumps as one if there are less than three LJ_continues in between)
        jump_ID = 0
        continue_count = 0
        for k in range(len(LJ_list)):
            if LJ_list[k] == "True":
                LJ_list[k] = "Jump_" + str(jump_ID)
                continue_count = 0

            elif LJ_list[k] == "LJ_Continues":
                continue_count += 1
                LJ_list[k] = "Jump_" + str(jump_ID)
                if continue_count == gap:
                    jump_ID += 1
                    continue_count = 0
        
        # Stored the updated LJ information to CSV
        df_info["LJ"] = LJ_list
        df_info.to_csv(file_name, index=False, header=True)

'''Function for collecting the matched radar ID of each lightning jump'''
def radar_ID(dir_path, case_study, cluster_amount, cluster_box_range, radar_dict):
    # Loop through all the cluster from the selected case study
    for i in range(cluster_amount):
        case_path = dir_path + "/" + case_study + str(i) + ".csv"
        case_df = pd.read_csv(case_path)
        case_LJ_list = case_df["LJ"].tolist()
        case_coor_list = case_df["Coordinate"].tolist()

        # Record the radar ID if lightning jump happens
        case_radar_list = []
        case_radar_coor_list = []
        last_jump = "Initial"
        for j in range(len(case_LJ_list)):     
            # If there is no lightning jump at the moment, record the radar ID as "NaN"
            if case_LJ_list[j] == "False" or case_LJ_list[j] == False or type(case_LJ_list[j]) == float:
                case_radar_list.append("NaN")
                case_radar_coor_list.append("NaN")
            
            # If there is lightning jump at the moment, record the radar ID base on different siuation(s) 
            else:
                # If the current jump is same as the previous one
                if case_LJ_list[j] == last_jump:
                    # If the preivous lightning jump does not match with any radar, record ID as "No_Radar"
                    if case_radar_list[j - 1] == "No_Radar":
                        case_radar_list.append("No_Radar")
                        case_radar_coor_list.append("No_Radar")
                    # If the previous lightning jump match with a radar, record ID as "SameJump"
                    else:
                        case_radar_list.append("Same_Jump")
                        case_radar_coor_list.append("Same_Jump")

                # If the current jump is a new jump
                else:
                    real_list = json.loads(case_coor_list[j])
                    min_lon, max_lon, min_lat, max_lat, area_polygon = polygon_func(real_list[0], real_list[1], cluster_box_range)
                    radar_covers_LJ = False
                    radar_lj_dist = 100
                    for radar in radar_dict:
                        # Record the radar station which is closest to the lightning jump centroid
                        if area_polygon.contains(Point(radar_dict[radar])):
                            if (math.dist(radar_dict[radar], real_list) < radar_lj_dist):
                                radar_lj_dist = math.dist(radar_dict[radar], real_list)
                                radar_covers_LJ = True
                                closest_ID = radar
                            
                    # If no radar is detected by the current jump, record its ID as "No_Radar"
                    if radar_covers_LJ == False:
                        case_radar_list.append("No_Radar")
                        case_radar_coor_list.append("No_Radar")
                        last_jump = case_LJ_list[j]
                    else:
                        case_radar_list.append(closest_ID)
                        case_radar_coor_list.append(radar_dict[closest_ID])
                        last_jump = case_LJ_list[j]

        # Store the radar ID information back to the CSV file
        case_df["radar_ID"] = case_radar_list
        case_df["radar_Coor"] = case_radar_coor_list
        case_df.to_csv(case_path, index = False, header = True)

'''Function for collecting the SHI information and store them into the CSV file of lightning cluster'''
def shi_Collect(cluster_amount, dir_path, case_study, cluster_box_range, level2_root, var_name, date, shi_time, last_moment, threshold):
    # Loop through all the cluster from the selected case study
    for i in range(cluster_amount):
        # Load in the CSV of lightning jump in each cluster
        case_path = dir_path + "/" + case_study + str(i) + ".csv"
        case_df = pd.read_csv(case_path)
        radar_list = case_df["radar_ID"].tolist()
        radar_coor_list = case_df["radar_Coor"].tolist()
        coor_list = case_df["Coordinate"].tolist()
        time_list = case_df["Time"].tolist()

        # List for recording the SHI information
        shi_list = []
        shi_90_list = []
        shi_time_list = []
        shi_coor_list = []
        shi_valid_size_list = []
        shi_invalid_size_list = []
        shi_valid_range_list = []
        previous_radar_ID = "Initial"
        # Record the SHI information based on lightning jump(s) in each cluster and the related radar station
        for j in range(len(radar_list)):
            # Record the SHI information as NaN if there no lightning jump
            if radar_list[j] == "No_Radar" or radar_list[j] == "Same_Jump" or type(radar_list[j]) == float or radar_list[j] == "NaN":
                shi_list.append("NaN")
                shi_90_list.append("NaN")
                shi_time_list.append("NaN")
                shi_coor_list.append("NaN")
                shi_valid_size_list.append("NaN")
                shi_invalid_size_list.append("NaN")
                shi_valid_range_list.append("NaN")
            else:
                # If there is lightning jump and there is a valid radar netCDF file, extract the SHI information
                try:
                    shi_path = level2_root + radar_list[j] + '/' + var_name.upper() + '/' + radar_list[j] + '_' + date + '_' + var_name + '.nc'
                    with Dataset(shi_path, mode = 'r') as shi_file:
                        # Create the lat-lon mask based the current lightning jump centroid
                        LJ_centroid = json.loads(coor_list[j])
                        min_lon, max_lon, min_lat, max_lat, area_polygon = polygon_func(LJ_centroid[0], LJ_centroid[1], cluster_box_range)
                        lat_grid = shi_file.variables['latitude'][:, :]
                        lon_grid = shi_file.variables['longitude'][:, :]
                        lat_mask = (lat_grid > min_lat) & (lat_grid < max_lat)
                        lon_mask = (lon_grid > min_lon) & (lon_grid < max_lon)
                        latlon_mask = lat_mask & lon_mask

                        # Compute the full valid range of a lightning jump box in an ideal case
                        RD_centroid = json.loads(radar_coor_list[j])
                        min_lon_RD, max_lon_RD, min_lat_RD, max_lat_RD, area_polygon = polygon_func(RD_centroid[0], RD_centroid[1], cluster_box_range)
                        lat_mask_RD = (lat_grid > min_lat_RD) & (lat_grid < max_lat_RD)
                        lon_mask_RD = (lon_grid > min_lon_RD) & (lon_grid < max_lon_RD)
                        latlon_mask_RD = lat_mask_RD & lon_mask_RD
                        ideal_valid_size = shi_file.variables["shi"][0, :, :].data[latlon_mask_RD].shape[0]

                        # Compute the valid & invalid region size of SHI detection for each lightning jump
                        valid_latlon_size = shi_file.variables["shi"][0, :, :].data[latlon_mask].shape[0]
                        radar_lat_size = shi_file.variables["shi"][0, :, :].shape[0]
                        radar_lon_size = shi_file.variables["shi"][0, :, :].shape[1]
                        valid_proportion = valid_latlon_size / radar_lat_size / radar_lon_size
                        invalid_size = ideal_valid_size - valid_latlon_size
                        shi_valid_size_list.append(valid_latlon_size)
                        shi_invalid_size_list.append(invalid_size)
                        shi_valid_range_list.append(round(valid_proportion, 4))

                        # Compute the time-range of the current lightning jump to extract the related SHI
                        time_datetime = cftime.num2date(shi_file.variables["time"][:], shi_file.variables["time"].units)                        
                        start = datetime.strptime((date[:4] + "-" + date[4:6] + "-" + date[6:] + " " + time_list[j]), '%Y-%m-%d %H:%M:%S')
                        end = start + timedelta(minutes = shi_time)

                        # Limit the time-range within the case-study day
                        if (end >= last_moment):
                            end = last_moment

                        # Create a time-range mask and extract the valid SHI data from the netCDF file
                        time_mask = (time_datetime >= start) & (time_datetime <= end)
                        shi_valid_time = shi_file.variables[var_name][time_mask, :, :]

                        # Store the time-slot of the valid SHI detected by the radar close to the current investigated lightning jump
                        date_time_list = cftime.num2date((np.array(shi_file.variables["time"][time_mask])), shi_file.variables["time"].units)
                        date_time_record = []
                        for dt_element in date_time_list:
                            date_time_record.append(dt_element.strftime('%H:%M:%S'))
                        shi_time_list.append(date_time_record)

                        # Extract the valid data from the preprocessed SHI data from time-range mask with the lat-lon mask
                        current_max_shi_list = []
                        nonneg_90_shi_list = []
                        coor_shi_list = []
                        lat_value = lat_grid[latlon_mask]
                        lon_value = lon_grid[latlon_mask]
                        
                        for k in shi_valid_time:
                            above_threshold_list = [x for x in k.data[latlon_mask].tolist() if x >= threshold]
                            if (len(above_threshold_list) == 0):
                                coor_shi_list.append("NaN")
                                current_max_shi_list.append("NaN")
                                nonneg_90_shi_list.append("NaN")
                            else:
                                max_index = np.argmax(k.data[latlon_mask].tolist())
                                coor_shi_list.append([lat_value[max_index], lon_value[max_index]])
                                current_max_shi_list.append(round(max(k.data[latlon_mask]), 4))
                                nonneg_90_shi_list.append(round(np.percentile(above_threshold_list, 90), 4))
                        shi_list.append(current_max_shi_list)
                        shi_90_list.append(nonneg_90_shi_list)
                        shi_coor_list.append(coor_shi_list)

                # If there is a lightning jump but no valid radar file, record 'No_File' into the SHI information list
                except:
                    shi_list.append("No_File")
                    shi_90_list.append("No_File")
                    shi_time_list.append("No_File")
                    shi_coor_list.append("No_File")
                    shi_valid_size_list.append("No_File")
                    shi_invalid_size_list.append("No_File")
                    shi_valid_range_list.append("No_File")

        # Store to the SHI information back to the cluster CSV
        case_df["max_SHI"] = shi_list
        case_df["nonneg_90_SHI"] = shi_90_list
        case_df["time_SHI"] = shi_time_list
        case_df["coor_SHI"] = shi_coor_list
        case_df["valid_size_SHI"] = shi_valid_size_list
        case_df["invalid_size_SHI"] = shi_invalid_size_list
        case_df["valid_range_SHI"] = shi_valid_range_list
        case_df.to_csv(case_path, index = False, header = True)

'''Function for writing basic information to the job script'''
def script_basic(job_file):
    job_file.write("#!/bin/bash\n")
    job_file.write("#PBS -l walltime=01:00:00\n")
    job_file.write("#PBS -l mem=20GB\n")
    job_file.write("#PBS -l ncpus=1\n")
    job_file.write("#PBS -l jobfs=20GB\n")
    job_file.write("#PBS -l storage=gdata/k10+gdata/hh5+scratch/k10+gdata/er8+scratch/er8+gdata/ra22+gdata/rq0\n\n")
    job_file.write("#PBS -l other=hyperthread\n")
    job_file.write("#PBS -q normal\n")
    job_file.write("#PBS -P er8\n\n")
    job_file.write("module use /g/data3/hh5/public/modules\n")
    job_file.write("module load conda/analysis3\n")
    job_file.write("conda\n\n")