# README of Jonathan Wu's part of the Lightning Jump Detection Project

# Python Files

# all_plots.py

## Functions
## name_extract(filename)
Inputs
- Sting: filename (city_yyy-mm-22_ClusterX.csv)
Outputs
- String: day
- String: city
- String: cluster

Takes in a filename and outputs the day, city, and cluster respectively.

## add_datetime(time, date)
Inputs
- String: time ("hh:mm")
- String: date ("yyyy-mm")
Outputs
- Datetime: datetime

Takes in a time and date and outputs a datetime variable, used with df.apply.

## count_2dhist(df)
Inputs
- Dataframe: df (vaild or invalid)

Takes in a dataframe containing lightning jumps and plots a 2d histogram based on their coordinates.

## clean_lj_topo(df)
Inputs
- Dataframe: df (valid or invalid)

Takes in a dataframe containing lightning jumps and plots their coordinates on top of a topographic map.

## leadtime_x_sigma(df)
Inputs
- Dataframe: df (valid data only)

Takes in a validated dataframe and plots the leadtime (time from lightning jump to time of severe weather) against the respective lightning jumps sigma value.

## hourly_dist(valid, invalid, **kwargs)
Inputs 
- Dataframe: valid (valid data only)
- Dataframe: invalid (invalid data only)
- **kwargs: specify (density=True) or (density=False)

Takes validated and invalialidated dataframes and plots a histogram of their hourly distribution (UTC time). Basically, how many lightning jumps per hour, for validated, and then for invalidated.

## hourly_dist_IC(valid, invalid, **kwargs)
Inputs 
- Dataframe: valid (valid data only)
- Dataframe: invalid (invalid data only)
- **kwargs: specify (density=True) or (density=False)

Takes validated and invalialidated dataframes and plots a histogram of their hourly distribution (UTC time). Basically, how many IC numbers hour, for validated, and then for invalidated.

## hourly_dist_total_sigma(valid, invalid, **kwargs)
Inputs 
- Dataframe: valid (valid data only)
- Dataframe: invalid (invalid data only)
- **kwargs: specify (density=True) or (density=False)

Takes validated and invalialidated dataframes and plots a histogram of their hourly distribution (UTC time). Basically, how many sigma values per hour, for validated, and then for invalidated.

## monthly_dist_lj(valid, invalid, **kwargs)
Inputs 
- Dataframe: valid (valid data only)
- Dataframe: invalid (invalid data only)
- **kwargs: specify (density=True) or (density=False)

Takes validated and invalialidated dataframes and plots a histogram of their monthly distribution (UTC time). Basically, how many sigma values per hour, for validated, and then for invalidated.

## shi_x_sigma(df)
Inputs
- Dataframe: df (valid data only)

Takes a validated dataframe and plots the average 90th percentile non negative SHI values against the lightning jumps sigma value.

## leadtime_pdf(df)
Inputs
- Dataframe: df (valid data only)

Takes a validated dataframe and plots the pdf of the leadtimes (time from lightning jump to time of severe weather)

## leadtime_x_SHI(df)
Inputs
- Dataframe: df (valid data only)

Takes a validated dataframe and plots the leadtimes against the SHI values (both maximum shi value and first shi value greater that 26.6)

## dist_x_leadtime(df)
Inputs
- Dataframe: df (valid data only)

Takes a validated dataframe and plots the distance from the lightning jump and severe weather event against the leadtime (time between lightning jump and severe weather) 

## shi_pdf(df)
Inputs
- Dataframe: df (valid data only)

Takes a validated dataframe and plots the pdf of all SHI values greater than 26.6

## time_series_avg_sigma(valid, invalid)
Inputs 
- Dataframe: valid (valid data only)
- Dataframe: invalid (invalid data only)

Takes a valid and invalid dataframe and plots average sigma value per hour in a time series plot



# all_plots.py

## Functions
## change_nan(ls)
Input
- A list containing string 'NaN'

Output
- The same list with np.nan instead of string 'NaN'

## unchange_nan(ls)
Input 
- A list containing np.nan

Output
- The same list with string 'NaN' instead of np.nan

## match_indexes(list1, list2)
Input 
- two lists

Output
- [(l1ind1, l2ind2), (l1ind2, l2ind2), ...]: returns a list of tuples containing the indexes at which both lists have the same value

## find_similarities(df):
Inputs
- dataframe

Output
- dataframe

Takes in a dataframe and cleans the rows. Removes different LJ same SW

## intra_similiarity(df)
Inputs
- dataframe
Output
- dataframe

Takes in a dataframe containing a whole days worth of data, removes lightning jumps that are identical
(intra cluster similarity checking)

## remove_valid(df)
Inputs
- dataframe
Output
- dataframe

Takes in a dataframe containing valid and invalid rows, removes all valid rows, and removes all rows without lightning jumps. Thus, we are left with only unmatched lightning jumps.

# call.py

## Functions
## split_severe_hail(path)
Inputs
- String: path to df containing validated hail and lj data (severe and non severe hail)

Splits this df into two differnet dfs one containing severe hail matched with lightning, and one containing non severe hail matched with lightning

## call_revised(path)
Inputs
- String: path to folder containing years worth of data

Reads years worth of data and outputs one df with validated data and invalidated data


# plot_runner.py

## Functions
## plot(valid_path, invalid_path)
Input
- String: path to valid dataframe
- String: path to invalid dataframe

Calls plot functions from all_plots.py

# script_writer.py

Given a years worth of data, generates 365 job scripts for parrallel processing

# file_processing.py

Given path arguments from script_writer jobs, processes the files, aka removes similarities and saves them into a folder.