import all_plots
import pandas as pd 
from ast import literal_eval
import similarity




valid_path = 'severe_hail.csv'
# valid_path = 'severe_hail_case.csv'
invalid_path = 'invalid_bris_v2.csv'
# invalid_path = 'invalid_case_v3.csv'
def plot(valid_path, invalid_path):
    valid = pd.read_csv(valid_path)
    invalid = pd.read_csv(invalid_path)

    valid["datetime"] = pd.to_datetime(valid["datetime"])
    invalid["datetime"] = pd.to_datetime(invalid["datetime"])

    # Turn the list in string format to a proper python list
    valid['max_SHI'] = valid['max_SHI'].apply(literal_eval)
    valid['nonneg_90_SHI'] = valid['nonneg_90_SHI'].apply(literal_eval)
    valid['Coordinate'] = valid['Coordinate'].apply(literal_eval)
    valid['coor_SHI'] = valid['coor_SHI'].apply(literal_eval)
    valid['time_SHI'] = valid['time_SHI'].apply(literal_eval)

    invalid['Coordinate'] = invalid['Coordinate'].apply(literal_eval)
        
    # Changes string formatted 'NaN' to numpy.nan for analysis
    valid['max_SHI'] = valid['max_SHI'].apply(similarity.change_nan)
    valid['coor_SHI'] = valid['coor_SHI'].apply(similarity.change_nan)
    valid['nonneg_90_SHI'] = valid['nonneg_90_SHI'].apply(similarity.change_nan)

    ## all_plots.leadtime_x_sigma(valid)
    # all_plots.count_2dhist(valid)
    
    all_plots.hourly_dist(valid, invalid)
    ## all_plots.hourly_dist_IC(valid, invalid, density=False)
    ## all_plots.hourly_dist_total_sigma(valid, invalid, density=False)
    all_plots.monthly_dist_lj(valid, invalid, density=False)
    
    # all_plots.shi_x_sigma(valid)
    ## all_plots.shi_pdf(valid)
    ## all_plots.dist_x_leadtime(valid)
    # all_plots.leadtime_x_SHI(valid)
    ## all_plots.leadtime_pdf(valid)
    # all_plots.ic_pdf_valid_x_invalid(valid, invalid)
    
    # all_plots.time_series_avg_sigma(valid, invalid)
    # all_plots.time_series_avg_IC(valid, invalid)

plot(valid_path, invalid_path)
