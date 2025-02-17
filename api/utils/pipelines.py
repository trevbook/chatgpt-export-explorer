"""
This module contains various utility functions related to preprocessing pipelines that prepare data for use by the API.
"""

# =====
# SETUP
# =====
# Below, we'll set up the rest of the file.

# General imports
import json
import math
import sqlite3
import warnings

# Third-party imports
import pandas as pd
import numpy as np
from tqdm import tqdm
from umap import UMAP

# Project imports
import utils.settings as settings
import utils.data_parsing as data_utils
import utils.llm_enrichment as llm_utils
import utils.openai as openai_utils
import utils.clusters as cluster_utils

# Ignore warnings
warnings.filterwarnings("ignore")

# ================
# DEFINING METHODS
# ================
# Next, we'll define the utility functions that we'll use to preprocess the data.


def preprocess_conversation_data(
    conversations: list[dict], db_path: str = "data/conversations.db"
) -> None:
    """
    Preprocesses conversation data and stores it in a SQLite database.

    Args:
        conversations: List of conversation dictionaries from the conversations.json export
        db_path: Path to SQLite database file to create/use
    """

    # Print that we're starting the preprocessing
    print("Starting conversation data preprocessing...")

    # ---------------------
    # Initializing Database
    # ---------------------
    # We'll start by initializing the database and creating the necessary tables.

    # Create database connection
    db_conn = sqlite3.connect(db_path)
    db_cursor = db_conn.cursor()

    # Drop existing tables if they exist
    db_cursor.execute("DROP TABLE IF EXISTS conversations")
    db_cursor.execute("DROP TABLE IF EXISTS clusters")

    # Create conversations table
    create_conversations_table_query = """
    CREATE TABLE conversations (
        conversation_id TEXT PRIMARY_KEY,
        title TEXT NOT NULL, 
        create_time INTEGER,
        default_model_slug TEXT,
        raw_messages_data TEXT,
        messages_markdown TEXT,
        summary TEXT,
        tags TEXT,
        embedding BLOB,
        umap_x REAL,
        umap_y REAL
    )
    """
    db_cursor.execute(create_conversations_table_query)

    # Create clusters table
    create_clusters_table_query = """
    CREATE TABLE clusters (
        cluster_solution_id TEXT,
        cluster_id TEXT,
        conversation_ids TEXT,
        centroid_conversation_ids TEXT,
        centroid_embedding BLOB,
        cluster_size INTEGER,
        cluster_label TEXT,
        cluster_description TEXT,
        tag_counts TEXT,
        mean_cosine_similarity REAL,
        cluster_radius REAL,
        silhouette_score REAL,
        centroid_umap_x REAL,
        centroid_umap_y REAL,
        PRIMARY KEY (cluster_solution_id, cluster_id)
    )
    """
    db_cursor.execute(create_clusters_table_query)

    # ---------------------------------
    # Loading Initial Conversation Data
    # ---------------------------------
    # Next, we'll process the conversations and prepare the initial data to insert into the database.

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
    insert_conversations_query = """
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
    """
    db_cursor.executemany(insert_conversations_query, conversations_data_to_insert)
    db_conn.commit()

    # ---------------------------
    # Enriching Conversation Data
    # ---------------------------
    # Next, we'll enrich the conversation data with summaries, tags, embeddings, and UMAP projections.

    # Enrich conversations with LLM summaries and tags
    llm_enriched_conversations_df = llm_utils.enrich_conversations_with_summaries_and_tags(
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

    db_cursor.executemany(
        """
        UPDATE conversations
        SET summary = :summary, tags = :tags
        WHERE conversation_id = :conversation_id
        """,
        conversations_data_to_insert,
    )
    db_conn.commit()

    # Generate embeddings
    embs = openai_utils.generate_embeddings_for_texts(
        text_list=[
            f"{row.title}\nTags: {', '.join(row.tags)}\nSummary: {row.summary}\nConversation: {row.messages_markdown[:settings.MAX_CHARS_PER_CONVERSATION_CONTEXT]}"
            for row in llm_enriched_conversations_df.itertuples()
        ]
    )

    conversation_emb_df = llm_enriched_conversations_df.copy()[["conversation_id"]]
    conversation_emb_df["embedding"] = embs.tolist()

    # Generate UMAP projections
    umap_model = UMAP(n_components=2)
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

    db_cursor.executemany(
        """
        UPDATE conversations
        SET embedding = :embedding, umap_x = :umap_x, umap_y = :umap_y
        WHERE conversation_id = :conversation_id
        """,
        conversations_data_to_insert,
    )
    db_conn.commit()

    # ------------------------
    # Clustering Conversations
    # ------------------------
    # Finally, we'll cluster the conversations and insert the cluster data into the database.

    # Generate clusters
    n_clusters = min(math.ceil(math.sqrt(len(conversation_emb_df))), 24)

    clusters_df = cluster_utils.cluster_conversations(
        conversation_embs_df=conversation_emb_df.merge(
            llm_enriched_conversations_df[["conversation_id", "tags"]],
            on="conversation_id",
        ),
        n_clusters=n_clusters,
    )

    cluster_metrics_df = cluster_utils.calculate_cluster_metrics(clusters_df)

    cluster_metrics_df[["umap_x", "umap_y"]] = umap_model.fit_transform(
        np.stack(cluster_metrics_df.embedding_centroid)
    )

    # Label clusters using LLM
    labeled_clusters_df = llm_utils.label_conversation_clusters(
        conversations_df=llm_enriched_conversations_df,
        cluster_metrics_df=cluster_metrics_df,
    )

    # Insert cluster data
    clusters_data_to_insert = [
        {
            "cluster_solution_id": f"kmeans_{n_clusters}",
            "cluster_id": row.cluster,
            "conversation_ids": json.dumps(row.all_conversation_ids),
            "centroid_conversation_ids": json.dumps(row.centroid_conversation_ids),
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

    db_cursor.executemany(
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
    db_conn.commit()

    # Close database connection
    db_conn.close()

    # Print that we're done with the preprocessing
    print("Conversation data preprocessing complete!")
