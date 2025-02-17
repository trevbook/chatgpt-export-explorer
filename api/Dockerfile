# We're going to use the Python 3.10 slim image as our base image
FROM python:3.10-slim

# Set up the working directory
WORKDIR /app

# Set certain environment variables
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    PYTHONPATH=/app

# Install Poetry
RUN pip install poetry
RUN poetry self add poetry-plugin-export

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Install dependencies directly with poetry instead of exporting
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Run the FastAPI application w/ Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
