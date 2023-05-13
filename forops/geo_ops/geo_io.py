import geopandas as gpd
import pandas as pd
import json
import requests
import pprint
import os
import rasterio

'''
This module read in or exports vector data
Question, should it handle raster data?
'''
# Read in Datasets
def get_record_limit(url):
    """
    Function to get the record limit from a REST API URL.

    Args:
        url (str): URL of the REST API.

    Returns:
        record_limit (int): Maximum number of records allowed in a request.

    """

    # Extract the base URL by removing any existing parameters
    base_url = url.split("/query?")[0]
    # Set the parameters for the request
    params = {"f": "json"}
    # Send a GET request to the base URL to retrieve the metadata
    response = requests.get(base_url, params=params)

    if response.ok:
        # Parse the response as JSON
        data = response.json()
        # Get the maximum record count from the metadata
        record_limit = data["tileMaxRecordCount"]
        return record_limit
    else:
        print(f"Error: {response.status_code} {response.reason}")
        return None


def get_feature_server_metadata(url):
    """
    Function to retrieve and print the metadata of a feature server.

    Args:
        url (str): URL of the feature server.

    """

    # Set the parameters for the request
    params = {"f": "json"}
    # Send a GET request to the URL to retrieve the metadata
    response = requests.get(url, params=params)

    if response.ok:
        # Parse the response as JSON
        data = response.json()
        # Print the metadata using pprint for better readability
        pprint.pprint(data)
    else:
        print(f"Error: {response.status_code} {response.reason}")


def get_feature_count(url):
    """
    Function to retrieve the feature count from a feature service URL.

    Args:
        url (str): URL of the feature service.

    Returns:
        count (int): Number of features in the service.

    """

    # Extract the base URL by removing any existing parameters
    base_url = url.split("?")[0]
    # Set the parameters for the request
    params = {
        "where": "1=1",  # Return count for all features
        "returnCountOnly": "true",  # Only retrieve the count, not the actual features
        "f": "json"  # Request metadata in JSON format
    }
    # Send a GET request to the base URL with the specified parameters
    response = requests.get(base_url, params=params)
    # Parse the response as JSON
    data = response.json()
    # Retrieve and return the feature count from the parsed JSON data
    return data["count"]


def read_from_url(file_path, rows_per_request, offset, crs):
    # Read data from a URL
    base_url = file_path.split("?")[0]  # remove any existing parameters
    count = get_feature_count(url=base_url)
    max_rows = get_record_limit(file_path)

    if rows_per_request == 0 or rows_per_request > max_rows:
        # Determine the number of rows per request based on the record limit
        if rows_per_request == 0:
            print(f"Record limit not set, using server limit of {max_rows}")
            rows_per_request = max_rows
        else:
            print(f"Limit exceeded, using server limit of {max_rows}")
            rows_per_request = max_rows

    number_requests = count / rows_per_request
    print(f"Record Count = {count}, splitting into {number_requests} requests")

    features = []
    while True:
        print(offset)
        # Construct the query URL
        query = f"{base_url}?outFields=*&where=1%3D1&f=geojson&resultOffset={offset}&resultRecordCount={rows_per_request}"
        # Read data from the query URL
        gdf = gpd.read_file(query)

        if len(gdf) == 0:
            break

        features.append(gdf)
        offset += rows_per_request

    gdf = gpd.GeoDataFrame(pd.concat(features, ignore_index=True))
    # Set the coordinate reference system (CRS)
    gdf = gdf.to_crs(crs)
    return gdf


def read_raster_file(raster_file):
    """
    Function to read a raster file using the rasterio library.

    Args:
        raster_file (str): Path to the raster file.

    Returns:
        raster_array (numpy.ndarray): Array containing the raster data.
        raster_profile (dict): Profile metadata of the raster.

    """

    # Open the raster file using rasterio
    with rasterio.open(raster_file) as raster:
        # Read the raster data into an array
        raster_array = raster.read(1)
        # Retrieve the profile metadata of the raster
        raster_profile = raster.profile

    # Return the raster array and profile
    return raster_array, raster_profile


