# README of Lightning Jump Detection Project

## Python File
### visulisation_func.py -- Function Package that can be imported by other code file
### cluster_track.py -- Code for tracking the lightning cluster along time
### lightning_jump.py -- Code for detecting the lightning jump period in the specific area

## Cluster_InfoCSV Folder
### this folder contains each case-study's cluster information, including lightning, amp, LJ and Sigma value 

## Cluster_TSCSV Folder
### Brisbane_2014-11-27.csv -- CSV records the tracking of the lightning amount along time within each cluster

## Cluster_TSPlot Folder
### Folder for storing the cluster track Time-Series Plot

## Preprocess_CSV Folder
### data_num.csv -- CSV contains number of lightning at each day during the investigated period

## Project Folder (***)(***)
### Folder for containing the source code of the core algorithm of the LJ Detection Project

# ---------------------------------------------------------------------------------------------------------------
# Redundant_Code Folder
## Python File
### preproecss.py -- Code for collecting the lightning amount at each day during the selected date range
### generic_visual.py -- Code for plotting the visulisation of lightning given the case area among the year
### PNGtoGIF.py -- Code for converting the folder of PNG(s) to a GIF for visualisation of the moving trend
### 1127_spec.py -- Code for investigating the Brisbane Lightning Case on 2014-11-27
### TS_plot.py -- Code for plotting the TS visualisation based on the user's preference

# Redundant_Data Folder
## Lightning_TSCSV Folder
### 20141127_Brisbane_6.csv -- CSV records the amount of lightning at each minute in Brisbane with range 6

## Lightning_TSPlot Folder
### AMP Folder -- Plots of AMP amount of selected lightning types in specific area during the range of time
### ICCG_VS Folder -- Plots of number of IC vs CG in specific area during the selected time
### TS_CG Folder -- Plots of number of CG lightning in specific area during the selected time
### TS_IC Folder -- Plots of number of IC lightning in specific area during the selected time
### TS_Total Folder -- Plots of number of Total lightning in specific area during the selected time

## Movement_GIF Folder
### Folder for storing the GIF of the cluster movement's visualisation

## YYYY-MM-DD_Visualisation Folder
### Folder for containing the generated PNG of lightning plot of map at each minutes in the specific area

## cluster_test Folder
### Folder for storing the visualisation of the target cluster's track pattern (used for making the GIF)
### The plots are stored in sub-folder for each specific cluster

## split_cluster_test Folder
### Folder for storing the splitted cluster(s) moving path track plot

## radar_plot Folder
### Folder for storing the radar plot of the severe hail index plot