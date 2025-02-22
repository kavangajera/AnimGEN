# Base image with Python
FROM python:3.9-slim

# Create necessary directories with correct permissions


# Install system dependencies
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    ffmpeg \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    sox \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variable for Manim
ENV MEDIA_DIR=/app/workspace/media

# Expose port for Flask
EXPOSE 8080

# Command to run the Flask application
CMD ["python", "app.py"]