# Stage 1: Build stage with PyTorch and dependencies
FROM pytorch/pytorch:2.9.1-cpu AS builder

# Set working directory
WORKDIR /app

# Copy requirements and install Python deps (including PyTorch pre-installed)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage (slim)
FROM python:3.11-slim

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Install minimal runtime deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy app code (excluding large dirs via .dockerignore)
COPY . .

# Make entrypoint executable
RUN chmod +x /app/scripts/entrypoint.sh

# Expose port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/bin/sh", "/app/scripts/entrypoint.sh"]