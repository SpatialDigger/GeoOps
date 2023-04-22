import os
import glob
import rasterio
from rasterio import merge
import matplotlib.pyplot as plt
import time

# from geoops.geo_io import time_recording


def time_recording(type='start'):
    """
    Record the start time, end time, or duration of a process.

    Args:
        type (str): The type of time recording. Options are 'start', 'end', or 'duration'.
                    Defaults to 'start'.

    Returns:
        float or str or None: The recorded time or None if the type is invalid.
    """
    global start_time, end_time

    # Check if the type argument is valid
    if type not in ['start', 'end', 'duration']:
        print("Error: Invalid time recording type. Must be 'start', 'end', or 'duration'.")
        return None

    # Record the start time
    if type == 'start':
        start_time = time.time()
        return time.strftime("%H:%M:%S", time.localtime(start_time))
    # Record the end time
    elif type == 'end':
        end_time = time.time()
        return time.strftime("%H:%M:%S", time.localtime(end_time))
    # Calculate the duration
    elif type == 'duration':
        if start_time is not None and end_time is not None:
            duration = end_time - start_time
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            print("Error: Both start time and end time must be recorded.")
            return None

def merge_geotiffs(geotif_folder, out_folder, out_file_name='', recursive=False, crs=27700):
    """
    Merge multiple GeoTIFF files into a single raster using rasterio merge.

    Args:
        geotif_folder (str): Path to the folder containing the GeoTIFF files.
        out_folder (str): Path to the folder where the merged raster will be saved.
        out_file_name (str): Name of the output merged raster file. Default is 'dem.tif'.
        recursive (bool): Option to search for GeoTIFF files recursively in subdirectories. Default is False.

    Returns:
        None
    """
    # Record the start time
    start_time = time_recording('start')
    print(f"Start Time: {start_time}")

    # Check if all parameters are provided
    if not geotif_folder or not out_folder or not out_file_name:
        raise ValueError("geotif_folder, out_folder, and out_file_name are required parameters.")
    # Check if out_file_name ends with .tif
    if not out_file_name.endswith('.tif'):
        raise ValueError("out_file_name should end with '.tif'")

    # Use glob to get a list of GeoTIFF files in the input directory, with an option to search recursively
    geotiff_files = []
    if recursive:
        for dirpath, dirnames, filenames in os.walk(geotif_folder):
            for filename in filenames:
                if filename.endswith('.tif'):
                    geotiff_files.append(os.path.join(dirpath, filename))
    else:
        geotiff_files = glob.glob(os.path.join(geotif_folder, '*.tif'))

    # Create an empty list to store the selected geotiff files
    selected_geotiffs = []

    # Loop over each GeoTIFF file
    for file in geotiff_files:
        print(file)
        # Open the file with rasterio
        with rasterio.open(file) as src:
            # Get the bounding box of the raster
            selected_geotiffs.append(file)

    # Read the selected rasters into memory
    rasters = [rasterio.open(file) for file in selected_geotiffs]

    # Merge the rasters into a single raster
    merged, out_transform = merge.merge(rasters)

    merged = merged.squeeze()

    height, width = merged.shape

    # Write the masked merged raster to a new file using the specified output folder and file name
    out_file = os.path.join(out_folder, out_file_name)
    with rasterio.open(out_file, 'w', driver='GTiff', width=merged.shape[1], height=merged.shape[0],
                       count=1, dtype=merged.dtype, crs=crs, transform=out_transform) as dst:
        dst.write(merged, 1)
        dst.nodata = -9999  # Set the nodata value

    # Record the end time
    end_time = time_recording('end')
    print(f"End Time: {end_time}")

    # Calculate the duration
    duration = time_recording('duration')

    print(f"Duration: {duration}")
    print('processing complete')
    print(f'{len(selected_geotiffs)} tiffs merged to {os.path.join(out_folder, out_file_name)}')


def view_raster(raster_file, cmap='gray', min_value=0, display_meta=False, fig_size=(10, 10), display_axis=True):
    # Open the raster
    with rasterio.open(raster_file) as src:

        # Read in band1 of the raster
        raster = src.read(1)

        # Make sure the crs is used
        crs = src.crs
        transform = src.transform

    # Plot the raster
    fig, ax = plt.subplots(figsize=fig_size)
    ax.imshow(raster, cmap=cmap, extent=src.bounds, vmin=min_value)
    if display_axis:
        ax.set_axis_on()
    plt.show()
    if display_meta:
        # print out the meta data in case there are any issues to be followed up
        print(src.meta)

