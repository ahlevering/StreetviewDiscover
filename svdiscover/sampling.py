from time import sleep
from math import floor, ceil

import streetview
import geopandas as gpd
from pyproj import Proj, CRS, Transformer
from shapely.geometry import MultiPoint
from shapely.ops import transform

def sample_pts_in_poly(poly_geom, grid_resolution=20):
    """Creates a point every n meters in a regular grid set by the grid resolution.
    Coordinate system of input geometry should be in meters (Use the UTM zone that intersects your polgyon if unsure)

    Arguments:
        poly_geom {shapely.geometry.polygon.Polygon} -- Target polygon in which points must fall
        grid_resolution {integer} -- Resolution in meters
    
    Keyword Arguments:
        n_samples {int} -- Number of points to sample. Default will sample based on polygon area (default: 20 meters)
    
    Returns:
        {shapely.geometry.MultiPoint} -- Shapely MultiPoint object containing all coordinate pairs
    """    
    xmin_orig, ymin_orig, xmax_orig, ymax_orig = poly_geom.bounds

    # Generate XY pairs with spacing set by the grid resolution
    xy_pairs = []
    for x in range(floor(xmin_orig), ceil(xmax_orig), grid_resolution):
        for y in range(floor(ymin_orig), ceil(ymax_orig), grid_resolution):
            xy_pairs.append((x, y))
    grid_points_in_extent = MultiPoint(xy_pairs)
    
    # Keep only points which intersect the input polygon
    sample_pts = poly_geom.intersection(grid_points_in_extent)

    return sample_pts

def reproject_to_wgs(geometry, in_proj, out_proj='EPSG:4326'):
    """Reprojects a Shapely geometry to an output projection

    Args:
        geometry (Shapely.geometry): [description]
        in_proj (str): EPSG description of the input project system
        out_proj (str, optional): EPSG description of the input project system. Defaults to 'EPSG:4326'.

    Returns:
        {Shapely.geometry}: The input Shapely geometry reprojected to the output projection
    """
    in_proj = CRS(in_proj)
    out_proj = CRS('EPSG:4326')        
    projection = Transformer.from_crs(in_proj, out_proj, always_xy=True).transform
    geom_resampled = transform(projection, geometry)
    return geom_resampled

def store_panos_from_sample_pts(sample_pts, subregion_name, sv_db):
    """Retrieves panoramas and stores them in a SQLite database
    
    Arguments:
        sample_pts {list} -- List of coordinate pairs
        subregion_name {str} -- Subregion name to fill in the region table
        sv_db {StreetviewDB} -- SQLite database for panorama IDs
    """    
    for sample_pt in sample_pts:
        entries = panos_from_coord_pair(sample_pt, subregion_name)
        if len(entries) > 0:
            for entry in entries:
                sv_db.add_entry(entry, manual_commit=True)
        sv_db.db.commit()
        sleep(0.01)


def panos_from_coord_pair(sample_pt, subregion_name=''):
    """Get all panoramas with a date from a coordinate pair
    
    Arguments:
        sample_pt {list} -- List containing an X and Y coordinate in WGS84 coordinates
    
    Keyword Arguments:
        subregion_name {str} -- Optional subregion name for keeping track of aggregations (default: {''})
    
    Returns:
        {list} -- List containing dictionaries of all panoramas at the coordinate pairs
    """
    try:    
        anchor_pano = streetview.panoids(lat=sample_pt[1], lon=sample_pt[0])
    except:
        print("Querying errors, retrying in 30 seconds")
        sleep(30)
        anchor_pano = streetview.panoids(lat=sample_pt[1], lon=sample_pt[0])

    entries = []
    if len(anchor_pano) > 0:
        for pano in anchor_pano:
            if 'year' in pano:
                entry = {'subregion_name': subregion_name,
                            'pano_id': pano['panoid'],
                            'capture_date': f'{pano["year"]}-{pano["month"]}',
                            'anchor_x': sample_pt[0],
                            'anchor_y': sample_pt[1],
                            'pano_x': pano['lon'],
                            'pano_y': pano['lat'],
                            'lookup_date': str(date.today()),
                            'download_date': '',
                            'saved_path': ''}
                entries.append(entry)
    return entries