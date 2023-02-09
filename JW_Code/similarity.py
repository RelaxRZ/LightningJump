from geopy.distance import geodesic
import numpy as np
from ast import literal_eval
from progress import printProgressBar
import pandas as pd

# Function used to change string "NaN" to np.nan
# Used in conjunction with df.apply and so that we analyse the lists properly
def change_nan(ls):
    return [np.nan if i == 'NaN' else i for i in ls] 

# Function used to change np.nan to string "NaN"
# Used in conjunction with df.apply and so that we can use literal_eval
def unchange_nan(ls):
    return ["NaN" if np.any(np.isnan(x)) else x for x in ls]


# Given two lists, return a list of tuples [(i1, i2), ...] where inside the tuples are the matching values indexes
def match_indexes(list1, list2):
    return [(i, j) for i, el1 in enumerate(list1) for j, el2 in enumerate(list2) if el1 == el2]


# Given a data frame, returns a dataframe conataining the cleaned severe weather events 
# (duplicates are removed) This only checks for inter cluster similarities not intra
def find_similarities(df):
    # resetting the indexes so that we do not accidentally delete multiple rows at once
    df = df.reset_index(drop = True) 

    # Masking empty LJ values
    df = df.mask(df["LJ"] == 'False')
    df.dropna(subset=['LJ'], inplace=True)


    # Masking empty max shi values
    df = df.mask(df['max_SHI'] == '')
    df = df.mask(df['max_SHI'] == 'No_File')
    df.dropna(subset=['max_SHI'], inplace=True)

    # Masking lightning jumps without severe weather
    df = df.mask(df['time_SHI'] == '')
    df = df.mask(df['time_SHI'] == 'No_File')
    df.dropna(subset=['time_SHI'], inplace=True)

    
    try:
        # Turn the list in string format to a proper python list
        df['max_SHI'] = df['max_SHI'].apply(literal_eval)
        # df['Coordinate'] = df['Coordinate'].apply(literal_eval)
        df['coor_SHI'] = df['coor_SHI'].apply(literal_eval)
        df['time_SHI'] = df['time_SHI'].apply(literal_eval)
        
        # Changes string formatted 'NaN' to numpy.nan for analysis
        df['max_SHI'] = df['max_SHI'].apply(change_nan)
        df['coor_SHI'] = df['coor_SHI'].apply(change_nan)
        df['time_SHI'] = df['time_SHI'].apply(change_nan)
    except:
        # print('lets keep on going and see how we go')
        a = 0

    removed = [] # keep a list of removed indexes

    # Iterate through the dataframe in reverse order
    for index1, row1 in reversed(list(df.iterrows())):
        t1 = row1["time_SHI"] 
        
        # If index has already been removed continue (so we do not have index errors)
        if index1 in removed: continue

        # Edge case check that max_SHI is not full of NaN values
        if np.isnan(row1['max_SHI']).all():
            df = df.drop(index1)
            continue
        
        # Nested loop to check for similarities
        for index2, row2 in reversed(list(df.iterrows())):
            # Edge case check that max_SHI is not full of NaN values
            if np.isnan(row2['max_SHI']).all():
                df = df.drop(index2)
                removed.append(index2)
                continue

            # Continue so that we do not double check rows
            if (index1 <= index2): continue

            # extract the list in a string format to a proper python list for the time of the SHI
            t2 = row2["time_SHI"]

            # Find the indexes where the time of SHI recording match up
            matches = match_indexes(t1, t2)

            # If there are less than 3 matching time points then we do not say there is a match
            time_match_count = len(matches)
            if time_match_count < 3: continue

            # Holder variables for the indexes of the matching time records
            f1 = [t[0] for t in matches]
            f2 = [t[1] for t in matches]

            # Extracting the max SHI at the indexes with the matching time records
            r1_shi = np.array([row1['max_SHI'][i] for i in f1], dtype=object)
            r2_shi = np.array([row2['max_SHI'][i] for i in f2], dtype=object)

            # Extracting the coordinates of the max SHI values
            r1_coor = np.array([row1['coor_SHI'][i] for i in f1], dtype=object)
            r2_coor = np.array([row2['coor_SHI'][i] for i in f2], dtype=object)

            # Given the overlapping time slots, find the index of the maximum of the 
            # max SHI values, we use a try except in case there are no shi values in the overlapping time frame
            try:
                max_index1 = np.nanargmax(r1_shi, dtype=object)
                max_index2 = np.nanargmax(r2_shi, dtype=object) 
            except:
                # print('we continue')
                # if there are no values in the overlapping time frame then we continue
                continue

            # Retrieving the max of the max SHI values
            max_SHI_1 = r1_shi[max_index1]
            max_SHI_2 = r2_shi[max_index2]

            # Retrieving coordinates of the max of the max shi values
            coord1 = r1_coor[max_index1]
            coord2 = r2_coor[max_index2]

            # Finding the absolute difference between the max shi vals
            max_shi_dist = np.abs(max_SHI_1-max_SHI_2)

            # Finding the km distance between the two maxes
            km_distance = geodesic(coord1, coord2).km

            # Checking on both conditions to ensure similarity
            if (max_shi_dist < 10) or (km_distance < 10):
                # print(f'removing row!!! row1; {index1} coordinate {coord1}, maxSHI: {max_SHI_1}')
                # print(f'removing row!!! row2; {index2} coordinate {coord2}, maxSHI: {max_SHI_2}\n\n')
                # if maxes are the same then drop the later event
                if (max_shi_dist == 0):
                    df = df.drop(index1)
                    break
                else:
                    # else drop the event with the smaller SHI
                    if (max_SHI_1 > max_SHI_2):
                        df = df.drop(index2)
                        removed.append(index2)
                        continue
                    else:
                        df = df.drop(index1)
                        break

    # we reverse the change on the row values so that later on we can use literal_eval again
    # dont ask me why this is just how it has to be
    df['max_SHI'] = df['max_SHI'].apply(unchange_nan)
    df['coor_SHI'] = df['coor_SHI'].apply(unchange_nan)
    # df['time_SHI'] = df['time_SHI'].apply(unchange_nan)
    
    return df
    
            



