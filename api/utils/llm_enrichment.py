"""
This module contains various utility functions related to using LLMs for enriching data. 
"""

# =====
# SETUP
# =====
# Below, we'll set up the rest of the file.

# General imports
import json
from typing import List

# Third-party imports
import pandas as pd
from pydantic import BaseModel, Field
from tqdm import tqdm

# Project imports
import utils.openai as openai_utils
import utils.settings as settings

# ================
# DEFINING METHODS
# ================
# Next, we'll define the utility functions that we'll use to enrich the data.


def enrich_conversations_with_summaries_and_tags(
    conversations_df: pd.DataFrame,
    max_chars_per_conversation_context: int = 4_000,
    n_suggested_tags: tuple[int, int] = (3, 5),
    gpt_model: str = settings.DEFAULT_GPT_MODEL,
    max_parallel_requests: int = settings.MAX_CONCURRENT_OPENAI_REQUESTS,
    show_progress: bool = True,
) -> pd.DataFrame:
    """
    Enriches a conversations DataFrame with LLM-generated summaries and tags.

    Args:
        conversations_df: DataFrame containing conversation data with messages_markdown column
        max_chars_per_conversation_context: Maximum characters to include in context sent to LLM
        n_suggested_tags: Tuple of (min_tags, max_tags) to generate
        gpt_model: The GPT model to use for generating summaries and tags
        max_parallel_requests: Maximum number of parallel requests to make to the API
        show_progress: Whether to show a progress bar during processing

    Returns:
        DataFrame with added summary and tags columns
    """
    # Define the system prompt for generating summaries and tags
    system_prompt = f"""
    You're an intelligent AI assistant who likes responding in JSON. 

    The user will provide you with a conversation between an AI chatbot and a user. 
    Your task is to briefly - in 1-2 sentences - summarize the main topics covered within the conversation.
    You'll also provide a list of "tags" - these are keywords / short phrases that characterize the conversation.
    Tags ought to be lowercase, and relevant to the conversation content. Include between {n_suggested_tags[0]}-{n_suggested_tags[1]} tags.
    """

    # Define Pydantic model for structured output
    class ConversationSummary(BaseModel):
        summary: str = Field(
            ..., description="A 1-2 sentence summary of the conversation"
        )
        tags: List[str] = Field(
            ..., description="A list of tags that describe the conversation"
        )

    # Generate completions in parallel
    completions = openai_utils.generate_completions_in_parallel(
        message_format_pairs=[
            (
                [
                    {
                        "role": "developer",
                        "content": [{"type": "text", "text": system_prompt}],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": row.messages_markdown[
                                    :max_chars_per_conversation_context
                                ]
                                + "...",
                            }
                        ],
                    },
                ],
                ConversationSummary,
            )
            for row in conversations_df.itertuples()
        ],
        gpt_model=gpt_model,
        max_parallel_requests=max_parallel_requests,
        show_progress=show_progress,
        tqdm_label="Enriching conversations with summaries and tags",
    )

    # Parse completions into summaries and tags
    conversation_summaries = []
    for completion in completions:
        try:
            conversation_summaries.append(completion.choices[0].message.parsed)
        except Exception as e:
            print(f"Error parsing completion: {e}")
            print(completion)
            conversation_summaries.append(None)

    # Update conversations DataFrame with summaries and tags
    conversations_df = conversations_df.copy()
    conversations_df["conversation_summary"] = conversation_summaries
    conversations_df["summary"] = conversations_df["conversation_summary"].apply(
        lambda x: x.summary if x else None
    )
    conversations_df["tags"] = conversations_df["conversation_summary"].apply(
        lambda x: x.tags if x else None
    )

    return conversations_df


