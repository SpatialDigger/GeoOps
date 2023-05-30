'''
This is for any functions applied to geometry
'''


from shapely.validation import explain_validity
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
from pyproj import CRS
from ForestOps.geo_ops.geo_io import read_data

'''
Geodataframe Operations
'''

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
    return pd.concat(gdfs, ignore_index=True)


def fix_invalid_geometries(gdf):
    """
    Fix invalid geometries in a GeoDataFrame.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame with potentially invalid geometries.

    Returns:
        GeoDataFrame: GeoDataFrame with fixed geometries.
    """

    # Make a copy of the input GeoDataFrame
    fixed_gdf = gdf.copy()

    # Check for missing geometries and remove the corresponding rows
    missing_geometries = fixed_gdf[fixed_gdf['geometry'].isna()]
    if not missing_geometries.empty:
        print("Rows with missing geometries have been removed:")
        print(missing_geometries)
    fixed_gdf = fixed_gdf[fixed_gdf['geometry'].notna()]

    # Iterate over each geometry in the GeoDataFrame
    for idx, geometry in fixed_gdf['geometry'].iteritems():
        # Check if the geometry is invalid
        if not geometry.is_valid:
            # Fix the invalid geometry by buffering it with a distance of 0
            fixed_geometry = geometry.buffer(0)

            # Convert single Polygon to MultiPolygon if necessary
            if fixed_geometry.geom_type == 'Polygon':
                fixed_geometry = MultiPolygon([fixed_geometry])

            # Update the geometry in the GeoDataFrame with the fixed geometry
            fixed_gdf.loc[idx, 'geometry'] = fixed_geometry

            # Print information about the invalid and fixed geometries
            valid_reason = explain_validity(geometry)  # Assuming `explain_validity` is defined elsewhere
            fixed_geom = explain_validity(fixed_geometry)  # Assuming `explain_validity` is defined elsewhere
            print(f"Invalid geometry in GeoDataFrame: index {idx}: {valid_reason}\nResult: {fixed_geom}")

    return fixed_gdf


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


'''
Geospatial operations
'''


def cut_and_retain_intersection(gdf):
    """
    Cut the geometries of a GeoDataFrame using their intersection with the union of all geometries.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame.

    Returns:
        GeoDataFrame: GeoDataFrame with cut geometries.
    """
    print('cutting and retaining geometry')

    # Create a copy of the GeoDataFrame to avoid modifying the original
    gdf_cut = gdf.copy()

    # Perform intersection of each geometry with the union of all geometries
    gdf_cut['geometry'] = gdf_cut.geometry.intersection(gdf_cut.geometry.unary_union)

    return gdf_cut


def extract_overlapping_polygons(gdf1, gdf2):
    """
    Extract polygons from gdf1 that overlap with gdf2.

    Args:
        gdf1 (GeoDataFrame): First GeoDataFrame.
        gdf2 (GeoDataFrame): Second GeoDataFrame.

    Returns:
        GeoDataFrame: GeoDataFrame with overlapping polygons from gdf1.
    """
    # Perform a spatial join using 'intersects' operation
    intersection = gpd.sjoin(gdf1, gdf2, how='inner', predicate='intersects')

    # Extract the indices of polygons from gdf1 that overlap with gdf2
    overlapping_indices = intersection.index.unique()

    return gdf1[gdf1.index.isin(overlapping_indices)]


def extract_non_overlapping_polygons(gdf1, gdf2):
    """
    Extract polygons from gdf1 that do not overlap with gdf2.

    Args:
        gdf1 (GeoDataFrame): First GeoDataFrame.
        gdf2 (GeoDataFrame): Second GeoDataFrame.

    Returns:
        GeoDataFrame: GeoDataFrame with non-overlapping polygons from gdf1.
    """
    # Perform a spatial join using 'intersects' operation
    intersection = gpd.sjoin(gdf1, gdf2, how='left', predicate='intersects')

    # Extract the indices of polygons from gdf1 that do not overlap with gdf2
    non_overlapping_indices = intersection[intersection.index_right.isna()].index.unique()

    return gdf1[gdf1.index.isin(non_overlapping_indices)]