#
# def map_calculator(raster1, raster2, output_path, operation):
#     """
#     Perform a map calculation on two raster images and save the result to a new raster image.
#
#     Args:
#         input_path1 (str): Path to the first input raster image.
#         input_path2 (str): Path to the second input raster image.
#         output_path (str): Path to save the output raster image.
#         operation (str): The operation to perform on the input raster images. Supported operations are:
#                         'add': Addition
#                         'subtract': Subtraction
#                         'multiply': Multiplication
#                         'divide': Division
#                         'power': Exponentiation
#                         'min': Minimum
#                         'max': Maximum
#
#     Returns:
#         None
#     """
#     with rasterio.open(raster1) as src1, rasterio.open(raster2) as src2:
#         # Check if the input raster images have the same shape and CRS
#         if src1.shape != src2.shape or src1.crs != src2.crs:
#             raise ValueError("Input raster images must have the same shape and CRS")
#
#         # Perform the map calculation based on the operation
#         if operation == 'add':
#             result = src1.read(1) + src2.read(1)
#         elif operation == 'subtract':
#             result = src1.read(1) - src2.read(1)
#         elif operation == 'multiply':
#             result = src1.read(1) * src2.read(1)
#         elif operation == 'divide':
#             result = src1.read(1) / src2.read(1)
#         elif operation == 'power':
#             result = src1.read(1) ** src2.read(1)
#         elif operation == 'min':
#             result = rasterio.band((src1.read(1), src2.read(1))).min(axis=0)
#         elif operation == 'max':
#             result = rasterio.band((src1.read(1), src2.read(1))).max(axis=0)
#         else:
#             raise ValueError("Invalid operation. Supported operations are: 'add', 'subtract', 'multiply', 'divide', 'power', 'min', 'max'")
#
#         # Create the output raster image
#         profile = src1.profile
#         with rasterio.open(output_path, 'w', **profile) as dst:
#             dst.write(result, 1)




def raster_calculator(raster1, raster2, output_path, operation):
    # Open the input raster datasets
    src1 = rasterio.open(raster1)
    src2 = rasterio.open(raster2)

    # Read the raster bands as numpy arrays
    arr1 = src1.read(1)
    arr2 = src2.read(1)

    # Perform the specified operation
    if operation == 'add':
        result = arr1 + arr2
    elif operation == 'subtract':
        result = arr1 - arr2
    elif operation == 'multiply':
        result = arr1 * arr2
    elif operation == 'divide':
        result = arr1 / arr2
    elif operation == 'power':
        result = arr1 ** arr2
    elif operation == 'min':
        result = arr1 * arr2
        result = result.min(axis=0)
    elif operation == 'max':
        result = arr1 * arr2
        result = result.max(axis=0)

    # Write the result to the output raster
    profile = src1.profile
    profile.update(count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(result, 1)

    # Close the input raster datasets
    src1.close()
    src2.close()


import rasterio


def compute_raster_summary(raster_path, nodata=None, display_summary=False):
    """
    Compute summary statistics from a raster dataset, including nodata handling.

    Args:
        raster_path (str): The file path of the raster dataset.
        nodata (float or int, optional): The nodata value of the raster. Defaults to None.

    Returns:
        dict: A dictionary containing the computed summary statistics, including nodata count.
    """
    # Open raster dataset
    with rasterio.open(raster_path) as src:
        # Read raster data as a NumPy array
        raster_data = src.read(1)

        # Detect nodata value from raster metadata if not provided
        if nodata is None:
            nodata = src.nodata

        # Mask nodata values
        if nodata is not None:
            raster_data = raster_data[raster_data != nodata]

        # Compute summary statistics
        min_value = raster_data.min()
        max_value = raster_data.max()
        mean_value = raster_data.mean()
        std_value = raster_data.std()

        # Count nodata values
        nodata_count = 0
        if nodata is not None:
            nodata_count = (src.read(1) == nodata).sum()

        # Create a dictionary to store the summary statistics
        summary = {
            'minimum': min_value,
            'maximum': max_value,
            'mean': mean_value,
            'standard_deviation': std_value,
            'nodata': nodata,
            'nodata_count': nodata_count
        }
    if display_summary:
        print("Summary statistics for raster file:", raster_path)
        print("Minimum value:", summary['minimum'])
        print("Maximum value:", summary['maximum'])
        print("Mean value:", summary['mean'])
        print("Standard deviation:", summary['standard_deviation'])
        print("Nodata value:", summary['nodata'])
        print("Nodata count:", summary['nodata_count'])

    return summary


