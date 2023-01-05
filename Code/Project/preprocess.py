import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta
from visualisation_func import spec_year

# Variable define
date_range = 365
start_date = "2014-01-01"
date_format = "%Y-%m-%d"
year = start_date[0:4]

#directory with the data
dirin = '/g/data/er8/lightning/data/wz_ltng/'

# Obtain the csv file name and only read the 'date' data for preprocessing
filename = 'wz_ltng_' + year + '.csv'
df = pd.read_csv(dirin + filename, sep=',', usecols=["date"])

# Count and store the number of lightning within each day from the target date range
date_num_dict = spec_year(start_date, date_range, date_format, df)
date_num_df = pd.DataFrame(date_num_dict.items(), columns = ["Date", "Lightning_Count"])
date_num_df.to_csv('Preprocess_CSV/date_num.csv', index=False, header=True)