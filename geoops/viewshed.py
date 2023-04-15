import rasterio
import numpy as np
from pyproj import Proj, transform

# line_of_sight_analysis('path/to/dem.tif', 'path/to/obs_points.csv', 'path/to/tgt_points.csv', 'path/to/tgt_height.tif')

import rasterio
import numpy as np
from pyproj import Proj, transform
from shapely.geometry import Point


def line_of_sight_analysis(dem_file, obs_points_gdf, tgt_points_gdf, tgt_height_file):
    # Load the DEM raster
    with rasterio.open(dem_file) as src:
        dem_data = src.read(1)
        dem_transform = src.transform
        dem_crs = src.crs

    # Convert the observation and target points to the DEM raster's CRS
    obs_points_gdf = obs_points_gdf.to_crs(dem_crs)
    tgt_points_gdf = tgt_points_gdf.to_crs(dem_crs)

    # Convert the observation and target points to numpy arrays
    obs_points = np.array([(p.x, p.y, p.z) for p in obs_points_gdf.geometry])
    tgt_points = np.array([(p.x, p.y, p.z) for p in tgt_points_gdf.geometry])

    # Calculate the line of sight for each target point from each observation point
    los_rasters = []
    for obs_point in obs_points:
        los_data = rasterio.warp.rasterize([(int(obs_point[0]), int(obs_point[1]))], out_shape=dem_data.shape,
                                           transform=dem_transform)
        los_rasters.append(los_data)

    # Convert the line of sight rasters to boolean arrays
    los_bools = []
    for los_raster in los_rasters:
        los_bool = los_raster.astype(bool)
        los_bools.append(los_bool)

    # For each target point, calculate the height below the sight line between the line and the DEM
    tgt_heights = []
    for tgt_point in tgt_points:
        tgt_height = np.zeros(dem_data.shape)
        for los_bool in los_bools:
            # Find the first index where the line of sight is True
            idx = np.argmax(los_bool[:, int(tgt_point[0]), int(tgt_point[1])])
            # Calculate the height below the sight line between the line and the DEM
            tgt_height[idx:, int(tgt_point[0]), int(tgt_point[1])] = dem_data[idx:, int(tgt_point[0]),
                                                                     int(tgt_point[1])] - (
                                                                                 obs_point[2] - tgt_point[2]) / (
                                                                                 idx - obs_point[2]) * np.arange(idx,
                                                                                                                 dem_data.shape[
                                                                                                                     0])[
                                                                                                       ::-1]
        tgt_heights.append(tgt_height)

    # Save the height below the sight line rasters to a file
    with rasterio.open(tgt_height_file, 'w', driver='GTiff', height=dem_data.shape[0], width=dem_data.shape[1],
                       count=len(tgt_heights), dtype=tgt_heights[0].dtype, crs=dem_crs, transform=dem_transform) as dst:
        for i, tgt_height in enumerate(tgt_heights):
            dst.write(tgt_height, i + 1)

