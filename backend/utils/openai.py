"""
This module contains various utility functions related to the OpenAI APIs. 
"""

# =====
# SETUP
# =====
# The code below will help to set up the rest of this utility file.

# General import statements
import json
import time
import random
from typing import List, Optional, Tuple, Union, Callable
from concurrent.futures import ThreadPoolExecutor

# Third-party import statements
import openai
from tenacity import retry, stop_after_attempt, wait_fixed
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from tqdm import tqdm
import numpy as np
from openai import OpenAI

# ==================
# DEFINING CONSTANTS
# ==================
# Below, I'm going to define some constants. These will help for bookeeping costs & rate-limits
# associated with the OpenAI API.

# These costs are based on the OpenAI pricing page: https://platform.openai.com/pricing
# These costs were copied on February 15th, 2025.
OPENAI_MODEL_COST_PER_MILLION_TOKENS = {
    "gpt-4o-mini": {"input_tokens": 0.15, "output_tokens": 0.6},
    "gpt-4o": {"input_tokens": 2.5, "output_tokens": 10},
}

# These are based on the organizational limits defined here: https://platform.openai.com/settings/organization/limits
# These limits were copied on February 15th, 2025; I have Tier 3 usage limits.
OPENAI_MODEL_RATE_LIMITS = {
    "gpt-4o-mini": {"tokens_per_minute": 4_000_000, "requests_per_minute": 5_000},
    "gpt-4o": {"tokens_per_minute": 800_000, "requests_per_minute": 5_000},
}

# ================
# DEFINING METHODS
# ================
# Now, I'll define some utility methods that will help to interact with the OpenAI API.


def _calculate_sleep_time(
    tokens: Optional[int], model: str, n_workers: int, multiplier: float = 1.35
) -> float:
    """
    Calculates the sleep time based on the number of tokens used in a completion.

    Args:
        tokens (int): The number of tokens used in the completion.
        model (str): The model used for the completion.
        n_workers (int): The number of workers submitting completions.
        multiplier (float): A multiplier to adjust the sleep time. Defaults to 1.05.

    Returns:
        sleep_time (float): The time to sleep in seconds.
    """
    if tokens is None:
        return 0

    # Sleep a small amount of time to avoid sending requests all at once
    time.sleep(random.uniform(0, 0.35))

    # Get the rate limits for the model
    rate_limit_dict = OPENAI_MODEL_RATE_LIMITS.get(model)
    if rate_limit_dict is None:
        rate_limit_dict = OPENAI_MODEL_RATE_LIMITS.get("gpt-4o")

    # Slightly modifiy the multiplier
    multiplier += random.uniform(-0.1, 0.1)

    # Calculate the sleep time
    token_per_minute_sleep_time = (
        (tokens / rate_limit_dict.get("tokens_per_minute"))
        * multiplier
        * n_workers
        * 60
    )
    requests_per_minute_sleep_time = (
        (1 / rate_limit_dict.get("requests_per_minute")) * multiplier * n_workers * 60
    )
    total_sleep_time = token_per_minute_sleep_time + requests_per_minute_sleep_time

    # Return the total sleep time
    return total_sleep_time


@retry(
    wait=wait_fixed(3),
    stop=stop_after_attempt(2),
    reraise=True,
)
def _generate_completion_with_backoff(
    messages: List[dict],
    gpt_model: str,
    n_workers: int,
    temperature: float = 0,
    max_tokens: int = 2_048,
    response_format: BaseModel = None,
) -> ChatCompletion:
    """
    Generates a completion with a backoff strategy in case of failure / rate limiting.

    Args:
        messages (List[dict]): The messages to use for the completion.
        gpt_model (str): The GPT model to use for the completion.
        n_workers (int): The number of workers submitting completions.
        temperature (float): The sampling temperature for the completion. Defaults to 0.
        max_tokens (int): The maximum number of tokens to generate. Defaults to 2_048.

    Returns:
        completion (ChatCompletion): The completion response.
    """

    # Submit the completion request
    completion = openai.beta.chat.completions.parse(
        model=gpt_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
    )

    # Determine the necessary sleep time
    sleep_time = _calculate_sleep_time(
        tokens=completion.usage.total_tokens, model=gpt_model, n_workers=n_workers
    )

    # Sleep for the necessary time
    time.sleep(min(sleep_time, 3))

    # Return the completion
    return completion


