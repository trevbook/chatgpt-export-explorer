"""
This module contains various utility functions related to parsing the ChatGPT export data. 
"""

# =====
# SETUP
# =====
# Below, we'll set up the rest of the file.

# Third-party imports
import pandas as pd

# ================
# DEFINING METHODS
# ================
# Next, we'll define the utility functions that we'll use to parse the ChatGPT export data.


def extract_longest_conversation_df(mapping: dict) -> pd.DataFrame:
    """
    Extracts the longest "chain" of messages from a mapping of conversation nodes.

    Args:
        mapping (dict): A dictionary mapping node IDs to node information.

    Returns:
        pd.DataFrame: A DataFrame containing the messages in the longest chain.
    """

    # Helper function to get chain from node to leaf
    def get_chain_from_node(node_id):
        chain = []
        current_id = node_id

        while current_id:
            node = mapping[current_id]
            if node["message"] is not None:  # Only include non-null messages
                chain.append(node["message"])

            # Move to child if exists, otherwise break
            children = node["children"]
            current_id = children[0] if children else None

        return chain

    # Find all root nodes (nodes with no parent)
    root_nodes = [
        node_id for node_id, node in mapping.items() if node["parent"] is None
    ]

    # Get all possible chains starting from root nodes
    all_chains = [get_chain_from_node(root_id) for root_id in root_nodes]

    # Get the longest chain
    longest_chain = max(all_chains, key=len) if all_chains else []

    # Create a DataFrame from the mapping
    messages_df = pd.DataFrame(
        sorted(
            longest_chain,
            key=lambda x: (x["create_time"] or 0) if x else 0,
        )
    )

    # Add the "author_role" column
    messages_df["author_role"] = messages_df["author"].apply(
        lambda x: x["role"] if x else None
    )

    # Return the DataFrame
    return messages_df


def extract_simple_conversation_markdown(
    conversation_df: pd.DataFrame = None, mapping: dict = None
) -> str:
    """
    Extracts a simple Markdown representation of a conversation between a user and an AI assistant.
    The output of the `extract_longest_conversation_df` function can be used as input to this function.

    Args:
        conversation_df (pd.DataFrame, optional): A DataFrame containing the conversation data. If not provided, mapping must be provided.
        mapping (dict, optional): A dictionary mapping node IDs to node information. If provided, will be used to extract conversation DataFrame.

    Returns:
        str: A simple Markdown representation of the conversation
    """
    if mapping is not None:
        conversation_df = extract_longest_conversation_df(mapping)
    elif conversation_df is None:
        raise ValueError("Either conversation_df or mapping must be provided")

    # Filter out messages not from the assistant / user
    filtered_conversation_df = conversation_df.query(
        "author_role=='assistant' | author_role=='user'"
    )

    # Iterate through each of the message data within the filtered_conversation_df, and extract the content
    markdown_lines = []
    for msg_row in filtered_conversation_df.itertuples():

        # Extract a dictionary of the message data + message content
        msg_data_dict = msg_row._asdict()
        msg_content_dict = msg_data_dict.get("content", {})

        # Determine the role of the author
        author_role = msg_data_dict.get("author_role")

        # Populate the msg_text depending on the content type
        msg_text = None
        if msg_content_dict.get("content_type") == "text":
            msg_text = " ".join(msg_content_dict.get("parts", []))
        elif msg_content_dict.get("content_type") == "code":
            msg_text = msg_content_dict.get("text", None)
        elif msg_content_dict.get("content_type") == "multimodal_text":
            msg_text = " ".join(
                [
                    part if isinstance(part, str) else "\n[IMAGE OMITTED]\n"
                    for part in msg_content_dict.get("parts", [])
                ]
            )

        # If the message text is not None, add it to the markdown_lines list
        if msg_text is not None and msg_text.strip() != "":
            markdown_lines.append(f"# **{author_role.capitalize()}:**\n{msg_text}")

    # Join the markdown lines w/ newlines + `---` separator
    return "\n\n---\n".join(markdown_lines)


def extract_summarized_conversation_markdown(
    summarized_conversation: pd.Series, max_conversation_chars: int = 2000
) -> str:
    """
    Extracts a markdown representation of a summarized conversation, including the title, tags, summary and a sample of the conversation.

    Args:
        summarized_conversation (pd.Series): A Series containing the summarized conversation data, with fields like 'title', 'tags', 'summary' and 'conversation_markdown'
        max_conversation_chars (int, optional): Maximum number of characters to include from the conversation. Defaults to 2000.

    Returns:
        str: A markdown representation of the summarized conversation
    """
    # Check if conversation is truncated
    conversation_text = summarized_conversation.conversation_markdown
    is_truncated = len(conversation_text) > max_conversation_chars

    truncation_text = "\n\n***conversation truncated***" if is_truncated else ""
    ellipsis = "..." if is_truncated else ""

    return f"""# {summarized_conversation.title}\n

    \n\n**TAGS:** \n```\n{summarized_conversation.tags}\n```\n

    \n\n**SUMMARY:** \n{summarized_conversation.summary}

    \n\n**CONVERSATION SAMPLE:**

    \n\n{conversation_text[:max_conversation_chars]}{ellipsis}{truncation_text}"""
