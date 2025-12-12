# Use official lightweight Python image (newer Python for compatibility)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install system dependencies needed to build some Python packages
# and ensure pip/setuptools/wheel are up-to-date so wheels are used when available.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   git \
	   curl \
	   ca-certificates \
	   wget \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt

# Copy everything to the container
COPY . .

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh || true

# Expose port (Railway/Render use PORT env variable)
EXPOSE 8000

# ENTRYPOINT runs the downloader then starts the app. Provide MODEL_URL or MODEL_HF_ID
# at runtime: e.g. `docker run -e MODEL_URL=... -p 8000:8000 <image>`
ENTRYPOINT ["/bin/sh", "/app/scripts/entrypoint.sh"]