import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPoint
from shapely.ops import transform, unary_union, polygonize, cascaded_union
from osgeo import gdal
# import rasterstats
import numpy as np
from scipy.stats import skew, kurtosis
import pandas as pd

def filter_by_attribute(gdf, column, value):
    # TODO: write this function to handle various filtering methods
    # filter the geodataframe by an attribute value
    filtered_gdf = gdf.query('STATE_NAME == "California"')

    # filter the geodataframe by a spatial condition
    bbox = (-125, 31, -114, 43)  # define a bounding box as (minx, miny, maxx, maxy)
    filtered_gdf = gdf.cx[bbox]

def buffer(geometry, distance):
    """
    Applies a buffer of specified distance to all geometries in the list

    Status: untested
    """
    return geometry.buffer(distance)


def intersect(geometry1, geometry2):
    """
    Returns the intersection of two geometries.
    Status: untested
    """
    intersection = geometry1.intersection(geometry2)
    return intersection


def union():
    """
    Unions all shapes in the list and returns a single shape
    """
    union = shapes[0]
    for shape in shapes[1:]:
        union = union.union(shape)
    return union

def merge():
    """
    Merges all shapes in the list and returns a single shape
    """
    merged = gpd.GeoDataFrame(pd.concat(shapes, ignore_index=True), crs=shapes[0].crs)
    return merged

def create_polygon(coordinates):
    """
    Creates a polygon from a list of coordinates
    """
    polygon = Polygon(coordinates)
    return gpd.GeoDataFrame(geometry=[polygon], crs=shapes[0].crs)

def dissolve(by):
    """
    Dissolves all shapes in the list by specified column(s)
    """
    dissolved = gpd.GeoDataFrame(pd.concat(shapes, ignore_index=True), crs=shapes[0].crs)
    dissolved = dissolved.dissolve(by=by)
    return dissolved

def spatial_join(other, how='inner', op='intersects'):
    """
    Spatially join all shapes in the list with another shapefile
    """
    joined = shapes[0].spatial.join(other, how=how, op=op)
    for shape in shapes[1:]:
        joined = joined.spatial.join(shape, how=how, op=op)
    return joined

def centroid():
    """
    Computes the centroid of all shapes in the list and returns a single shape
    """
    centroid = shapes[0].centroid
    for shape in shapes[1:]:
        centroid = centroid.append(shape.centroid)
    return centroid

def line_to_point():
    """
    Converts all LineString and MultiLineString geometries in the list to Point geometries
    """
    points = []
    for shape in shapes:
        if shape.geom_type in ['LineString', 'MultiLineString']:
            points.append(shape.centroid)
        else:
            points.append(shape)
    return points

def polygon_to_line():
    """
    Converts all Polygon and MultiPolygon geometries in the list to LineString geometries
    """
    lines = []
    for shape in shapes:
        if shape.geom_type in ['Polygon', 'MultiPolygon']:
            lines.append(shape.boundary)
        else:
            lines.append(shape)
    return lines

def points_to_polygon(points):
    """
    Converts a list of Point geometries to a Polygon geometry
    """
    multipoint = MultiPoint([point.geometry for point in points])
    return Polygon(multipoint)

def convex_hull(points):
    """
    Computes the convex hull of a list of Point geometries
    """
    multipoint = MultiPoint([point.geometry for point in points])
    return multipoint.convex_hull

def concave_hull(points, alpha):
    """
    Computes the concave hull of a list of Point geometries using the alpha shape algorithm
    """
    multipoint = MultiPoint([point.geometry for point in points])
    alpha_shape = multipoint.alpha_shape(alpha)
    if isinstance(alpha_shape, Polygon):
        return alpha_shape
    else:
        return alpha_shape.convex_hull

def difference(geom1, geom2):
    """
    Computes the geometric difference between two geometries, returning a new geometry that represents the area of the first geometry minus the shared area with the second geometry.
    """
    return geom1.difference(geom2)

def symmetric_difference(geometry1, geometry2):
    """
    Computes the geometric symmetric difference between two geometries, returning a new geometry that represents the area of the first geometry that is not shared with the second geometry, plus the area of the second geometry that is not shared with the first geometry.
    """
    return geometry1.symmetric_difference(geometry2)

