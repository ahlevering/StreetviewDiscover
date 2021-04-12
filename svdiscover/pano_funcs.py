import csv
from datetime import datetime

import geopandas as gpd
from shapely.geometry import Point

def add_pano_stats_to_polygons(pano_db, poly):
    """Adds panorama availability statistics of panoramas within an input polygon

    Args:
        pano_db (svdiscover.database.StreetviewDB): SQLite database containing panorama statistics
        poly (GeoPandas dataframe): Dataframe with polygon geometries

    Returns:
        GeoPandas dataframe: Input dataframe with added statistics
    """    
    # Accounting for GeoPandas geometry and Shapely polygon objects
    if type(poly['geometry'].bounds) == tuple:
        xmin, ymin, xmax, ymax = poly['geometry'].bounds
    else:
        xmin, ymin, xmax, ymax = poly['geometry'].bounds.values[0]
    
    # Get points which are inside of the extent of the polygon
    panos_in_approx_range = pano_db.get_records(f'(pano_x BETWEEN {xmin} AND {xmax}) AND (pano_y BETWEEN {ymin} AND {ymax})')
    ids_with_pts = {}
    for _,row in panos_in_approx_range.iterrows():
        ids_with_pts[row['pano_id']] = Point([row['pano_x'], row['pano_y']])
    
    # Keep only those points that intersect the polygon
    pano_ids_in_poly = [p for p in ids_with_pts if gpd.GeoSeries(poly['geometry']).intersects(ids_with_pts[p]).any()]
    panos_in_poly = panos_in_approx_range[panos_in_approx_range['pano_id'].isin(pano_ids_in_poly)]

    # Calculate pano stats over all panos in poly
    if not panos_in_poly.empty:
        poly = calculate_pano_timestats(poly, panos_in_poly)

    return poly

def calculate_pano_timestats(poly, panos):
    """From a dataframe of panoramas, calculates basic availability statistics for a given polygon

    Args:
        poly (GeoPandas dataframe): Dataframe with polygon geometries
        poly (Pandas dataframe): Dataframe with polygon geometries

    Returns:
        Geopandas dataframe: Input dataframe with added statistics
    """    
    # Calculate differences between earliest and latest panoramas
    earliest_pano_date = panos['capture_date'].min()
    latest_pano_date = panos['capture_date'].max()
    mean_pano_date = panos['capture_date'].mean()
    panos_range_days = (latest_pano_date - earliest_pano_date).days

    # Calculate time diffference to start of streetview
    FIRST_PANO_DATE = datetime(2005, 1, 1) # Streetview went into alpha in 2005, so 2005 is taken as the earliest possible date
    days_rel_to_earliest_date = (earliest_pano_date - FIRST_PANO_DATE).days    

    # Assign to row
    poly['earliest'] = str(earliest_pano_date.date())
    poly['earliest_year'] = int(earliest_pano_date.date().year)
    poly['latest'] = str(latest_pano_date.date())
    poly['latest_year'] = int(latest_pano_date.date().year)
    poly['mean_date'] = str(mean_pano_date.date())
    poly['rel_earliest_days'] = days_rel_to_earliest_date
    poly['range_days'] = panos_range_days

    return poly

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