"""
This is the entrypoint to the FastAPI application.
"""

# =====
# SETUP
# =====
# Below, we'll set up the rest of the file.

# Set up logging first
from utils.logging import configure_logging

configure_logging()

# General imports
import json
import logging
from typing import List

# Third-party imports
from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Project imports
from processing import ProcessingService
from database import DatabaseManager
from models import ProcessingStatus, ClusteringResults, Conversation

# Set up the logger
logger = logging.getLogger(__name__)

# ===================
# CONFIGURING FASTAPI
# ===================
# We'll start by configuring the FastAPI app.

# Create FastAPI app instance
app = FastAPI(
    title="Chat GPT Explorer API",
    description="API for exploring Chat GPT conversations",
    version="0.1.0",
)

# Add CORS middleware for local deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================
# DECLARING ENDPOINTS
# ===================
# Below, we'll declare different endpoints for the FastAPI app.
# Initialize services
logger.info("Initializing database and processing services")
db = DatabaseManager("data/conversations.db")
processor = ProcessingService(db)


@app.post("/upload")
async def upload_conversations(
    file: UploadFile, background_tasks: BackgroundTasks
) -> ProcessingStatus:
    """Handle initial file upload and start processing"""
    logger.info(f"Received file upload: {file.filename}")

    # Save file temporarily
    content = await file.read()
    conversations = json.loads(content)

    # Start processing in background task
    logger.info("Starting processing in background task")
    background_tasks.add_task(processor.process_conversations, conversations)

    return ProcessingStatus(
        status="processing", message="Started processing conversations", progress=0
    )


@app.get("/processing-status")
async def get_processing_status() -> ProcessingStatus:
    """Get current processing status"""
    return processor.get_status()


@app.get("/conversations/clusters-in-solution/{clustering_solution_id}")
async def get_clusters_in_solution(clustering_solution_id: str) -> ClusteringResults:
    """Get clustering results for a specific solution

    Args:
        clustering_solution_id: ID of the clustering solution to retrieve

    Returns:
        ClusteringResults: Object containing cluster metrics and metadata

    Raises:
        HTTPException: If no conversation data exists in database
    """
    if not db.has_data():
        logger.warning("No conversation data found in database")
        raise HTTPException(404, "No conversation data found")
    results = db.get_clusters_in_solution(clustering_solution_id)
    return results


@app.get("/has-data")
async def check_data_exists() -> bool:
    """Check if any conversation data exists in the database"""
    return db.has_data()


@app.get("/conversations/cluster-solutions")
async def get_cluster_solutions() -> List[dict]:
    """Get list of all cluster solutions with their IDs and number of clusters"""
    if not db.has_data():
        logger.warning("No conversation data found in database")
        raise HTTPException(404, "No conversation data found")
    solutions = db.get_cluster_solutions()
    return solutions


@app.get("/conversations/by-cluster-solution/{clustering_solution_id}")
async def get_conversations_by_cluster_solution(
    clustering_solution_id: str,
) -> List[Conversation]:
    """Get all conversations for a given cluster solution, including their cluster assignments

    Args:
        clustering_solution_id: ID of the cluster solution to get conversations for

    Returns:
        List[Conversation]: List of conversations with cluster assignments

    Raises:
        HTTPException: If no conversation data exists in database
    """
    if not db.has_data():
        logger.warning("No conversation data found in database")
        raise HTTPException(404, "No conversation data found")
    conversations = db.get_conversations_by_cluster_solution(clustering_solution_id)
    return conversations
