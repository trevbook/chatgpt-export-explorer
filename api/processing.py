"""
This module handles conversation processing and analysis for the ChatGPT Explorer.
"""

# =====
# SETUP
# =====
# Below, we'll set up the processing service class.

# General imports
import json
import math
import sqlite3
import warnings
from typing import Dict, Any
import logging
from importlib import import_module
from functools import lru_cache

# Third-party imports
import pandas as pd
import numpy as np
from tqdm import tqdm

# Project imports
import utils.settings as settings
import utils.data_parsing as data_utils

# Set up logging
logger = logging.getLogger(__name__)

# Ignore warnings
warnings.filterwarnings("ignore")

# ===================
# PROCESSING SERVICE
# ===================
# The ProcessingService class handles conversation processing, embedding generation,
# and clustering analysis.


class ProcessingService:
    def __init__(self, db_manager):
        """Initialize the processing service with a database manager"""
        self.db = db_manager
        self.status_file = "data/processing_status.json"
        self._initialize_status()
        self._umap = None
        self._llm_utils = None
        self._openai_utils = None
        self._cluster_utils = None

    def _initialize_status(self):
        """Initialize or reset the status file"""
        initial_status = {"status": "idle", "message": "", "progress": 0}
        self._update_status_file(initial_status)

    def _update_status_file(self, status_data: Dict[str, Any]):
        """Update the status file with new status information"""
        try:
            with open(self.status_file, "w") as f:
                json.dump(status_data, f)
        except Exception as e:
            logger.error(f"Error updating status file: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current processing status from file"""
        try:
            with open(self.status_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self._initialize_status()
            return self.get_status()
        except Exception as e:
            logger.error(f"Error reading status file: {e}")
            return {"status": "error", "message": str(e), "progress": 0}

    @property
    @lru_cache()
    def umap(self):
        """Lazy load UMAP"""
        if self._umap is None:
            from umap import UMAP

            self._umap = UMAP
        return self._umap

    @property
    def llm_utils(self):
        """Lazy load LLM utilities"""
        if self._llm_utils is None:
            self._llm_utils = import_module("utils.llm_enrichment")
        return self._llm_utils

    @property
    def openai_utils(self):
        """Lazy load OpenAI utilities"""
        if self._openai_utils is None:
            self._openai_utils = import_module("utils.openai")
        return self._openai_utils

    @property
    def cluster_utils(self):
        """Lazy load clustering utilities"""
        if self._cluster_utils is None:
            self._cluster_utils = import_module("utils.clusters")
        return self._cluster_utils

    def process_conversations(self, conversations: list):
        """
        Process conversations in background, including parsing, embedding generation,
        and clustering analysis.

        Args:
            conversations (list): List of conversation data to process
        """
        try:
            # Update status as processing progresses
            self._update_status_file(
                {
                    "status": "processing",
                    "message": "Parsing conversations",
                    "progress": 10,
                }
            )
            logger.info("Status updated: Parsing conversations (10%)")

            # Initialize database tables
            self.db.initialize_database()

            # Process conversations and prepare initial data
            conversations_data_to_insert = []
            for conversation in tqdm(conversations, desc="Processing conversations"):
                messages_df = data_utils.extract_longest_conversation_df(
                    mapping=conversation.get("mapping", {})
                )

                cur_conversation_data = {
                    "conversation_id": conversation.get("conversation_id"),
                    "title": conversation.get("title", "UNTITLED CONVERSATION"),
                    "create_time": conversation.get("create_time"),
                    "default_model_slug": conversation.get("default_model_slug"),
                    "raw_messages_data": messages_df.to_json(),
                    "messages_markdown": data_utils.extract_simple_conversation_markdown(
                        conversation_df=messages_df
                    ),
                }
                conversations_data_to_insert.append(cur_conversation_data)

            # Insert initial conversation data
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    """
                    INSERT INTO conversations (
                        conversation_id,
                        title,
                        create_time,
                        default_model_slug,
                        raw_messages_data,
                        messages_markdown
                    ) VALUES (
                        :conversation_id,
                        :title,
                        :create_time,
                        :default_model_slug,
                        :raw_messages_data,
                        :messages_markdown
                    )
                    """,
                    conversations_data_to_insert,
                )

            self._update_status_file(
                {
                    "status": "processing",
                    "message": "Generating embeddings",
                    "progress": 40,
                }
            )
            logger.info("Status updated: Generating embeddings (40%)")

            # Enrich conversations with LLM summaries and tags
            llm_enriched_conversations_df = self.llm_utils.enrich_conversations_with_summaries_and_tags(
                conversations_df=pd.DataFrame(conversations_data_to_insert),
                max_chars_per_conversation_context=settings.MAX_CHARS_PER_CONVERSATION_CONTEXT,
            )

            # Update conversations with summaries and tags
            conversations_data_to_insert = [
                {
                    "conversation_id": row.conversation_id,
                    "summary": row.summary,
                    "tags": json.dumps(row.tags),
                }
                for row in llm_enriched_conversations_df.itertuples()
            ]

            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    """
                    UPDATE conversations
                    SET summary = :summary, tags = :tags
                    WHERE conversation_id = :conversation_id
                    """,
                    conversations_data_to_insert,
                )

            # Generate embeddings
            embs = self.openai_utils.generate_embeddings_for_texts(
                text_list=[
                    f"{row.title}\nTags: {', '.join(row.tags)}\nSummary: {row.summary}\nConversation: {row.messages_markdown[:settings.MAX_CHARS_PER_CONVERSATION_CONTEXT]}"
                    for row in llm_enriched_conversations_df.itertuples()
                ]
            )

            conversation_emb_df = llm_enriched_conversations_df.copy()[
                ["conversation_id"]
            ]
            conversation_emb_df["embedding"] = embs.tolist()

            # Generate UMAP projections
            umap_model = self.umap(n_components=2)
            conversation_emb_df[["umap_x", "umap_y"]] = umap_model.fit_transform(
                np.stack(conversation_emb_df.embedding)
            )

            # Update conversations with embeddings and UMAP coordinates
            conversations_data_to_insert = [
                {
                    "conversation_id": row.conversation_id,
                    "embedding": np.array(row.embedding, dtype=np.float32).tobytes(),
                    "umap_x": row.umap_x,
                    "umap_y": row.umap_y,
                }
                for row in conversation_emb_df.itertuples()
            ]

            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    """
                    UPDATE conversations
                    SET embedding = :embedding, umap_x = :umap_x, umap_y = :umap_y
                    WHERE conversation_id = :conversation_id
                    """,
                    conversations_data_to_insert,
                )

            self._update_status_file(
                {"status": "processing", "message": "Clustering data", "progress": 70}
            )
            logger.info("Status updated: Clustering data (70%)")

            # Generate clusters
            n_clusters = min(math.ceil(math.sqrt(len(conversation_emb_df))), 24)

            clusters_df = self.cluster_utils.cluster_conversations(
                conversation_embs_df=conversation_emb_df.merge(
                    llm_enriched_conversations_df[["conversation_id", "tags"]],
                    on="conversation_id",
                ),
                n_clusters=n_clusters,
            )

            cluster_metrics_df = self.cluster_utils.calculate_cluster_metrics(
                clusters_df
            )

            cluster_metrics_df[["umap_x", "umap_y"]] = umap_model.fit_transform(
                np.stack(cluster_metrics_df.embedding_centroid)
            )

            # Label clusters using LLM
            labeled_clusters_df = self.llm_utils.label_conversation_clusters(
                conversations_df=llm_enriched_conversations_df,
                cluster_metrics_df=cluster_metrics_df,
            )

            # Insert cluster data
            clusters_data_to_insert = [
                {
                    "cluster_solution_id": f"kmeans_{n_clusters}",
                    "cluster_id": row.cluster,
                    "conversation_ids": json.dumps(row.all_conversation_ids),
                    "centroid_conversation_ids": json.dumps(
                        row.centroid_conversation_ids
                    ),
                    "centroid_embedding": np.array(
                        row.embedding_centroid, dtype=np.float32
                    ).tobytes(),
                    "cluster_size": row.n_conversations,
                    "cluster_label": row.cluster_label,
                    "cluster_description": row.cluster_description,
                    "tag_counts": json.dumps(row.tag_counts),
                    "mean_cosine_similarity": row.mean_cosine_similarity,
                    "cluster_radius": row.cluster_radius,
                    "silhouette_score": row.silhouette_score,
                    "centroid_umap_x": row.umap_x,
                    "centroid_umap_y": row.umap_y,
                }
                for row in labeled_clusters_df.itertuples()
            ]

            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    """
                    INSERT INTO clusters (
                        cluster_solution_id,
                        cluster_id,
                        conversation_ids,
                        centroid_conversation_ids,
                        centroid_embedding,
                        cluster_size,
                        cluster_label,
                        cluster_description,
                        tag_counts,
                        mean_cosine_similarity,
                        cluster_radius,
                        silhouette_score,
                        centroid_umap_x,
                        centroid_umap_y
                    ) VALUES (
                        :cluster_solution_id,
                        :cluster_id,
                        :conversation_ids,
                        :centroid_conversation_ids,
                        :centroid_embedding,
                        :cluster_size,
                        :cluster_label,
                        :cluster_description,
                        :tag_counts,
                        :mean_cosine_similarity,
                        :cluster_radius,
                        :silhouette_score,
                        :centroid_umap_x,
                        :centroid_umap_y
                    )
                    """,
                    clusters_data_to_insert,
                )

            self._update_status_file(
                {
                    "status": "complete",
                    "message": "Processing complete",
                    "progress": 100,
                }
            )
            logger.info("Status updated: Processing complete (100%)")

        except Exception as e:
            self._update_status_file(
                {"status": "error", "message": str(e), "progress": 0}
            )
            logger.error(f"Processing error: {str(e)}")
