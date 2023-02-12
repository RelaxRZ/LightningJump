# README of Lightning Jump Detection Project

## Text File
### variable_csse.txt -- txt for storing the variable case and its corresponding set of values

## Script File (Two Types of Operation Process)
## (**1**) Operation Process: cluster_track.qsub -> lightning_jump.qsub -> shi_collection.qsub
## (**2**) Operation Process: cluster_track_job.qsub -> lightning_jump_job.qsub -> shi_collection_job.qsub
#### cluster_track_job.qsub -- Script for the task to generate different case study's lightning cluster
#### cluster_track.qsub -- Script for the parallel processing to obtain yearly case study's lightning cluster
#### lightning_jump_job.qsub -- Script for the task to obtain different case study's lightning jump
#### lightning_jump.qsub -- Script for the parallel processing to obtain yearly case study's lightning jump
#### shi_collection_job.qsub -- Script for the task to obatin different case study's SHI information
#### shi_collection.qsub -- Script for the parallel processing to obtain yearly case study's SHI information

## Python File
#### LJ_FUNCTION.py -- Function Package that can be imported by other code file
#### cluster_track.py -- Code for tracking the lightning cluster along time
#### lightning_jump.py -- Code for detecting the lightning jump period in the specific area
#### ts_plot.py -- Code for plotting the TS visualisation based on the user's preference
#### shi_collection.py -- Code for collecting SHI information of each lightning jump within each cluster
#### preprocess.py -- Code for preliminary extracting the lightning instance from each yearly-record CSV
#### data_split.py -- Code for producing the daily CSV file by splitting the yearly-record CSV data
#### iccg_visual.py -- Code for plotting the visualisation of each case study's lightning data
#### script_creator.py -- Code for generating the sub-job script for processing different case study

## Cluster_InfoCSV Folder
#### Folder for storing case-study's cluster information, including lightning, LJ, SHI data under a variable case

## Cluster_TSCSV Folder
#### Folder for storing the summarised lightning cluster data for each case study under a variable case

## Cluster_TSPlot Folder
#### Folder for storing the cluster track Time-Series Plot

## ICCG_Plot Folder
#### Folder for storing the directory of the lightning data visualisation of each case study

## Job_Script Folder
#### Folder for storing the sub-job script for processing different case study

## Preliminary_Test Folder
#### Folder for containing the source code of the core algorithm of the LJ Detection Project for Testing

## Preprocess_CSV Folder
#### data_num_yyyy.csv -- CSV contains number of lightning at each day during the investigated year (yyyy)
#### yyyy Folder -- Folder contains the CSV for each day's data within the investigated year (yyyy)

-----------------------------------------------------------------------------------------------------------------
# Redundant_Code Folder
## Python File
#### preproecss.py -- Code for collecting the lightning amount at each day during the selected date range
#### generic_visual.py -- Code for plotting the visulisation of lightning given the case area among the year
#### PNGtoGIF.py -- Code for converting the folder of PNG(s) to a GIF for visualisation of the moving trend
#### 1127_spec.py -- Code for investigating the Brisbane Lightning Case on 2014-11-27

# Redundant_Data Folder
## cluster_test Folder
#### Folder for storing the visualisation of the target cluster's track pattern (used for making the GIF)
#### The plots are stored in sub-folder for each specific cluster

## Lightning_TSCSV Folder
#### 20141127_Brisbane_8.csv -- CSV records the amount of lightning at each minute in Brisbane with range 6

## Lightning_TSPlot Folder
#### AMP Folder -- Plots of AMP amount of selected lightning types in specific area during the range of time
#### ICCG_VS Folder -- Plots of number of IC vs CG in specific area during the selected time
#### TS_CG Folder -- Plots of number of CG lightning in specific area during the selected time
#### TS_IC Folder -- Plots of number of IC lightning in specific area during the selected time
#### TS_Total Folder -- Plots of number of Total lightning in specific area during the selected time

## Movement_GIF Folder
#### Folder for storing the GIF of the cluster movement's visualisation

## radar_plot Folder
#### Folder for storing the radar plot of the severe hail index plot

## split_cluster_test Folder
#### Folder for storing the splitted cluster(s) moving path track plot

## Resource Folder (** Contains Informative Data **)
#### Folder for storing the radar station location and case study CSV
