import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPoint
from shapely.ops import transform, unary_union, polygonize, cascaded_union
from osgeo import gdal
# import rasterstats
import numpy as np
from scipy.stats import skew, kurtosis

class GeospatialStatistics:

    def __init__(self, polygon_file, attribute):
        self.polygon_file = polygon_file
        self.attribute = attribute

    def zonal_statistics(self, raster_file, vector_file, stats=None):
        """
        Computes statistical measures for a set of raster cells or polygons that intersect with another set of polygons or regions.

        Parameters:
            raster_file (str): The file path of the input raster dataset.
            vector_file (str): The file path of the input vector dataset.
            stats (list): The statistical measures to compute as a list of strings. Default is None, which computes all stats.

        Returns:
            A dictionary containing the statistics for each polygon in the input vector dataset.
        """
        if stats is None:
            stats = ['min', 'mean', 'max', 'count', 'sum', 'std', 'median', 'majority']
        stats_dict = rasterstats.zonal_stats(vector_file, raster_file, stats=stats, nodata=-999)

        return stats_dict

    def geospatial_summary_stats(self, stats=None):
        # Read in the polygon file as a GeoDataFrame
        polygons = gpd.read_file(self.polygon_file)

        # Calculate summary statistics for the given attribute
        if stats is None:
            stats = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        desc_stats = polygons[self.attribute].describe(percentiles=[0.25, 0.5, 0.75])
        stats = desc_stats[stats].to_dict()

        # Add additional summary statistics
        stats['sum'] = polygons[self.attribute].sum()
        stats['skewness'] = skew(polygons[self.attribute])
        stats['kurtosis'] = kurtosis(polygons[self.attribute])

        # Additional statistics
        stats['range'] = polygons[self.attribute].max() - polygons[self.attribute].min()
        stats['iqr'] = np.subtract(*np.percentile(polygons[self.attribute], [75, 25]))
        stats['cv'] = (polygons[self.attribute].std() / polygons[self.attribute].mean()) * 100
        stats['geometric_mean'] = np.exp(np.mean(np.log(polygons[self.attribute])))
        stats['harmonic_mean'] = len(polygons[self.attribute]) / np.sum(1 / polygons[self.attribute])
        stats['mode'] = polygons[self.attribute].mode().values[0]

        return stats
