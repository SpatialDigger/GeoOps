import geopandas as gpd
import pandas as pd
import json
import requests
import pprint
import pkgutil
import os
import tempfile


def get_record_limit(url):
    base_url = url.split("/query?")[0]  # remove any existing parameters
    params = {"f": "json"}
    response = requests.get(base_url, params=params)

    if response.ok:
        data = response.json()
        return data["tileMaxRecordCount"]
    else:
        print(f"Error: {response.status_code} {response.reason}")
        return None


def get_feature_server_metadata(url):
    params = {"f": "json"}
    response = requests.get(url, params=params)

    if response.ok:
        data = response.json()
        pprint.pprint(data)
    else:
        print(f"Error: {response.status_code} {response.reason}")


def get_feature_count(url):
    base_url = url.split("?")[0]  # remove any existing parameters
    params = {
        "where": "1=1",
        "returnCountOnly": "true",
        "f": "json"
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return data["count"]


def read_files(file_path, rows_per_request=0, offset=0, crs=27700):
    if file_path.endswith('.shp'):
        return gpd.read_file(file_path)
    elif file_path.startswith('http://') or file_path.startswith('https://'):
        base_url = file_path.split("?")[0]  # remove any existing parameters
        count = get_feature_count(url=base_url)
        max_rows = get_record_limit(file_path)
        if rows_per_request == 0 or rows_per_request > max_rows:
            # rows_per_request = max_rows
            if rows_per_request == 0:
                print(f"Record limit not set, using server limit of {max_rows}")
                rows_per_request = max_rows
            else:
                print(f"Limit exceeded, using server limit of {max_rows}")
                rows_per_request = max_rows
        number_requests = count / rows_per_request
        print(f"Record Count = {count}, spliiting into {number_requests} requests")
        features = []
        while True:
            print(offset)
            query = f"{base_url}?outFields=*&where=1%3D1&f=geojson&resultOffset={offset}&resultRecordCount={rows_per_request}"
            gdf = gpd.read_file(query)

            if len(gdf) == 0:
                break
            features.append(gdf)
            offset += rows_per_request
        gdf = gpd.GeoDataFrame(pd.concat(features, ignore_index=True))
        gdf = gdf.to_crs(crs)
        return gdf
    elif file_path.endswith('.geojson'):
        with open(file_path) as f:
            data = json.load(f)
        return gpd.GeoDataFrame.from_features(data)
    else:
        print("File is not a shapefile or URL")
        return None






def to_arcgis_geodb(data, gdb_path, name, schema=None, overwrite=True):
    if pkgutil.find_loader("arcpy") is not None:

        # Create a temporary directory and get its name
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a GeoDataFrame with some data
            data = gpd.GeoDataFrame({"id": [1, 2], "geometry": [Point(0, 0), Point(1, 1)]})

            # Write the GeoDataFrame to a temporary file in the temporary directory
            tmpfile = tmpdir + "/data.geojson"
            data.to_file(tmpfile, driver="GeoJSON")

            # Read the temporary file back into a new GeoDataFrame
            # new_data = gpd.read_file(tmpfile)

            # Do something with the new GeoDataFrame
            # print(new_data.head())

        # Check if the geometry type of the GeoDataFrame is 'Polygon'
        is_polygon = data.geometry.geom_type.isin(['Polygon']).all()

        if is_polygon:
            print('The GeoDataFrame contains only Polygon geometries.')
            geom_type = 'Polygon'
        else:
            print('The GeoDataFrame contains at least one non-Polygon geometry.')

        if schema is not None:
            pass
            # arcpy.conversion.JSONToFeatures(
            #     in_json_file=tmpfile,
            #     out_file=os.path.join(gdb_path, schema, name),
            #     geometry_type=geom_type
            # )
    else:
        print('arcpy not found, unable to write')

# url = "https://services-eu1.arcgis.com/ZOdPfBS3aqqDYPUQ/arcgis/rest/services/National_Heritage_List_for_England_NHLE/FeatureServer/3/query?outFields=*&where=1%3D1&f=geojson"
# read_files(url, rows_per_request=2000)
