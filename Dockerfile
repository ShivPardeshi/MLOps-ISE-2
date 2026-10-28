# =======================================================
# Dockerfile for student-app: Student Performance Predictor
# Base Image: Python 3.12 Slim
# =======================================================

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Set working directory inside container
WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, assets, and trained model
COPY app.py .
COPY pytest.ini .
COPY models/ ./models/
COPY templates/ ./templates/
COPY static/ ./static/
COPY tests/ ./tests/

# Add non-root user for security best practices
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose web application port
EXPOSE 5000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Command to execute web application
CMD ["python", "app.py"]
