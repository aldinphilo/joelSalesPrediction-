# Use lightweight Python image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache build-base curl ca-certificates \
    && pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apk del build-base

# Copy app code (excluding large dirs via .dockerignore)
COPY . .  # This includes Model/

# Expose port
EXPOSE 8000

# Entrypoint (downloads model then starts Flask app)
CMD ["python", "app.py"]