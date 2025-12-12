# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything to the container
COPY . .

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh || true

# Expose port (Railway/Render use PORT env variable)
EXPOSE 8000

# ENTRYPOINT runs the downloader then starts the app. Provide MODEL_URL or MODEL_HF_ID
# at runtime: e.g. `docker run -e MODEL_URL=... -p 8000:8000 <image>`
ENTRYPOINT ["/bin/sh", "/app/scripts/entrypoint.sh"]