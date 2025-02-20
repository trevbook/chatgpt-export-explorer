FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    PYTHONPATH=/app \
    # Add environment variables for worker configuration
    WEB_CONCURRENCY=4 \
    MAX_WORKERS=4

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

# Use Gunicorn with single Uvicorn worker
CMD ["gunicorn", "main:app", \
    "--workers", "1", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--bind", "0.0.0.0:8000", \
    "--timeout", "300", \
    "--keep-alive", "5", \
    "--log-level", "info"]