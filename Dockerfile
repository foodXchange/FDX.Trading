# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages and Azure services
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY foodxchange/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire foodxchange directory
COPY foodxchange/ .

# Copy environment files (will be overridden by docker-compose)
COPY .env.example .env.example

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check for Azure services
HEALTHCHECK --interval=5m --timeout=30s --start-period=2m --retries=3 \
    CMD python quick_health_check.py || exit 1

# Expose the application port
EXPOSE 8000

# Default command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]