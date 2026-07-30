FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend code and samples
COPY backend/app /app/app
COPY samples /app/samples
COPY scripts /app/scripts

EXPOSE 8000

ENV PYTHONPATH=/app

# Run seed script and start FastAPI server
CMD ["sh", "-c", "python scripts/seed_demo.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
