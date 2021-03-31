import csv
from datetime import datetime

def group_by_xy(records, x_col, y_col, precision=-1):
    """Groups panoramas by their xy location.
    Records must be sorted by XY columns of interest!
    
    Arguments:
        records {List of lists} -- Contains records extracted from a Streetview database
        x_col {int} -- Index of x-coordinate column
        y_col {int} -- Index of y-coordinate column

    Keyword Arguments:
        precision {int} -- Number of digits used for grouping. -1 is all digits. (default: {-1})
    
    Returns:
        dict -- Contains records grouped by their anchor location as dict key
    """    
    groups = {}
    records_at_xy = []
    records = iter(records)

    # Initialize t-1
    prev_record = next(records)
    records_at_xy.append(prev_record)

    for record in records:
        # Check if panos are close enough to be considered at the same location
        if str(record[x_col])[:precision] != str(prev_record[x_col])[:precision]:
            if str(record[y_col])[:precision] != str(prev_record[y_col])[:precision]:
                groups[f'{prev_record[x_col]}-{prev_record[y_col]}'] = records_at_xy
                records_at_xy = []     
        records_at_xy.append(record)
        prev_record = record
    return groups

def get_xy_timestats(xy_records, x_col, y_col):
    """Calculates biggest timedif, min pano date, max pano date, and num. of distinct pano dates per anchor XY
    
    Arguments:
        anchor_records {dict} -- Dictionary with xy as keys and records at xy as entries
        x_col {int} -- Index of x-coordinate column
        y_col {int} -- Index of y-coordinate column        
    
    Returns:
        list -- List containing the xy and its biggest time difference
    """    
    xy_stats = []

    for a in xy_records:
        timestamps = [datetime.strptime(entry[2], '%Y-%m') for entry in xy_records[a]]
        min_time = min(timestamps)
        max_time = max(timestamps)
        num_timesteps = len(set(timestamps))

        month_timediff = 12 * (max_time.year - min_time.year) + (max_time.month - min_time.month)
        year_timediff = month_timediff/12

        xy_stats.append([xy_records[a][0][0],
                        xy_records[a][0][x_col],
                        xy_records[a][0][y_col],
                        min_time,
                        max_time,
                        month_timediff,
                        year_timediff,
                        num_timesteps])
    return xy_stats

# def plot_anchor_timediff(records, centerpoint, zoom=5):
#     map_obj = folium.Map(
#         location=centerpoint,
#         zoom_start=zoom
#     )

#     for r in records:
#         if r[-1] <= 2:
#             color = 'red'
#         elif r[-1] >= 3 and r[-1] < 6:
#             color = 'orange'
#         else:
#             color = 'green'

#         folium.Marker(
#             location=[r[1], r[0]],
#             #popup=f"{records[r][0][0]}",
#             icon=folium.Icon(color=color)
#         ).add_to(map_obj)
#     return map_obj
