""""
Author: Alex Levering (2021)
Example code on how to query panorama ids

Sample data used are 4-digit post codes around the city center of Amsterdam,
Derived from the Dutch Statistics Office (CBS, 2017)
https://www.pdok.nl/introductie/-/article/cbs-postcode-statistieken
"""
from random import shuffle
from pathlib import Path

import streetview
import geopandas as gpd

from svdiscover.sampling import sample_pts_in_poly, store_panos_from_sample_pts, reproject_to_wgs
from svdiscover.database import StreetviewDB

## Setup output path
Path('output').mkdir(exist_ok=True)

# Setup database
sv_db_path = 'output/sv_imgs_ams.sqlite'
sv_db = StreetviewDB(sv_db_path)
sv_db.make_region_table('postcodes', set_target=True)

## Load target geometries
pc4_file = 'examples/geodata/postcodes_ams.geojson'
pc4_polys = gpd.read_file(pc4_file)

# Settings
# With 20m we will acquire a very dense sampling, though some panos may be missed.
grid_resolution = 20 # Set this value to 200 if you want to quickly verify that everything works
in_proj = 'EPSG:28992' # RD New, the national Dutch coordinate system

## Get previously-queried regions from database
recorded_pcs = list(set([rec[0] for rec in sv_db.get_records()]))

# This can take a while to run as it needs to query the API many times for each polygon
for _,row in pc4_polys.iterrows():
    if not row['postcode'] in recorded_pcs: # Ignore previously handled postcodes
        print(row['postcode'])
        sample_pts = sample_pts_in_poly(row['geometry'], grid_resolution)
        reproj_pts = reproject_to_wgs(sample_pts, in_proj)
        sample_xy_pairs = [(float(pt.xy[0][0]), float(pt.xy[1][0])) for pt in reproj_pts] # Convert to XY tuples
        store_panos_from_sample_pts(sample_xy_pairs, row['postcode'], sv_db)