def label_conversation_clusters(
    conversations_df: pd.DataFrame,
    cluster_metrics_df: pd.DataFrame,
    gpt_model: str = settings.DEFAULT_GPT_MODEL,
    max_parallel_requests: int = settings.MAX_CONCURRENT_OPENAI_REQUESTS,
    show_progress: bool = True,
) -> pd.DataFrame:
    """
    Labels conversation clusters using GPT to analyze centroid conversations and tag counts.

    Args:
        conversations_df (pd.DataFrame): DataFrame containing conversation details with columns:
            conversation_id, title, summary
        cluster_metrics_df (pd.DataFrame): DataFrame containing cluster information with columns:
            cluster, centroid_conversation_ids, tag_counts
        gpt_model (str): GPT model to use for labeling
        max_parallel_requests (int): Maximum number of parallel requests to make to OpenAI
        show_progress (bool): Whether to show progress bar

    Returns:
        pd.DataFrame: Copy of clusters_df with additional columns:
            cluster_label, cluster_description
    """

    # Define system prompt for cluster labeling
    system_prompt = """
    You're an intelligent AI assistant who likes responding in JSON.

    The user will provide you with a list of conversation summaries from a cluster of related conversations.
    Your task is to analyze these summaries and identify the common themes and topics that unite them.

    You'll provide:
    1. A brief, descriptive title for the cluster that captures its main theme
    2. A 1-2 sentence description explaining what types of conversations are in this cluster and what unites them

    Please ensure your response is concise but informative, focusing on the key patterns that emerge from the conversation cluster.
    """

    # Define a "ConversationClusterSummary" Pydantic model that will be used to validate the AI's response
    class ConversationClusterSummary(BaseModel):
        title: str = Field(
            ..., description="A brief, human-readable title for the cluster."
        )
        description: str = Field(
            ..., description="A longer 1-2 sentence description of the cluster."
        )

    # Create working copy of clusters DataFrame
    labeled_clusters_df = cluster_metrics_df.copy()

    # Create centroid summaries markdown
    labeled_clusters_df["centroid_summaries"] = labeled_clusters_df[
        "centroid_conversation_ids"
    ].apply(
        lambda ids: [
            f"**{title}**\n\n{summary}"
            for title, summary in conversations_df[
                conversations_df["conversation_id"].isin(ids)
            ][["title", "summary"]].values.tolist()
        ]
    )

    # Format summaries into markdown
    labeled_clusters_df["centroid_summary_markdown"] = labeled_clusters_df[
        "centroid_summaries"
    ].apply(lambda x: "---\n\n" + "\n\n---\n\n".join(x) + "\n\n---\n\n")

    # Create final prompt markdown combining summaries and tag counts
    labeled_clusters_df["prompt_markdown"] = labeled_clusters_df.apply(
        lambda row: f"# **Example Conversations:**\n\n{row['centroid_summary_markdown']}\n\n# **Tag Counts:**\n\n```json\n{json.dumps(row['tag_counts'], indent=4)}\n```",
        axis=1,
    )

    # Generate cluster labels using GPT
    completions = openai_utils.generate_completions_in_parallel(
        message_format_pairs=[
            (
                [
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": system_prompt}],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": row.prompt_markdown,
                            }
                        ],
                    },
                ],
                ConversationClusterSummary,
            )
            for row in labeled_clusters_df.itertuples()
        ],
        gpt_model=gpt_model,
        max_parallel_requests=max_parallel_requests,
        show_progress=show_progress,
        tqdm_label="Labeling conversation clusters",
    )

    # Parse completions
    cluster_summaries = []
    for completion in completions:
        try:
            cluster_summaries.append(completion.choices[0].message.parsed)
        except Exception as e:
            print(f"Error parsing completion: {e}")
            print(completion)
            cluster_summaries.append(None)

    # Add summaries to DataFrame
    labeled_clusters_df["cluster_summary"] = cluster_summaries
    labeled_clusters_df["cluster_label"] = labeled_clusters_df["cluster_summary"].apply(
        lambda x: x.title if x else None
    )
    labeled_clusters_df["cluster_description"] = labeled_clusters_df[
        "cluster_summary"
    ].apply(lambda x: x.description if x else None)

    # Clean up intermediate columns
    labeled_clusters_df = labeled_clusters_df.drop(
        columns=[
            "centroid_summaries",
            "centroid_summary_markdown",
            "prompt_markdown",
            "cluster_summary",
        ]
    )

    return labeled_clusters_df
