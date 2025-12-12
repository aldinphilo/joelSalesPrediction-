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

# Expose port (Railway/Render use PORT env variable)
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]