import os
import glob
import rasterio
from rasterio import merge


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