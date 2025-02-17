"""
This is the entrypoint to the FastAPI application.
"""

# =====
# SETUP
# =====
# Below, we'll set up the rest of the file.

# Third-party imports
from fastapi import FastAPI

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

# ===================
# DECLARING ENDPOINTS
# ===================
# Below, we'll declare different endpoints for the FastAPI app.


@app.get("/")
async def root():
    """Root endpoint that returns a hello world message."""
    return {"message": "Hello World"}
