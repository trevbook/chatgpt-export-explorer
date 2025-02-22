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
from multiprocessing import Process
import concurrent
import asyncio

# Third-party imports
from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Project imports
from processing import ProcessingService
from database import DatabaseManager
from models import ProcessingStatus, ClusteringResults

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
    allow_origins=["http://localhost:3000"],
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


@app.get("/status")
async def get_processing_status() -> ProcessingStatus:
    """Get current processing status"""
    return processor.get_status()


@app.get("/conversations/clusters")
async def get_clusters() -> ClusteringResults:
    """Get clustering results"""
    if not db.has_data():
        logger.warning("No conversation data found in database")
        raise HTTPException(404, "No conversation data found")
    results = db.get_clusters()
    return results


@app.get("/has-data")
async def check_data_exists() -> bool:
    """Check if any conversation data exists in the database"""
    return db.has_data()