def _calculate_completion_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Calculates the cost of a completion based on the number of input and output tokens.

    Args:
        model (str): The model used for the completion.
        input_tokens (int): The number of input tokens.
        output_tokens (int): The number of output tokens.

    Returns:
        cost (float): The cost of the completion.
    """

    # Get the cost per million tokens for the model
    model_costs_dict = OPENAI_MODEL_COST_PER_MILLION_TOKENS.get(model)

    # Calculate the cost of the input tokens
    input_token_cost = (input_tokens / 1_000_000) * model_costs_dict.get("input_tokens")

    # Calculate the cost of the output tokens
    output_token_cost = (output_tokens / 1_000_000) * model_costs_dict.get(
        "output_tokens"
    )

    # Return the total cost
    return input_token_cost + output_token_cost


def generate_embeddings_for_texts(
    text_list: List[str],
    model_name: str = "text-embedding-3-small",
    embedding_n_dimensions: Optional[int] = None,
    max_parallel_requests: int = 16,
    max_tokens_per_batch: int = 8_191,
    show_progress: bool = True,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> np.ndarray:
    """
    This function generates embeddings for a list of texts using an OpenAI embedding model.

    Args:
        text_list (List[str]): A list of texts for which embeddings are to be generated.
        model_name (str): The name of the OpenAI model to use for generating embeddings.
        embedding_n_dimensions (Optional[int]): The number of dimensions for the embeddings.
        max_parallel_requests (int): The maximum number of parallel requests to make to the OpenAI API.
        max_tokens_per_batch (int): The maximum number of tokens per batch.
        show_progress (bool): Whether to show a progress bar.
        progress_callback (Optional[Callable[[int], None]]): Optional callback function to report progress.
            Callback function should accept an integer representing completed items.

    Returns:
        np.ndarray: An array of embeddings for the texts.
    """

    # Setting a global constant based on the "rule of thumb" from OpenAI's tokenizer tool:
    # https://platform.openai.com/tokenizer
    CHARS_PER_TOKEN = 3.75

    # If max_tokens_per_batch is > 8,191, then we'll print a warning and override it
    if max_tokens_per_batch > 8_191:
        print(
            "Warning: The maximum number of tokens per batch is 8,191. Overriding the input value."
        )
        max_tokens_per_batch = 8_191

    # Setting up the OpenAI client
    openai_client = OpenAI()

    # -------------
    # Batching Text
    # -------------
    # First, I'll break the text into batches based on the max_tokens_per_batch

    # Initialize the list of batches
    batches = []

    # Initialize the current batch
    current_batch = []
    cur_batch_token_ct = 0
    for text in text_list:
        # Estimate the number of tokens for the current text
        n_tokens = len(text) / CHARS_PER_TOKEN

        # If the current text would exceed the max_tokens_per_batch, then we'll start a new batch
        if cur_batch_token_ct + n_tokens > max_tokens_per_batch:
            batches.append(current_batch)
            current_batch = []
            cur_batch_token_ct = 0

        # Add the current text to the current batch
        current_batch.append(text)

        # Update the current batch token count
        cur_batch_token_ct += n_tokens

    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)

    # --------------
    # Embedding Text
    # --------------
    # Now that I've got all of the text in batches, I'll embed each batch

    @retry(
        wait=wait_fixed(3),
        stop=stop_after_attempt(2),
        reraise=True,
    )
    def _emb_helper(text_list: List[str], openai_client: OpenAI):
        # Generate the embeddings for the current batch

        if embedding_n_dimensions is not None:
            response = openai_client.embeddings.create(
                input=text_list, model=model_name, dimensions=embedding_n_dimensions
            )
        else:
            response = openai_client.embeddings.create(
                input=text_list, model=model_name
            )

        # Extract the embeddings
        embeddings = [emb.embedding for emb in response.data]

        return embeddings

    # Parallelize calls to the OpenAI API
    futures = {}
    results = {}
    with ThreadPoolExecutor(max_workers=max_parallel_requests) as executor:

        # Submit the futures
        for i, batch in enumerate(batches):
            futures[i] = executor.submit(_emb_helper, batch, openai_client)

        # Collect the results
        for i, future in tqdm(
            iterable=futures.items(),
            total=len(futures),
            desc="Generating Embeddings",
            disable=not show_progress,
        ):
            res = future.result()

            if res is not None:
                results[i] = res
                if progress_callback:
                    progress_callback(i + 1)
            else:
                raise ValueError("An error occurred while generating embeddings.")

    # -----------------
    # Returning Results
    # -----------------
    # Finally, I can prepare and return the results of this function

    # Concatenate the results into a single array, ensuring that the order of the original text_list is preserved
    embeddings = np.concatenate([np.array(results[i]) for i in range(len(results))])

    return embeddings


def generate_completions_in_parallel(
    message_format_pairs: List[Tuple[List[dict], Optional[BaseModel]]],
    gpt_model: str = "gpt-4o",
    temperature: float = 0,
    max_tokens: int = 2_048,
    max_parallel_requests: int = 16,
    show_progress: bool = True,
    tqdm_label: str = "Generating Completions",
    return_completion_costs: bool = False,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> Union[List[ChatCompletion], Tuple[List[ChatCompletion], float]]:
    """
    Generates completions in parallel for multiple prompts using ThreadPoolExecutor.

    Args:
        message_format_pairs (List[Tuple[List[dict], Optional[BaseModel]]]): List of tuples containing
            (messages, response_format) pairs for each completion
        gpt_model (str): The GPT model to use for completions. Defaults to "gpt-4o"
        temperature (float): Temperature setting for completions. Defaults to 0
        max_tokens (int): Maximum tokens per completion. Defaults to 2,048
        max_parallel_requests (int): Maximum number of parallel requests. Defaults to 16
        show_progress (bool): Whether to show progress bar. Defaults to True
        tqdm_label (str): Label for the progress bar. Defaults to "Generating Completions"
        return_completion_costs (bool): Whether to return completion costs. Defaults to False
        progress_callback (Optional[Callable[[int], None]]): Optional callback function to report progress.
            Callback function should accept an integer representing completed items.

    Returns:
        Union[List[ChatCompletion], Tuple[List[ChatCompletion], float]]:
            If return_completion_costs is False, returns list of completion responses.
            If True, returns tuple of (completions list, total cost)
    """

    def _completion_helper(
        messages: List[dict], response_format: Optional[BaseModel]
    ) -> ChatCompletion:
        # Generate completion with backoff
        completion = _generate_completion_with_backoff(
            messages=messages,
            gpt_model=gpt_model,
            n_workers=max_parallel_requests,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        # Calculate costs and sleep time
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens

        cost = _calculate_completion_cost(
            model=gpt_model, input_tokens=input_tokens, output_tokens=output_tokens
        )

        sleep_time = _calculate_sleep_time(
            tokens=input_tokens + output_tokens,
            model=gpt_model,
            n_workers=max_parallel_requests,
        )

        time.sleep(sleep_time)

        return completion, cost

    # Parallelize calls to the OpenAI API
    futures = {}
    results = {}
    completion_costs = {}
    with ThreadPoolExecutor(max_workers=max_parallel_requests) as executor:
        # Submit the futures
        for i, (messages, response_format) in enumerate(message_format_pairs):
            futures[i] = executor.submit(_completion_helper, messages, response_format)

        completed_items = 0

        # Collect the results
        for i, future in tqdm(
            iterable=futures.items(),
            total=len(futures),
            desc=tqdm_label,
            disable=not show_progress,
        ):
            completion, cost = future.result()

            if completion is not None:
                results[i] = completion
                completion_costs[i] = cost

                completed_items += 1
                if progress_callback:
                    progress_callback(completed_items)
            else:
                raise ValueError("An error occurred while generating completion.")

    # Return results in original order with optional costs
    completions = [results[i] for i in range(len(results))]
    if return_completion_costs:
        total_cost = sum(completion_costs.values())
        return completions, total_cost
    return completions
