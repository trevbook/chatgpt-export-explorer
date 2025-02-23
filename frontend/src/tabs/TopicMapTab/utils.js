export function transformClusterData(clusterData, view) {
  if (!clusterData) return [];

  if (view === "cluster") {
    console.log(clusterData);
    // Return cluster centroids for cluster view
    return clusterData.clusters.map((cluster) => ({
      x: cluster.centroid_umap_x,
      y: cluster.centroid_umap_y,
      label: cluster.cluster_label,
      type: "cluster",
      size: cluster.cluster_size, // Size based on number of documents
      cluster: cluster.cluster_id,
      // Additional metadata
      description: cluster.cluster_description,
      tagCounts: cluster.tag_counts,
      similarity: cluster.mean_cosine_similarity,
    }));
  } else {
    const docs_data = clusterData.map((doc) => ({
      x: doc.umap_x,
      y: doc.umap_y,
      label: doc.title,
      type: "conversation",
      size: 10, // Fixed size for documents
      cluster: doc.cluster_id,
    }));
    return docs_data;
  }
}
