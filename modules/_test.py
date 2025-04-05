# AUTOGENERATED! DO NOT EDIT! File to edit: ../modules_nbs/_test.ipynb.

# %% auto 0
__all__ = [
    "cluster_mat",
    "generate_clustered_symmetric_matrix",
    "plot_matrix",
    "get_mat",
]


# %% ../modules_nbs/_test.ipynb 2
def cluster_mat(matrix_df):
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import pdist

    # Compute the distance matrix
    distance_matrix = pdist(matrix_df)

    # Perform hierarchical clustering
    linkage_matrix = linkage(distance_matrix, method="average")

    # Get the order of rows and columns from the clustering
    idx = leaves_list(linkage_matrix)

    # Reorder the DataFrame
    clustered_df = matrix_df.iloc[idx, :].iloc[:, idx]

    return clustered_df


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def generate_clustered_symmetric_matrix(size, cluster_size):
    """
    Generate a symmetric adjacency matrix with strongly clustered values.

    :param size: Total size of the symmetric adjacency matrix
    :param cluster_size: Size of each cluster
    :return: Clustered symmetric adjacency matrix as a numpy array
    """
    if isinstance(cluster_size, list):
        from functools import reduce

        return reduce(
            np.add,
            [
                generate_clustered_symmetric_matrix(size, cluster_size=i)
                for i in cluster_size
            ],
        )

    matrix = np.zeros((size, size))

    # Create clusters
    num_clusters = (size // cluster_size) + 1
    clusteris = list(range(num_clusters))

    for i in clusteris:
        start = i * cluster_size
        end = start + cluster_size
        if end > size:
            end = size
            cluster_size_ = end - start
        else:
            cluster_size_ = cluster_size
        cluster = np.random.rand(cluster_size_, cluster_size_)
        cluster = (cluster + cluster.T) / 2  # Make cluster symmetric
        matrix[start:end, start:end] = (
            cluster * 5
        )  # Scale up cluster values for stronger clustering

    import random

    flip = random.choice([True, False])
    if flip:
        matrix = np.fliplr(np.flipud(matrix))

    # Fill the rest of the matrix with smaller random values
    matrix += np.random.rand(size, size) * 0.5
    matrix = (matrix + matrix.T) / 2  # Ensure the entire matrix is symmetric
    return matrix


def plot_matrix(matrix):
    """
    Plot the given matrix using a heatmap.

    :param matrix: The matrix to be plotted
    """
    sns.heatmap(matrix, cmap="viridis")
    plt.show()


def get_mat(
    size=10,  # Define the size of the matrix
    cluster=True,
    cluster_sizes=None,
):
    import pandas as pd
    import numpy as np

    if not cluster:
        # Set a seed for reproducibility
        np.random.seed(0)

        # Generate a random adjacency matrix
        matrix = np.random.rand(size, size)

        # Since adjacency matrices are typically symmetric, make the matrix symmetric
        matrix = (matrix + matrix.T) / 2

    if cluster:
        # df=cluster_mat(df)
        if cluster_sizes is None:
            cluster_sizes = list(
                np.linspace(size * 0.15, size * 0.6, 10).astype(int)
            ) + list(np.linspace(size * 0.5, size, 5).astype(int))
        matrix = generate_clustered_symmetric_matrix(size, cluster_sizes)
    # plot_matrix(matrix)
    # Create a pandas DataFrame from the matrix
    np.fill_diagonal(matrix, 0)
    df = pd.DataFrame(
        matrix,
        columns=[f"n{i}" for i in range(size)],
        index=[f"n{i}" for i in range(size)],
    )
    return df
