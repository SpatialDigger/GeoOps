import geopandas as gpd
import pandas as pd
import json
import requests
import pprint


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

        # continue with the rest of the code
        print(f"Record Count = {count}, spliiting into {number_requests} requests")
        features = []
        while True:
            print(offset)
            query = f"{base_url}?where=1%3D1&f=geojson&resultOffset={offset}&resultRecordCount={rows_per_request}"
            gdf = gpd.read_file(query)
            if len(gdf) == 0:
                break
            features.append(gdf)
            offset += rows_per_request
        # features = gpd.GeoDataFrame(pd.concat(features, geometry=features, ignore_index=True))

        # # concatenate all dataframes in the list into a single geodataframe
        features = pd.concat(features, ignore_index=True)
        #
        # # convert the resulting dataframe into a geodataframe
        features = gpd.GeoDataFrame(features, geometry=features.geometry)

        return features
    elif file_path.endswith('.geojson'):
        with open(file_path) as f:
            data = json.load(f)
        return gpd.GeoDataFrame.from_features(data)
    else:
        print("File is not a shapefile or URL")
        return None


# url = "https://services-eu1.arcgis.com/ZOdPfBS3aqqDYPUQ/arcgis/rest/services/National_Heritage_List_for_England_NHLE/FeatureServer/3/query?outFields=*&where=1%3D1&f=geojson"
# read_files(url, rows_per_request=2000)
