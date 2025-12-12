# Use lightweight Python image (Debian-based for better torch compatibility)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#        build-essential \
#        curl \
#        ca-certificates \
#     && rm -rf /var/lib/apt/lists/* \
#     && pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (including Model/)
COPY . .

# Expose port
EXPOSE 8000

# Entrypoint (downloads model then starts Flask app)
CMD ["python", "app.py"]