def simplify(geometry, tolerance=0.001, preserve_topology=True):
    """
    Simplifies a geometry by removing vertices while preserving its shape and topology, based on a specified tolerance or distance.
    """
    return geometry.simplify(tolerance, preserve_topology)

def affine_transform(geometry, matrix):
    """
    Applies an affine transformation to a geometry, which is a transformation that preserves parallelism and ratios of distances, for example, scaling, rotating, translating, or shearing a geometry.
    """
    return transform(lambda x, y, z=None: matrix @ (x, y), geometry)

def voronoi_diagram(points):
    """
    Computes the Voronoi diagram of a set of points, which is a partitioning of space into regions based on the closest point, and returns the boundaries of those regions as geometries.
    """
    voronoi_edges = polygonize(voronoi_diagram(points))
    return unary_union([edge.buffer(0.001) for edge in voronoi_edges if edge.length > 0])

def distance(geometry1, geometry2):
    return geometry1.distance(geometry2)

def within(geometry1, geometry2):
    return geometry1.within(geometry2)

def contains(geometry1, geometry2):
    return geometry1.contains(geometry2)

def crosses(geometry1, geometry2):
    return geometry1.crosses(geometry2)

def intersects(geometry1, geometry2):
    return geometry1.intersects(geometry2)

def overlaps(geometry1, geometry2):
    return geometry1.overlaps(geometry2)

def is_valid(geometry):
    return geometry.is_valid

def minimum_bounding_box(geometry):
    # Convert the input geometry into a MultiPoint object
    points = MultiPoint(list(geometry.exterior.coords))
    # Compute the minimum bounding box using the convex hull of the points
    hull = points.convex_hull
    # Convert the convex hull into a Polygon object
    polygon = Polygon(list(hull.exterior.coords))
    return polygon

def split_geometry(geometry, splitter):
    # Check if the splitter intersects the geometry
    if not geometry.intersects(splitter):
        return [geometry]
    # Check the geometry type
    if geometry.type == 'Polygon':
        # Split the polygon along the splitter
        parts = list(geometry.difference(splitter))
        # Return the resulting polygons
        return [part for part in parts if not part.is_empty]
    elif geometry.type == 'LineString':
        # Split the line string along the splitter
        parts = list(geometry.difference(splitter))
        # Return the resulting line strings
        return [part for part in parts if not part.is_empty]
    else:
        return []

def resample_raster(input_file, output_file, out_resolution):
    """
    Resamples a raster to a new resolution or grid size.

    Parameters:
        input_file (str): The file path of the input raster.
        output_file (str): The file path of the output raster.
        out_resolution (tuple): The target resolution of the output raster as (x_resolution, y_resolution).

    Returns:
        None
    """
    input_raster = gdal.Open(input_file)
    input_geotransform = input_raster.GetGeoTransform()
    input_projection = input_raster.GetProjection()
    input_band = input_raster.GetRasterBand(1)

    output_geotransform = list(input_geotransform)
    output_geotransform[1] = out_resolution[0]
    output_geotransform[-1] = -out_resolution[1]

    x_size = input_raster.RasterXSize
    y_size = input_raster.RasterYSize

    output_raster = gdal.GetDriverByName('GTiff').Create(output_file, x_size, y_size, 1, input_band.DataType)
    output_raster.SetProjection(input_projection)
    output_raster.SetGeoTransform(output_geotransform)

    gdal.ReprojectImage(input_raster, output_raster, input_projection, input_projection, gdal.GRA_Bilinear)
    output_raster.FlushCache()

def clip_vector(input_file, clip_file, output_file):
    """
    Clips a vector dataset to a boundary or a mask.

    Parameters:
        input_file (str): The file path of the input vector dataset.
        clip_file (str): The file path of the clip vector dataset.
        output_file (str): The file path of the output vector dataset.

    Returns:
        None
    """
    input_gdf = gpd.read_file(input_file)
    clip_gdf = gpd.read_file(clip_file)

    clipped_gdf = gpd.clip(input_gdf, clip_gdf)

    clipped_gdf.to_file(output_file, driver='ESRI Shapefile')



def polygon_in_polygon(geometry1, geometry2):

