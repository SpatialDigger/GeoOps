import rasterio
import numpy as np
from pyproj import Proj, transform

# line_of_sight_analysis('path/to/dem.tif', 'path/to/obs_points.csv', 'path/to/tgt_points.csv', 'path/to/tgt_height.tif')

import rasterio
import numpy as np
from pyproj import Proj, transform
from shapely.geometry import Point
import numpy as np
import rasterio
from shapely.geometry import Point, LineString

from geoops.geo_io import read_raster_file


import geopandas as gpd
import rasterio as rio
from shapely.geometry import Point, LineString

import geopandas as gpd
import rasterio as rio
from shapely.geometry import Point, LineString, MultiLineString

import rasterio as rio
import geopandas as gpd
from shapely.geometry import LineString

def calculate_line_of_sight(obs_point_gdf, tgt_points_gdf, raster_file):
    """
    Return a MultiLineString representing the line of sight between the observer and target points, with a
    "visible" column indicating whether each target point is visible from the observer point.

    Parameters:
        obs_point_gdf (GeoDataFrame): A GeoDataFrame containing the observer point.
        tgt_points_gdf (GeoDataFrame): A GeoDataFrame containing the target points.
        raster_file (str): A string representing the path to the DEM raster file.

    Returns:
        sightlines_gdf (GeoDataFrame): A GeoDataFrame containing the sightlines between the observer and target points,
        with a "visible" column indicating whether each target point is visible from the observer point.
    """
    # Read in the DEM raster
    with rio.open(raster_file) as dem:
        # Reproject the observer and target points to match the DEM
        obs_point_proj = obs_point_gdf.to_crs(dem.crs)
        tgt_points_proj = tgt_points_gdf.to_crs(dem.crs)

        # Extract the elevation value for the observer point
        obs_point_elev = float(next(rio.sample([(obs_point_proj.geometry.x[0], obs_point_proj.geometry.y[0])], dem)))

        # Calculate the line of sight between the observer and target points
        sightlines = []
        visible = []
        for i, tgt_point in tgt_points_proj.iterrows():
            # Extract the elevation value for the target point
            tgt_point_elev = float(next(rio.sample([(tgt_point.geometry.x, tgt_point.geometry.y)], dem)))

            # Calculate the line of sight between the observer and target points
            line = LineString([(obs_point_proj.geometry.x[0], obs_point_proj.geometry.y[0]),
                               (tgt_point.geometry.x, tgt_point.geometry.y)])

            # Sample the elevation values along the line of sight
            for point in rio.sample(list(line.coords), dem):
                if point[0] > obs_point_elev and point[0] > tgt_point_elev:
                    # If the elevation of the point is greater than the elevations of both the observer and target,
                    # then the target is visible
                    visible.append(1)
                    break
            else:
                # If the loop completes without finding a visible point, the target is not visible
                visible.append(0)

            # Add the sightline to the list of sightlines
            sightlines.append(line)

        # Create a GeoDataFrame from the sightlines and visible columns
        sightlines_gdf = gpd.GeoDataFrame(geometry=sightlines)
        sightlines_gdf["visible"] = visible

        return sightlines_gdf


#
#
# def line_of_sight_analysis(dem_file, obs_points_gdf, tgt_points_gdf, tgt_height_file):
#     # Load the DEM raster
#     with rasterio.open(dem_file) as src:
#         dem_data = src.read(1)
#         dem_transform = src.transform
#         dem_crs = src.crs
#
#     # Convert the observation and target points to the DEM raster's CRS
#     obs_points_gdf = obs_points_gdf.to_crs(dem_crs)
#     tgt_points_gdf = tgt_points_gdf.to_crs(dem_crs)
#
#     # Convert the observation and target points to numpy arrays
#     obs_points = np.array([(p.x, p.y, p.z) for p in obs_points_gdf.geometry])
#     tgt_points = np.array([(p.x, p.y, p.z) for p in tgt_points_gdf.geometry])
#
#     # Calculate the line of sight for each target point from each observation point
#     los_rasters = []
#     for obs_point in obs_points:
#         los_data = rasterio.warp.rasterize([(int(obs_point[0]), int(obs_point[1]))], out_shape=dem_data.shape,
#                                            transform=dem_transform)
#         los_rasters.append(los_data)
#
#     # Convert the line of sight rasters to boolean arrays
#     los_bools = []
#     for los_raster in los_rasters:
#         los_bool = los_raster.astype(bool)
#         los_bools.append(los_bool)
#
#     # For each target point, calculate the height below the sight line between the line and the DEM
#     tgt_heights = []
#     for tgt_point in tgt_points:
#         tgt_height = np.zeros(dem_data.shape)
#         for los_bool in los_bools:
#             # Find the first index where the line of sight is True
#             idx = np.argmax(los_bool[:, int(tgt_point[0]), int(tgt_point[1])])
#             # Calculate the height below the sight line between the line and the DEM
#             tgt_height[idx:, int(tgt_point[0]), int(tgt_point[1])] = dem_data[idx:, int(tgt_point[0]),
#                                                                      int(tgt_point[1])] - (
#                                                                                  obs_point[2] - tgt_point[2]) / (
#                                                                                  idx - obs_point[2]) * np.arange(idx,
#                                                                                                                  dem_data.shape[
#                                                                                                                      0])[
#                                                                                                        ::-1]
#         tgt_heights.append(tgt_height)
#
#     # Save the height below the sight line rasters to a file
#     with rasterio.open(tgt_height_file, 'w', driver='GTiff', height=dem_data.shape[0], width=dem_data.shape[1],
#                        count=len(tgt_heights), dtype=tgt_heights[0].dtype, crs=dem_crs, transform=dem_transform) as dst:
#         for i, tgt_height in enumerate(tgt_heights):
#             dst.write(tgt_height, i + 1)
#