def clip_and_combine(gdf1, gdf2, column):
    """
    Clip and combine gdf1 with gdf2 based on their intersection.

    Args:
        gdf1 (GeoDataFrame): First GeoDataFrame.
        gdf2 (GeoDataFrame): Second GeoDataFrame.
        column (str): Name of the column to be added for indicating the intersection.

    Returns:
        Tuple: A tuple containing:
            - GeoDataFrame: Resulting GeoDataFrame after clipping and combining.
            - GeoDataFrame: GeoDataFrame representing the intersecting polygons.
            - GeoDataFrame: GeoDataFrame representing the non-intersecting polygons.
    """
    parcel_columns = gdf1.columns

    gdf_intersect = gpd.overlay(gdf1, gdf2, how='intersection', keep_geom_type=True)
    gdf_intersect = gdf_intersect.reindex(columns=parcel_columns)
    gdf_intersect[column] = True

    gdf_difference = gpd.overlay(gdf1, gdf2, how='difference', keep_geom_type=True)
    gdf_difference = gdf_difference.reindex(columns=parcel_columns)
    gdf_difference[column] = False

    result = gpd.GeoDataFrame(pd.concat([gdf_intersect, gdf_difference], ignore_index=True))

    result['area'] = result.area

    return result, gdf_intersect, gdf_difference

'''
Filters
'''

def filter_geomtype(gdf, geom_type=None):
    """
    Filter a GeoDataFrame based on the geometry types.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame.
        geom_type (list, optional): List of valid geometry types to retain. Defaults to ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection'].

    Returns:
        GeoDataFrame: Filtered GeoDataFrame.
    """
    if geom_type is None:
        geom_type = ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']

    return gdf[gdf.geometry.type.isin(geom_type)]


'''
Geometry
'''


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


'''
Functions yet to be grouped
'''


def plot_layers(gdf1, gdf2=None, title=None):
    """
    Plot GeoDataFrames on a single figure.

    Args:
        gdf1 (GeoDataFrame): First GeoDataFrame to be plotted.
        gdf2 (GeoDataFrame, optional): Second GeoDataFrame to be plotted. Defaults to None.
        title (str, optional): Title of the plot. Defaults to None.
    """
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the gdf1 GeoDataFrame
    gdf1.plot(ax=ax, facecolor='lightblue', edgecolor='blue')

    # Plot the gdf2 GeoDataFrame if provided
    if gdf2 is not None:
        gdf2.plot(ax=ax, facecolor='black', edgecolor='black', linewidth=1.5, alpha=0.5)

    # Set axis labels and title
    ax.set_xlabel('Easting')
    ax.set_ylabel('Northing')
    if title is not None:
        ax.set_title(title)

    # Set the axis limits based on the bounding box of gdf1
    ax.set_xlim(gdf1.total_bounds[0], gdf1.total_bounds[2])
    ax.set_ylim(gdf1.total_bounds[1], gdf1.total_bounds[3])

    # Show the plot
    plt.show()


def add_overlap_indicator(gdf1, gdf2, column_name):
    """
    Add an overlap indicator column to gdf1 based on its intersection with gdf2.

    Args:
        gdf1 (GeoDataFrame): First GeoDataFrame.
        gdf2 (GeoDataFrame): Second GeoDataFrame.
        column_name (str): Name of the column to be added.

    Returns:
        GeoDataFrame: gdf1 with the overlap indicator column added.
    """
    overlap = gpd.overlay(gdf1, gdf2, how='intersection')
    gdf1[column_name] = gdf1.index.isin(overlap.index)
    return gdf1


def print_unique_row_counts(gdf, column, disable=False):
    """
    Print the counts of unique rows based on the specified column.

    Args:
        gdf (GeoDataFrame): GeoDataFrame to count unique rows from.
        column (str): Column name for counting unique rows.
        disable (bool, optional): Flag to disable printing. Defaults to False.

    Returns:
        int: Number of unique rows.
    """
    # Calculate the count of unique rows based on the specified column
    unique_counts = gdf[column].value_counts()

    if not disable:
        # Iterate over the unique values and print the counts
        for value, count in unique_counts.items():
            print(f"Parcel ID: {value}, Count: {count}")
    return len(unique_counts)


def add_area(data, geometry_column, area_column, area_unit='ha'):
    """
    Add area information to the data.

    Args:
        data (GeoDataFrame): The input data containing the geometries.
        geometry_column (str): The name of the column containing the geometry.
        area_column (str): The name of the column to store the calculated area.
        area_unit (str, optional): The desired unit of the calculated area.
            Supported options: 'ha' (hectares, default), 'm' (square meters),
            'km' (square kilometers), 'ac' (acres), 'ft' (square feet).

    Returns:
        GeoDataFrame: The input data with the added area column.

    """
    # Add area information to the data

    if area_unit == 'ha':
        # Convert area to hectares (default)
        data[area_column] = data[geometry_column].area / 10000
    elif area_unit == 'm':
        # Keep area in square meters
        data[area_column] = data[geometry_column].area
    elif area_unit == 'km':
        # Convert area to square kilometers
        data[area_column] = data[geometry_column].area / 1000000
    elif area_unit == 'ac':
        # Convert area to acres
        data[area_column] = data[geometry_column].area / 4046.8564224
    elif area_unit == 'ft':
        # Convert area to square feet
        data[area_column] = data[geometry_column].area * 10.763910417
    return data
