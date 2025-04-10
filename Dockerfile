FROM python:3.12-slim

# Install system dependencies - note we exclude PyAudio dependencies to avoid build issues
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Use a start script with proper shell expansion for the PORT variable
RUN echo '#!/bin/bash\nuvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"' > start.sh && \
    chmod +x start.sh

# Command to run the application
CMD ["./start.sh"]