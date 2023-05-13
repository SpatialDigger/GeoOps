'''
This is for any functions applied to geometry
'''


# Repair Geometry


from shapely.geometry import MultiPolygon
from shapely.validation import explain_validity
import pandas as pd


def fix_invalid_geometries(gdf):
    # split this apart into individual functions
    fixed_gdf = gdf.copy()

    # Check for missing geometries and remove the corresponding rows
    missing_geometries = fixed_gdf[fixed_gdf['geometry'].isna()]
    if not missing_geometries.empty:
        print("Rows with missing geometries have been removed:")
        print(missing_geometries)
    fixed_gdf = fixed_gdf[fixed_gdf['geometry'].notna()]

    for idx, geometry in fixed_gdf['geometry'].iteritems():
        if not geometry.is_valid:
            fixed_geometry = geometry.buffer(0)
            if fixed_geometry.geom_type == 'Polygon':
                fixed_geometry = MultiPolygon([fixed_geometry])
            fixed_gdf.loc[idx, 'geometry'] = fixed_geometry

            valid_reason = explain_validity(geometry)
            fixed_geom = explain_validity(fixed_geometry)
            print(f"Invalid geometry in GeoDataFrame: index {idx}: {valid_reason} \nResult: {fixed_geom}")

    return fixed_gdf


from pyproj import CRS


def check_crs(data, crs):
    """
    Checks the CRS of a geospatial dataset and applies the specified CRS
    if it has not been set or is different from the provided CRS.

    Args:
        data (geopandas.GeoDataFrame): Geospatial dataset to check CRS of.
        crs (dict or str): Target coordinate reference system to apply.

    Returns:
        geopandas.GeoDataFrame: Dataset with updated CRS.
    """
    # Check if CRS has been set
    if data.crs is None:
        data.crs = crs

    # Check if CRS is different
    elif data.crs != crs:
        try:
            crs = CRS.from_string(crs)
        except ValueError:
            pass
        data = data.to_crs(crs)

    return data


import geopandas as gpd
from shapely.geometry import Polygon


def create_square(bottom_left, width, crs="EPSG:27700"):
    """
    Create a square polygon with a given bottom left point and width.

    Parameters:
    -----------
    bottom_left: tuple
        The (x, y) coordinates of the bottom left corner of the square.

    width: float or int
        The width of the square.

    crs: str, optional (default: "EPSG:27700")
        The coordinate reference system (CRS) of the GeoDataFrame.

    Returns:
    --------
    gdf: geopandas.GeoDataFrame
        A GeoDataFrame containing a single row with the square polygon.
    """
    # Extract x and y coordinates of the bottom left corner
    x, y = bottom_left

    # Define the vertices of the square polygon
    vertices = [(x, y), (x, y + width), (x + width, y + width), (x + width, y)]

    # Create a Polygon object from the vertices
    polygon = Polygon(vertices)

    return gpd.GeoDataFrame(geometry=[polygon], crs=crs)


from pyproj import CRS

from forops.geo_ops.geo_io import read_data

def process_geospatial_data_to_dict(urls):
    """
    Process geospatial data from the provided URLs, handling reading, fixing invalid geometries,
    and checking CRS.

    Args:
        urls (dict): Dictionary containing URLs as values, with keys representing the data.

    Returns:
        dict: Dictionary containing processed geospatial data.
    """
    data = {}

    for key, value in urls.items():
        print(f"Reading: {key}")
        try:
            # Read geospatial data from URL
            data[key] = read_data(value)
        except Exception as e:
            print(f"Error reading files for {key}: {str(e)}")
            continue

        # Fix invalid geometries
        data[key] = fix_invalid_geometries(data[key])

        # Set 'status' to None before calling check_crs function
        data[key]['status'] = None

        try:
            # Check and apply CRS
            data[key] = check_crs(data[key], 'epsg:27700')
        except Exception as e:
            print(f"Error checking CRS for {key}: {str(e)}")
            continue

    return data


import geopandas as gpd
import pandas as pd


def chunk_geodataframe(gdf, chunk_size=100000):
    """
    Chunk a geodataframe into smaller pieces and return a generator that yields chunks.
    Args:
        gdf (geopandas.GeoDataFrame): The geodataframe to be chunked.
        chunk_size (int, optional): The maximum number of rows in each chunk. Defaults to 1000.
    Yields:
        geopandas.GeoDataFrame: A chunk of the original geodataframe.
    """
    for i in range(0, len(gdf), chunk_size):
        yield gdf.iloc[i:i + chunk_size]


def explode_geodataframe(gdf):
    """
    Explode a geodataframe into separate rows.
    Args:
        gdf (geopandas.GeoDataFrame): The geodataframe to be exploded.
    Returns:
        geopandas.GeoDataFrame: A new geodataframe with the geometries exploded into separate rows.
    """
    # Explode the geometries into separate rows
    gdf_exploded = gdf.explode(index_parts=True)

    # Reset the index
    gdf_exploded = gdf_exploded.reset_index(drop=False)
    count_exploded = len(gdf_exploded) - len(gdf)
    print(f"{count_exploded} polygons created")

    # Make a copy of the original GeoDataFrame
    gdf_original = gdf.copy()

    # Explode the MultiPolygon geometries
    gdf_exploded = gdf.explode(index_parts=True)

    return gdf_exploded


def reassemble_geodataframe(gdfs):
    """
    Reassemble a list of geodataframes into a single geodataframe.
    Args:
        gdfs (list of geopandas.GeoDataFrame): A list of geodataframes to be reassembled.
    Returns:
        geopandas.GeoDataFrame: A single geodataframe containing all the rows from the input geodataframes.
    """
    # Concatenate the geodataframes into a single geodataframe
    gdf = pd.concat(gdfs, ignore_index=True)

    return gdf


def cut_and_retain_intersection(gdf):
    print('cutting and retaining geometry')
    # Create a copy of the GeoDataFrame to avoid modifying the original
    gdf_cut = gdf.copy()

    gdf_cut['geometry'] = gdf_cut.geometry.intersection(gdf_cut.geometry.unary_union)

    return gdf_cut


def filter_geomtype(gdf, geom_type=['Polygon', 'MultiPolygon']):
    filtered_gdf = gdf[gdf.geometry.type.isin(geom_type)]
    return filtered_gdf


