""""
Example code on how to export panoramas stored in a pano-database,
either by aggregating at anchor XY or by panos at the same location
"""

from svdiscover.database import StreetviewDB
from svdiscover.pano_funcs import group_by_xy, get_xy_timestats
from svdiscover.export import export_to_csv

## Setup database
sv_db_path = 'output/sv_imgs.sqlite'
sv_db = StreetviewDB(sv_db_path)
sv_db.table = 'postcodes_ams'
all_records = [rec for rec in sv_db.get_records()]

## Exporting panoramas taken at the same location
panos = group_by_xy(all_records, x_col=5, y_col=6, precision=6)
pano_stats = get_xy_timestats(panos, x_col=5, y_col=6)

header = ['subregion_name', 'pano_x', 'pano_y', 'min_time', 'max_time', 'month_timediff', 'year_timediff', 'num_timesteps']
export_to_csv("output/ams_pano_timestats.csv", pano_stats, header)

## Export panoramas at query anchorpoint
anchors = group_by_xy(all_records, x_col=3, y_col=4)    
anchors = get_xy_timestats(anchors, x_col=3, y_col=4)

header = ['subregion_name', 'anchor_x', 'anchor_y', 'min_time', 'max_time', 'month_timediff', 'year_timediff', 'num_timesteps']
export_to_csv("output/ams_anchor_timestats.csv", anchors, header)