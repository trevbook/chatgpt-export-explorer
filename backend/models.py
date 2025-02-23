"""
This module defines Pydantic models for the ChatGPT Explorer API responses.
"""

# =====
# SETUP
# =====
# Below, we'll set up the Pydantic models.

# General imports
from datetime import datetime
from typing import List, Dict

# Third-party imports
from pydantic import BaseModel


# ===================
# RESPONSE MODELS
# ===================
# The models below define the structure of API responses.


class ProcessingStatus(BaseModel):
    """Model for processing status response"""

    status: str  # idle, processing, complete, error
    """Current processing state of the system"""

    message: str
    """Human-readable status message describing current state"""

    progress: int  # 0-100
    """Percentage of processing completed, from 0-100"""


class ClusterMetrics(BaseModel):
    """Model for individual cluster metrics"""

    cluster_id: str
    """Unique identifier for this cluster"""

    conversation_ids: List[str]
    """List of conversation IDs belonging to this cluster"""

    centroid_conversation_ids: List[str]
    """IDs of conversations closest to cluster centroid"""

    cluster_size: int
    """Number of conversations in this cluster"""

    cluster_label: str
    """Short descriptive label for the cluster"""

    cluster_description: str
    """Detailed description of cluster themes and content"""

    tag_counts: Dict[str, int]
    """Frequency counts of conversation tags in cluster"""

    mean_cosine_similarity: float
    """Average similarity between conversations in cluster"""

    cluster_radius: float
    """Maximum distance from centroid to any point"""

    silhouette_score: float
    """Measure of cluster cohesion and separation"""

    centroid_umap_x: float
    """X coordinate of cluster centroid in UMAP projection"""

    centroid_umap_y: float
    """Y coordinate of cluster centroid in UMAP projection"""


class ClusteringResults(BaseModel):
    """Model for clustering results"""

    cluster_solution_id: str
    """Unique identifier for this clustering solution"""

    clusters: List[ClusterMetrics]
    """List of individual cluster metrics and metadata"""


class Conversation(BaseModel):
    """Model for individual conversation data"""

    conversation_id: str
    """Unique identifier for this conversation"""

    title: str = "UNTITLED CONVERSATION"
    """Title of the conversation"""

    cluster_id: str | None = None
    """Cluster ID to which this conversation belongs"""

    umap_x: float
    """X coordinate of conversation in UMAP projection"""

    umap_y: float
    """Y coordinate of conversation in UMAP projection"""
