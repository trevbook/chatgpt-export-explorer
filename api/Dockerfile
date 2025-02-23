FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    PYTHONPATH=/app \
    # Add environment variables for worker configuration
    WEB_CONCURRENCY=4 \
    MAX_WORKERS=4 \
    # Add timeout configurations
    TIMEOUT=1800 \
    GRACEFUL_TIMEOUT=300 \
    KEEPALIVE=5

# Install Poetry
RUN pip install poetry gunicorn
RUN poetry self add poetry-plugin-export

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Install dependencies directly with poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the application code
# COPY . .

# Use Gunicorn with single Uvicorn worker, reloading and increased timeouts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]