# Use lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       git \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (excluding large dirs via .dockerignore)
COPY . .

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh

# Expose port
EXPOSE 8000

# Entrypoint (downloads model then starts Flask app)
ENTRYPOINT ["/bin/sh", "/app/scripts/entrypoint.sh"]