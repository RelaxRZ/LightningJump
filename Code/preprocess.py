import sys
import pandas as pd
from LJ_FUNCTION import spec_year

# Define Variable (date_range and date_format is changable)
date_range = 366
case_date = "2020-01-01"
date_format = "%Y-%m-%d"

# Directory with the data
dirin = '/g/data/er8/lightning/data/wz_ltng/'

# Obtain the csv file name and only read the 'date' data for preprocessing
filename = 'wz_ltng_' + case_date[0:4] + '.csv'
df = pd.read_csv(dirin + filename, sep=',', usecols=["date"])

# Count and store the number of lightning within each day from the target date range
date_num_dict = spec_year(case_date, date_range, date_format, df)
date_num_df = pd.DataFrame(date_num_dict.items(), columns = ["Date", "Lightning_Count"])
date_num_df.to_csv('/g/data/er8/lightning/chizhang/Preprocess_CSV/date_num_' + case_date[0:4] + '.csv', index=False, header=True)