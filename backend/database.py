"""
This module handles all database operations for the ChatGPT Explorer.
"""

# =====
# SETUP
# =====
# Below, we'll set up the database manager class.

# General imports
import logging
from pathlib import Path
import json
from importlib import import_module
from functools import lru_cache
from typing import List

# Project imports
from models import ClusteringResults

# Set up the logger
logger = logging.getLogger(__name__)


# Lazy load sqlite3
@lru_cache()
def get_sqlite3():
    return import_module("sqlite3")


# ===================
# DATABASE MANAGEMENT
# ===================
# The DatabaseManager class handles all database operations.


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        logger.info(f"Initialized DatabaseManager with database path: {db_path}")

    def initialize_database(self):
        """Create database tables if they don't exist"""
        logger.info("Initializing database tables")
        sqlite3 = get_sqlite3()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create conversations table
            logger.debug("Creating conversations table if it doesn't exist")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY, -- This is the unique identifier for the conversation
                    title TEXT NOT NULL, -- This is the title of the conversation
                    create_time INTEGER, -- This is a Unix timestamp indicating when the conversation was created
                    default_model_slug TEXT, -- This is the model that was used to generate the conversation
                    raw_messages_data TEXT, -- This is a JSON string containing the entire conversation's raw messages data
                    messages_markdown TEXT, -- This is a Markdown string containing the entire conversation
                    summary TEXT, -- This is a summary of the conversation
                    tags TEXT, -- This is a JSON string containing a list of tags associated with the conversation
                    embedding BLOB, -- This is a binary large object containing the conversation's embedding
                    umap_x REAL, -- This is the UMAP x-coordinate of the conversation's embedding
                    umap_y REAL -- This is the UMAP y-coordinate of the conversation's embedding
                )
                """
            )

            # Create clusters table
            logger.debug("Creating clusters table if it doesn't exist")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS clusters (
                    cluster_solution_id TEXT,
                    cluster_id TEXT,
                    conversation_ids TEXT, -- This is a JSON string containing a list of the conversation IDs that belong to this cluster
                    centroid_conversation_ids TEXT, -- This is a JSON string containing a list of the conversation IDs that are the centroids of this cluster
                    centroid_embedding BLOB, -- This is a binary large object containing the centroid embedding of the cluster
                    cluster_size INTEGER, -- The number of conversations in the cluster
                    cluster_label TEXT, -- The label of the cluster
                    cluster_description TEXT, -- A description of the cluster
                    tag_counts TEXT, -- This is a JSON string containing the counts of particular tags in the cluster
                    mean_cosine_similarity REAL, -- The mean cosine similarity between points and centroid
                    cluster_radius REAL, -- The maximum distance from any point to centroid
                    silhouette_score REAL, -- The silhouette score for this cluster
                    centroid_umap_x REAL, -- The UMAP x-coordinate of the centroid
                    centroid_umap_y REAL, -- The UMAP y-coordinate of the centroid
                    PRIMARY KEY (cluster_solution_id, cluster_id)
                )
                """
            )
        logger.info("Database tables initialized successfully")

    def has_data(self) -> bool:
        """
        Check if database has any processed conversations.

        Returns:
            bool: True if there are conversations in the database, False otherwise.
            Returns False if conversations table doesn't exist.
        """
        logger.debug("Checking if database has any processed conversations")
        sqlite3 = get_sqlite3()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                result = cursor.execute("SELECT COUNT(*) FROM conversations").fetchone()
                has_data = result[0] > 0
                logger.debug(f"Database has data: {has_data}")
                return has_data
        except sqlite3.OperationalError:
            logger.debug("Conversations table does not exist")
            return False

    def get_clusters(self) -> ClusteringResults:
        """
        Get clustering results from the database.

        Returns:
            ClusteringResults: Object containing cluster metrics and metadata
        """
        logger.info("Retrieving clustering results from database")
        sqlite3 = get_sqlite3()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            logger.debug("Executing query to get latest clustering solution")
            cursor.execute(
                """
                WITH latest_solution AS (
                    SELECT cluster_solution_id 
                    FROM clusters 
                    ORDER BY cluster_solution_id DESC 
                    LIMIT 1
                )
                SELECT 
                    cluster_id,
                    conversation_ids,
                    centroid_conversation_ids,
                    cluster_size,
                    cluster_label,
                    cluster_description,
                    tag_counts,
                    mean_cosine_similarity,
                    cluster_radius,
                    silhouette_score,
                    centroid_umap_x,
                    centroid_umap_y,
                    cluster_solution_id
                FROM clusters
                WHERE cluster_solution_id = (SELECT cluster_solution_id FROM latest_solution)
                """
            )

            clusters = []
            cluster_solution_id = None
            logger.debug("Processing query results")
            for row in cursor.fetchall():
                clusters.append(
                    {
                        "cluster_id": row[0],
                        "conversation_ids": json.loads(row[1]),
                        "centroid_conversation_ids": json.loads(row[2]),
                        "cluster_size": row[3],
                        "cluster_label": row[4],
                        "cluster_description": row[5],
                        "tag_counts": json.loads(row[6]),
                        "mean_cosine_similarity": row[7],
                        "cluster_radius": row[8],
                        "silhouette_score": row[9],
                        "centroid_umap_x": row[10],
                        "centroid_umap_y": row[11],
                    }
                )
                if cluster_solution_id is None:
                    cluster_solution_id = row[12]

            logger.info(
                f"Retrieved {len(clusters)} clusters from solution {cluster_solution_id}"
            )
            return ClusteringResults(
                cluster_solution_id=cluster_solution_id, clusters=clusters
            )

    def get_cluster_solutions(self) -> List[dict]:
        """
        Get list of all cluster solutions with their IDs and number of clusters
        """
        logger.debug("Getting list of cluster solutions")
        sqlite3 = get_sqlite3()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    cluster_solution_id,
                    COUNT(DISTINCT cluster_id) as n_clusters
                FROM clusters
                GROUP BY cluster_solution_id
                ORDER BY cluster_solution_id DESC
            """
            )

            solutions = [
                {"cluster_solution_id": row[0], "n_clusters": row[1]}
                for row in cursor.fetchall()
            ]

            logger.info(f"Retrieved {len(solutions)} cluster solutions")
            return solutions
