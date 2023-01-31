# README of Lightning Jump Detection Project

## Text File
### case_log.txt -- txt for storing the case studies and its corresponding centroid's coordinate

## Python File
## (***) Operation Process: cluster_track.py -> lightning_jump.py -> ts_plot.py / shi_collection.py
### LJ_FUNCTION.py -- Function Package that can be imported by other code file
### cluster_track.py -- Code for tracking the lightning cluster along time
### lightning_jump.py -- Code for detecting the lightning jump period in the specific area
### TS_plot.py -- Code for plotting the TS visualisation based on the user's preference
### shi_collection.py -- Code for collecting SHI information of each lightning jump within each cluster

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