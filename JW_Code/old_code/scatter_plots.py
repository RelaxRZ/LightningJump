import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import csv
from datetime import datetime
import sys
import numpy as np
import cartopy.crs as ccrs
import scipy.stats
import re
import seaborn as sns
import numpy.ma as ma

# Plotting sigma vs shi data
def sigmaxshi(folder, file):

    pattern = r'Cluster\d+'
    match = re.search(pattern, file)
    cluster = match.group(0)

    date_pattern = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
    match2 = re.search(date_pattern, file)
    date = match2.group(0)


    df = pd.read_csv(folder + file)
    # Removing the empty data entries for lightning jumps
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)

    # Removing the empty data entries for SHI
    df['SHI'].replace('', np.nan, inplace=True)
    df.dropna(subset=['SHI'], inplace=True)

    # Choosing the lightning jumps

    lj = df.loc[df["LJ"] != "False"]

    plt.title(f"Sigma vs SHI: {year}-{month}-{date}_{cluster}.png")
    plt.xlabel("Severe Hail Index")
    plt.ylabel("Sigma")

    plt.scatter(lj['SHI'], lj['Sigma'])
    plt.savefig(f"Sigma_vs_SHI:_{year}-{month}-{date}_{cluster}.png")

# Plotting number of ic flashes against sigma values
def num_flashxsigma(folder, file):
    # Reading in all csv files
    df = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster0.csv')
    for i in range(19):
        cluster_num = i + 1
        temp = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster{cluster_num}.csv')
        df = pd.concat([df, temp])
    
    # Removing rows with empty LJ values
    df['LJ'].replace('', np.nan, inplace=True)
    df.dropna(subset=['LJ'], inplace=True)
    # Removing rows with empty sigma values
    df['Sigma'].replace('', np.nan, inplace=True)
    df.dropna(subset=['Sigma'], inplace=True)

    '''
    # Removing the empty data entries for ic and cg
    df['IC_num'].replace('', np.nan, inplace=True)
    df.dropna(subset=['IC_num'], inplace=True)

    # Removing the empty data entries for ic and cg
    df['CG_num'].replace('', np.nan, inplace=True)
    df.dropna(subset=['CG_num'], inplace=True)
    '''

    # False lightning jumps
    f_lj = df.mask(df["LJ"] != 'False')
    f_lj.dropna(subset=['LJ'], inplace=True)

    # Dropping the false lightning jumps
    df = df.mask(df["LJ"] == 'False')
    df.dropna(subset=['LJ'], inplace=True)

    # True lightning jumps, if previous LJ is equal to current LJ, remove
    t_lj = df.mask(df['LJ'].shift(1) == df['LJ'])
    t_lj.dropna(subset=['LJ'], inplace=True)

    # Continued lightning jumps, if previuous LJ is not equal to current LJ, remove
    cont_lj = df.mask(df['LJ'].shift(1) != df['LJ'])
    cont_lj.dropna(subset=['LJ'], inplace=True)

    # Plotting 2d hists of false, true, continued
    plt.hist2d(f_lj['IC_num'], f_lj['Sigma'], bins = 50, cmap = 'PuBuGn')
    plt.colorbar()
    plt.title("False LJ: ICxSIGMA")
    plt.xlabel("IC num")
    plt.ylabel("Sigma")
    plt.savefig(f"scatter_plots/bris_false_icXsigma.png")
    plt.close()
    
    plt.hist2d(t_lj['IC_num'], t_lj['Sigma'], bins = 50, cmap = 'Reds')
    plt.colorbar()
    plt.title("True LJ: ICxSIGMA")
    plt.xlabel("IC num")
    plt.ylabel("Sigma")
    plt.savefig(f"scatter_plots/bris_true_icXsigma.png")
    plt.close()
    
    cmap_reversed = plt.cm.get_cmap('hot_r')
    plt.hist2d(cont_lj['IC_num'], cont_lj['Sigma'], bins = 50, cmap = cmap_reversed)
    plt.colorbar()
    plt.title("Cont LJ: ICxSIGMA")
    plt.xlabel("IC num")
    plt.ylabel("Sigma")
    plt.savefig(f"scatter_plots/bris_cont_icXsigma.png")
    plt.close()
    

file = "Brisbane_2014-11-27_Cluster7.csv"
folder = "/g/data/er8/lightning/jonathan/Cluster_InfoCSV/Brisbane_2014-11-27/"

num_flashxsigma(folder, file)


# plotting the cdf and pdf of sigma values
def sigma_cdf_pdf(folder, file):

    # Reading in all csv files
    df = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster0.csv')
    for i in range(19):
        cluster_num = i + 1
        temp = pd.read_csv(f'{folder}Brisbane_2014-11-27_Cluster{cluster_num}.csv')
        df = pd.concat([df, temp])

    # Removing the empty data entries for Sigma
    df['Sigma'].replace('', np.nan, inplace=True)
    df.dropna(subset=['Sigma'], inplace=True)

    # Extracting wanted sigma values
    vals = df['Sigma']

    # Plotting two plots, pdf and cdf
    fi, (ax1, ax2) = plt.subplots(2, sharex=True)
    plt.title("pdf and cdf of Sigma values")

    # Allocating values into bins for pdf plot
    hist, bins = np.histogram(vals, bins=100, normed=True)
    bin_centers = (bins[1:]+bins[:-1])*0.5
    ax1.plot(bin_centers, hist)
    ax1.set_title('PDF of Sigma values')

    # Plotting cdf using sns
    ax2.set_title('CDF of Sigma values')
    sns.kdeplot(data = vals, cumulative = True)

    # Allocating the x axis intervals 
    plt.xticks(np.arange(-6, 12, 1.0))

    plt.xlabel("Sigma")
    plt.savefig("Sigma_pdf_cdf.png")

file = "Brisbane_2014-11-27_Cluster7.csv"
folder = "/g/data/er8/lightning/jonathan/Cluster_InfoCSV/Brisbane_2014-11-27/"

#sigma_cdf_pdf(folder, file)




    

