import os
import pandas as pd
from LJ_FUNCTION import start_end_row

case_year = "2020"
light_date = pd.read_csv('/g/data/er8/lightning/chizhang/Preprocess_CSV/date_num_' + case_year + '.csv')
case_date_list = light_date["Date"].tolist()

# Obtain the csv file name and only read the 'date' data for preprocessing
filename='/g/data/er8/lightning/data/wz_ltng/wz_ltng_' + case_year + '.csv'

# Create the sub-directory for storing the lightning information in each day from the target year
dir_path = os.path.join('/g/data/er8/lightning/chizhang/Preprocess_CSV/', case_year)
if not os.path.isdir(dir_path):
    os.mkdir(dir_path)

# Compute the start and end rows of the case study from the csv and extract the data
for case_date in case_date_list:
    start_row, end_row, light_date, i_date = start_end_row(case_date)
    df_date = pd.read_csv(filename, sep=',', skiprows = range(start_row, end_row), nrows = light_date.iloc[i_date]["Lightning_Count"])
    df_date.to_csv(dir_path + "/data_num_" + str(case_date) + ".csv", index=False, header=True)