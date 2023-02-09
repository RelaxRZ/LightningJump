import argparse
import os
import csv
import pandas as pd
import all_plots
import similarity
import sys
from ast import literal_eval
import regex as re

# Accept input from the job submission
narg=len(sys.argv)
if narg == 2:
    folder = sys.argv[1]

print(folder)


df_val = pd.DataFrame()
df_all = pd.DataFrame()
for file in os.listdir(folder):
    print(file)
    day, city = all_plots.name_extract(file)

    cluster_df = pd.read_csv(os.path.join(folder, file))

    cluster_df.dropna(subset=['Coordinate'], inplace=True)

    cluster_df['Coordinate'] = cluster_df['Coordinate'].apply(literal_eval)

    # Adding datetime to all rows
    cluster_df['datetime'] = cluster_df['Time'].apply(all_plots.add_datetime, date = day)

    # df containing all files, valid or not
    df_all = pd.concat([df_all, cluster_df])

    # Removing the invalidated rows, and inter cluster similarities
    cluster_df = similarity.find_similarities(cluster_df)

    df_val = pd.concat([df_val, cluster_df])

# Removes intra cluster similarities
df_val = similarity.intra_similiarity(df_val)
df_all = similarity.intra_similiarity(df_all)

# seperates valid and invalid rows
df_inval = similarity.remove_valid(df_all)

pattern = r'\w+_\d{4}-\d{2}-\d{2}'
match = re.search(pattern, folder)
folder_name = match.group(0)
print(folder_name)


df_val.to_csv(f"/g/data/er8/lightning/jonathan/daily_data_v1/valid/{folder_name}_valid.csv")
df_inval.to_csv(f"/g/data/er8/lightning/jonathan/daily_data_v1/invalid/{folder_name}_invalid.csv")



# /g/data/er8/lightning/chizhang/Cluster_InfoCSV/Variable_Case_1/Brisbane_2021-01-02

