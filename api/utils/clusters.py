"""
This module contains various utility functions used for clustering the data.
"""

# =====
# SETUP
# =====
# Below, we'll set up the rest of the file

# General imports
from collections import Counter

# Third-party imports
import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_samples

# ================
# DEFINING METHODS
# ================
# Next, we'll define the methods we'll use to cluster the data


def cluster_conversations(conversation_embs_df: pd.DataFrame, n_clusters: int = 24):
    """
    Cluster conversations using MiniBatchKMeans and add cluster labels to DataFrame.

    Args:
        conversation_embs_df (pd.DataFrame): DataFrame containing conversation_id and embedding columns
        n_clusters (int): Number of clusters to generate

    Returns:
        pd.DataFrame: Copy of input DataFrame with added 'cluster' column containing string cluster IDs
    """

    # Convert embeddings from object to numpy array
    embeddings_array = np.stack(conversation_embs_df["embedding"].values)

    # Initialize and fit MiniBatchKMeans
    minibatch_kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
    )
    cluster_labels = minibatch_kmeans.fit_predict(embeddings_array)

    # Calculate number of digits needed for zero padding based on n_clusters
    n_digits = len(str(n_clusters - 1))

    # Create copy of DataFrame and add zero-padded string cluster labels
    result_df = conversation_embs_df.copy()
    result_df["cluster"] = [
        f"cluster_{str(label).zfill(n_digits)}" for label in cluster_labels
    ]

    # Sort according to cluster
    result_df = result_df.sort_values(by="cluster")

    return result_df


def calculate_cluster_metrics(
    cluster_df: pd.DataFrame,
    n_centroid_docs: int = 8,
    max_n_tags_per_cluster: int = 15,
):
    """
    Calculates metrics for each cluster including centroid conversations, tag counts, similarities and quality metrics.

    Args:
        cluster_df (pd.DataFrame): DataFrame containing the following columns:
            "conversation_id", "embedding", "cluster", "tags"
        n_centroid_docs (int): Number of centroid documents to find per cluster
        max_n_tags_per_cluster (int): Maximum number of tags to store per cluster

    Returns:
        pd.DataFrame: DataFrame containing cluster metrics including:
            - cluster: Cluster ID
            - centroid_conversation_ids: List of conversation IDs closest to centroid
            - all_conversation_ids: List of all conversation IDs in cluster
            - n_conversations: Number of conversations in cluster
            - embedding_centroid: Centroid embedding vector
            - tag_counts: Dictionary of tag counts for cluster
            - mean_cosine_similarity: Mean similarity between points and centroid
            - cluster_radius: Maximum distance from any point to centroid
            - silhouette_score: Silhouette score for the cluster
    """

    # Convert embeddings to numpy array
    embeddings = np.stack(cluster_df["embedding"].values)

    # Calculate silhouette scores for all points
    silhouette_scores = silhouette_samples(embeddings, cluster_df["cluster"])

    # Initialize results list
    cluster_metrics = []

    # Calculate metrics for each cluster
    for cluster_id in cluster_df["cluster"].unique():
        # Get cluster data
        cluster_mask = cluster_df["cluster"] == cluster_id
        cluster_embeddings = embeddings[cluster_mask]
        cluster_conversations = cluster_df[cluster_mask]

        # Calculate centroid
        centroid = np.mean(cluster_embeddings, axis=0)

        # Calculate cosine similarities to centroid
        similarities = np.dot(cluster_embeddings, centroid) / (
            np.linalg.norm(cluster_embeddings, axis=1) * np.linalg.norm(centroid)
        )
        mean_similarity = float(np.mean(similarities))

        # Calculate cluster radius (max distance from centroid)
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        cluster_radius = float(np.max(distances))

        # Get centroid documents (closest to centroid)
        # TODO: I should experiment w/ alternative ways of selecting centroid documents
        centroid_indices = np.argsort(similarities)[-n_centroid_docs:]
        centroid_conversation_ids = cluster_conversations.iloc[centroid_indices][
            "conversation_id"
        ].tolist()

        # Get all conversation IDs
        all_conversation_ids = cluster_conversations["conversation_id"].tolist()

        # Calculate tag counts using Counter
        all_tags = [tag for tags in cluster_conversations["tags"] for tag in tags]
        tag_counts = dict(Counter(all_tags).most_common(max_n_tags_per_cluster))

        # Calculate mean silhouette score for this cluster
        cluster_silhouette = float(np.mean(silhouette_scores[cluster_mask]))

        # Store metrics
        cluster_metrics.append(
            {
                "cluster": cluster_id,
                "centroid_conversation_ids": centroid_conversation_ids,
                "all_conversation_ids": all_conversation_ids,
                "n_conversations": len(all_conversation_ids),
                "embedding_centroid": centroid,
                "tag_counts": tag_counts,
                "mean_cosine_similarity": mean_similarity,
                "cluster_radius": cluster_radius,
                "silhouette_score": cluster_silhouette,
            }
        )

    return pd.DataFrame(cluster_metrics).sort_values(by="cluster")
