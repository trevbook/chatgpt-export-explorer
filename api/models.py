"""
This module defines Pydantic models for the ChatGPT Explorer API responses.
"""

# =====
# SETUP
# =====
# Below, we'll set up the Pydantic models.

# Third-party imports
from pydantic import BaseModel
from typing import List, Dict

# ===================
# RESPONSE MODELS
# ===================
# The models below define the structure of API responses.


class ProcessingStatus(BaseModel):
    """Model for processing status response"""

    status: str  # idle, processing, complete, error
    message: str
    progress: int  # 0-100


class ClusterMetrics(BaseModel):
    """Model for individual cluster metrics"""

    cluster_id: str
    conversation_ids: List[str]
    centroid_conversation_ids: List[str]
    cluster_size: int
    cluster_label: str
    cluster_description: str
    tag_counts: Dict[str, int]
    mean_cosine_similarity: float
    cluster_radius: float
    silhouette_score: float
    centroid_umap_x: float
    centroid_umap_y: float


class ClusteringResults(BaseModel):
    """Model for clustering results"""

    cluster_solution_id: str
    clusters: List[ClusterMetrics]