def read_data(file_path, rows_per_request=0, offset=0, crs=27700):
    """
    Function to read geospatial data from different sources.

    Args:
        file_path (str): Path to the data file or URL.
        rows_per_request (int): Number of rows to request per API call (default: 0).
        offset (int): Offset value for pagination (default: 0).
        crs (int): Coordinate Reference System (CRS) code (default: 27700).

    Returns:
        gdf (geopandas.GeoDataFrame): Geospatial data as a GeoDataFrame.

    """

    # Check if the file path ends with specific extensions
    if file_path.endswith('.shp'):
        # Read shapefile
        return gpd.read_file(file_path)
    elif file_path.endswith('.geojson'):
        # Read GeoJSON file
        return gpd.read_file(file_path)
    elif file_path.endswith('.gpkg'):
        # Read GeoPackage file
        return gpd.read_file(file_path)
    elif file_path.endswith('.csv'):
        # This should be its own function
        # Read CSV file
        df = pd.read_csv(file_path)
        # Convert DataFrame to GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df.geometry))
        # Set the coordinate reference system (CRS)
        gdf = gdf.set_crs(crs)
        return gdf
    elif file_path.endswith('.gdb'):
        # Read file from a Geodatabase (.gdb)
        gpd.read_file(os.path.join(file_path))
    elif file_path.startswith('http://') or file_path.startswith('https://'):
        # Read data from a URL
        return read_from_url(file_path, rows_per_request, offset, crs)
        # base_url = file_path.split("?")[0]  # remove any existing parameters
        # count = get_feature_count(url=base_url)
        # max_rows = get_record_limit(file_path)
        #
        # if rows_per_request == 0 or rows_per_request > max_rows:
        #     # Determine the number of rows per request based on the record limit
        #     if rows_per_request == 0:
        #         print(f"Record limit not set, using server limit of {max_rows}")
        #         rows_per_request = max_rows
        #     else:
        #         print(f"Limit exceeded, using server limit of {max_rows}")
        #         rows_per_request = max_rows
        #
        # number_requests = count / rows_per_request
        # print(f"Record Count = {count}, splitting into {number_requests} requests")
        #
        # features = []
        # while True:
        #     print(offset)
        #     # Construct the query URL
        #     query = f"{base_url}?outFields=*&where=1%3D1&f=geojson&resultOffset={offset}&resultRecordCount={rows_per_request}"
        #     # Read data from the query URL
        #     gdf = gpd.read_file(query)
        #
        #     if len(gdf) == 0:
        #         break
        #
        #     features.append(gdf)
        #     offset += rows_per_request
        #
        # gdf = gpd.GeoDataFrame(pd.concat(features, ignore_index=True))
        # # Set the coordinate reference system (CRS)
        # gdf = gdf.to_crs(crs)
        # return gdf
    elif file_path.endswith('.geojson'):
        # Read GeoJSON file directly
        with open(file_path) as f:
            data = json.load(f)
        return gpd.GeoDataFrame.from_features(data)
    elif file_path.endswith('.tif'):
        raster_array, raster_profile = read_raster_file(file_path)
        return raster_array, raster_profile
    else:
        # Try reading the file assuming it's in a supported format
        try:
            return gpd.read_file(file_path)
        except Exception as e:
            print(f"Error reading file: {e}")
        return None


# Write out Datasets
def write_raster(filename, data, transform, crs):
    """
    Write a GeoTIFF raster using the given data, transform, and CRS.

    Args:
        filename (str): Output file name.
        data (numpy.ndarray): 2D numpy array of raster values.
        transform (affine.Affine): Affine transformation object.
        crs (rasterio.crs.CRS): CRS object.

    Returns:
        None.
    """
    height, width = data.shape
    count = 1
    dtype = data.dtype
    with rasterio.open(
        filename,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=count,
        dtype=dtype,
        crs=crs,
        transform=transform
    ) as dst:
        dst.write(data, 1)