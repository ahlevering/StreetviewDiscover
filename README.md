# StreetviewDiscover
Simple functions for discovering current and historic Google Streetview panorama IDs in polygons of a given region.

### Why?
Because Google currently doesn't provide overviews of the availability and reach of historic data for any given region. With this repo I hope to make it easier for people to find historic data for their desired region.

### How?
By hooking up readily-existing API wrappers with geo-operations so that users can look up the availability images in their own region. Currently the framework accepts polygon datasets as input, in which points are sampled. These points are used to check for panoramas at their respective location. For best results use a dataset of street polygons.

## Installing
Install Robolyst' Streetview wrapper separately

`pip install git+https://github.com/robolyst/streetview`

Then install this repo

`pip install git+https://github.com/Bixbeat/StreetviewDiscover`

### Usage
import the library using `import svdiscover`.

See the `Examples` folder for boilerplate code.

### Viewing the SQLite database
The best way to quickly view your data is by using the excellent [SQLite browser](https://sqlitebrowser.org/dl/). If you download the zip, you don't need to install any files either.
