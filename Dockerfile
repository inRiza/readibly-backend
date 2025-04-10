FROM python:3.12-slim

# Install system dependencies required for PyAudio and audio processing
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg \
    libasound-dev \
    libportaudio2 \
    libsndfile1 \
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

# Create a start script that properly handles environment variables
RUN echo '#!/bin/bash\nuvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"' > start.sh && \
    chmod +x start.sh

# Command to run the application
CMD ["./start.sh"]