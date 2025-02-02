# Use Python 3.9 slim image for a smaller footprint
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    FORCE_CPU=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch and torchvision first
RUN pip3 install torch==2.0.1+cpu torchvision==0.15.2+cpu --index-url https://download.pytorch.org/whl/cpu

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies in order, ensuring we keep CPU versions
RUN pip install --no-cache-dir Werkzeug==2.0.1 && \
    pip install --no-cache-dir Flask==2.0.1 && \
    pip install --no-cache-dir -r requirements.txt && \
    # Verify we're using CPU PyTorch
    python -c "import torch; assert not torch.cuda.is_available(), 'CUDA is available when it should not be'"

# Copy the rest of the application
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app --workers 2 --threads 2 --timeout 120 