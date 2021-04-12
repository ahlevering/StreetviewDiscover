""""
Author: Alex Levering (2021)
Example code on how to get statistics per polygon for panoramas

Sample data used are 4-digit post codes around the city center of Amsterdam,
Derived from the Dutch Statistics Office (CBS, 2017)
https://www.pdok.nl/introductie/-/article/cbs-postcode-statistieken
"""
from pathlib import Path
from datetime import datetime

import streetview
import geopandas as gpd
import pandas as pd

from svdiscover.pano_funcs import add_pano_stats_to_polygons
from svdiscover.database import StreetviewDB

## Region name
region_name = 'postcodes'

## Setup database & table
Path('output/databases/').mkdir(exist_ok=True)
sv_db_path = 'output/sv_imgs_ams.sqlite'

sv_db = StreetviewDB(sv_db_path, verbose=False)
sv_db.table = region_name

## Load target geometries
polys_file = f'geodata/postcodes_ams.geojson'
poly_geoms = gpd.read_file(polys_file)
poly_geoms = poly_geoms.to_crs('EPSG:4326')

## Subselect region polygon & clean fields
region_poly = poly_geoms[poly_geoms['postcode'] == '1011'] ## Select first region for this example
region_poly_cleaned = region_poly[['postcode', 'geometry']]
for col in ['earliest', 'earliest_year', 'latest', 'latest_year', 'mean_date', 'range_days', 'rel_earliest_days']:
    region_poly_cleaned[col] = -9999 # Assign nodata

# Get panorama info for region polygon
poly_with_timestats = add_pano_stats_to_polygons(sv_db, region_poly)

out_file = "output/neighbourhood_with_timestats.geojson"
poly_with_timestats.to_file(out_file, driver="GeoJSON")