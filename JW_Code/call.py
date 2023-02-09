import all_plots
import pandas as pd
import similarity
from ast import literal_eval
import os
from progress import printProgressBar
import numpy as np
import similarity




def split_severe_hail(path):
    df = pd.read_csv(path)

    # Turn the list in string format to a proper python list
    df['max_SHI'] = df['max_SHI'].apply(literal_eval)
        
    # Changes string formatted 'NaN' to numpy.nan for analysis
    df['max_SHI'] = df['max_SHI'].apply(similarity.change_nan)
    
    df_dict = df.to_dict('records')
    severe = []
    regular = []
    s = False
    for row in df_dict:
        print(row)
        for shi in row['max_SHI']:
            if np.isnan(shi):
                continue
            elif shi >= 26.6:
                s = True
                break
        if s:
            severe.append(row)
            s = False
        else:
            regular.append(row)
    
    s_df = pd.DataFrame(severe)
    r_df = pd.DataFrame(regular)

    s_df['max_SHI'] = s_df['max_SHI'].apply(similarity.unchange_nan)
    r_df['max_SHI'] = r_df['max_SHI'].apply(similarity.unchange_nan)


    s_df.to_csv("severe_hail_case.csv")
    r_df.to_csv('regular_hail_case.csv')

path = 'valid_case_v3.csv'

# split_severe_hail(path)


# Reading in a years worth of data
def call_revised(path):
    df_inval = pd.DataFrame() # valid rows all
    df_val = pd.DataFrame() # invalid rows all

    # print(os.path.join(subdir, file))
    # iterate through all dirs, subdirs and files
    for dirs in os.listdir(path):
        daily_df = pd.DataFrame() # df containing all rows valid and invalid for 1 day
        daily_df_val = pd.DataFrame() # df containing all rows vaild, for 1 day
        for file in os.listdir(os.path.join(path, dirs)):
            day, city = all_plots.name_extract(file)
            if city != "Brisbane": continue # Check only Brisbane data

            cluster_df = pd.read_csv(os.path.join(path, dirs, file))
            
            cluster_df.dropna(subset=['Coordinate'], inplace=True) # drop empty rows

            cluster_df['Coordinate'] = cluster_df['Coordinate'].apply(literal_eval) # change list in string format to proper list

            # Adding datetime to all rows
            cluster_df['datetime'] = cluster_df['Time'].apply(all_plots.add_datetime, date = day)
            
            # df containing all files, valid or not
            daily_df = pd.concat([daily_df, cluster_df])
            
            # Removing the invalidated rows, and inter cluster similarities
            cluster_df = similarity.find_similarities(cluster_df)
            
            # df_val only contains validated rows
            daily_df_val = pd.concat([daily_df_val, cluster_df])


        daily_df = similarity.intra_similiarity(daily_df) # remove intra similarity
        df_inval = pd.concat([df_inval, daily_df]) 

        daily_df_val = similarity.intra_similiarity(daily_df_val) # remove intra similarity
        df_val = pd.concat([df_val, daily_df_val])


    df_val.to_csv("valid_bris_v2.csv")

    df_inval = similarity.remove_valid(df_inval) # remove valid rows
    df_inval.to_csv("invalid_bris_v2.csv")

call_revised('/g/data/er8/lightning/chizhang/Cluster_InfoCSV/Variable_Case_3')

