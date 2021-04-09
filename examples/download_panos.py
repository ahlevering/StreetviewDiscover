""""
Author: Alex Levering (2021)
Example code on how to download panoramas stored in a pano-database
"""

import streetview
from svdiscover.database import StreetviewDB

# Get records
sv_db_path = 'output/sv_imgs_ams.sqlite'
sv_db = StreetviewDB(sv_db_path)
sv_db.table = 'postcodes'
all_records = sv_db.get_records()


# Download panoramas
my_google_api_key = '' # This is necessary for downloading. See the read-me on how to acquire a key.

for i,record in all_records.iterrows():
    heading = '' # By default: Gets forward-facing perspective
    
    # By default, Panoramas are saved by their year & pano-id
    streetview.api_download(record['pano_id'], heading, 'output/images/', my_google_api_key)