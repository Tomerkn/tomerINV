# Use Python 3.11
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Download Llama3 model
RUN ollama pull llama3

# Expose port
EXPOSE 8000

# Start Ollama service and then the Flask app
CMD ollama serve & sleep 15 && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 