import geopandas as gpd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def plot_geospatial_summary_stats(polygon_file, attribute):
    # Read in the polygon file as a GeoDataFrame
    polygons = gpd.read_file(polygon_file)

    # Calculate summary statistics for the given attribute
    stats = polygons[attribute].describe()

    # Add additional summary statistics
    stats['sum'] = polygons[attribute].sum()
    stats['median'] = polygons[attribute].median()
    stats['mean'] = polygons[attribute].mean()
    stats['std'] = polygons[attribute].std()
    stats['variance'] = polygons[attribute].var()
    stats['skewness'] = skew(polygons[attribute])
    stats['kurtosis'] = kurtosis(polygons[attribute])
    stats['range'] = polygons[attribute].max() - polygons[attribute].min()
    stats['iqr'] = np.subtract(*np.percentile(polygons[attribute], [75, 25]))
    stats['cv'] = (polygons[attribute].std() / polygons[attribute].mean()) * 100
    stats['geometric_mean'] = np.exp(np.mean(np.log(polygons[attribute])))
    stats['harmonic_mean'] = len(polygons[attribute]) / np.sum(1 / polygons[attribute])
    stats['mode'] = polygons[attribute].mode().values[0]
    stats['25th_percentile'] = np.percentile(polygons[attribute], 25)
    stats['75th_percentile'] = np.percentile(polygons[attribute], 75)

    # Create a figure with three subplots
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))
    sns.set(style="whitegrid")

    # Plot a histogram of the data
    sns.histplot(data=polygons, x=attribute, bins=20, ax=axs[0])
    axs[0].set_xlabel(attribute.capitalize())
    axs[0].set_ylabel("Count")

    # Plot a boxplot of the data
    sns.boxplot(data=polygons, x=attribute, ax=axs[1])
    axs[1].set_xlabel(attribute.capitalize())
    axs[1].set_ylabel("")

    # Plot a swarmplot of the data
    sns.swarmplot(data=polygons, x=attribute, ax=axs[2])
    axs[2].set_xlabel(attribute.capitalize())
    axs[2].set_ylabel("")

    # Add a title with the summary statistics
    fig.suptitle("Summary statistics for '{}'".format(attribute.capitalize()), fontsize=14, fontweight='bold', y=1.05)
    axs[0].set_title("Histogram\n\n" + str(stats))
    axs[1].set_title("Boxplot\n\n" + str(stats))
    axs[2].set_title("Swarmplot")

    plt.tight_layout()
    plt.show()
