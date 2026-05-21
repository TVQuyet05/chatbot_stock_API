# Use python 3.11 slim for a light image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements/pyproject
COPY pyproject.toml .

# Optimize: Install CPU-only torch first to save ~1.5GB of space
# Then install the rest of the project
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir .

# Copy source code and data
COPY src/ ./src/
COPY datasets/ ./datasets/
COPY portal/ ./portal/
COPY .env.example .env

# Expose API port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