# Testing intra clusters similarities
# Sometimes two clusters find the same lightning jump, and thus we have to remove one of them to prevent bias
def intra_similiarity(df):
    df = df.reset_index(drop = True) # drop indexes so we do not accidentally remove multiple rows

    # count and progress bar print progress bar in terminal (ignore)
    l = len(df)
    if l == 0:
        return df
    count = 0
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # looping through the dataframe
    for index1, row1 in df.iterrows():
         # count and progress bar print progress bar in terminal (ignore)
        printProgressBar(count + 1, l, prefix = 'Progress (intra): ', suffix = 'Complete', length = 50)
        count += 1

        for index2 in range(index1, len(df)):
            if (np.allclose(row1['Coordinate'], df.loc[index2, "Coordinate"], atol=1e-06) and 
                        (row1['datetime'].time() == df.loc[index2, 'datetime'].time())):
                df.drop(index1, inplace = True)
                break

    return df

# returns a dataframe containing only the not validated lightning jumps
def remove_valid(df):
    df = df.reset_index(drop = True)
    # Masking empty LJ values
    df = df.mask(df["LJ"] == 'False')

    # masking validated rows
    # mask = ((df['time_SHI']!=''))#  | (df['max_SHI']!='No_File'))
    df = df.mask(pd.isna(df['time_SHI']) == False)

    # dropping empty rows
    df.dropna(subset=['LJ'], inplace=True)
    df.dropna(subset=['Sigma'], inplace=True)
    '''
    print(df['time_SHI'])
    print(type(df.loc[0]['time_SHI']))
    print(pd.isna(df.loc[0]['time_SHI']))
    print(np.isnan(df.loc[0]['time_SHI']))
    print((df.loc[0]['time_SHI'] == 'NaN'))
    '''
    # df.dropna(subset=['max_SHI'], inplace=True)
    # df.dropna(subset=['Coordinate'], inplace=True)
    
    # so we can check for intra similarity after
    
    return df

