"""
This module configures logging for the ChatGPT Explorer.
"""

# =====
# SETUP
# =====
# Below, we'll set up the logging configuration.

# General imports
import logging
import sys


# ===================
# LOGGING CONFIGURATION
# ===================
# The configure_logging function sets up the root logger with console output.


def configure_logging():
    """Configure root logger with console handler and formatting"""
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add console handler to root logger
    root_logger.addHandler(console_handler)

    # Suppress httpx logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
