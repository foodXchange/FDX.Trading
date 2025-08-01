# Production Dockerfile for FoodXchange
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security first
RUN useradd -m -u 1000 appuser

# Copy Python dependencies from builder to appuser's home
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser foodxchange/ ./foodxchange/
COPY --chown=appuser:appuser requirements.txt ./

# Create necessary directories with correct ownership
RUN mkdir -p logs uploads temp static/errors projects && \
    chown -R appuser:appuser /app

# Add local pip packages to PATH for appuser
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Azure expects port 8000 (non-privileged port for non-root user)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production server with Gunicorn on port 8000 for Azure
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "foodxchange.main:app", "-k", "uvicorn.workers.UvicornWorker"]