# Dockerfile for Snowflake AI Agent
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY examples/ ./examples/
COPY .env.example .env

# Create directories for sessions and exports
RUN mkdir -p sessions sessions/exports

# Expose port if running web interface (future feature)
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Default command
CMD ["python", "-m", "src.main", "interactive"]