FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and pygame
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ src/
COPY assets/ assets/
COPY . .

# Create necessary directories
RUN mkdir -p assets/characters/{spiderman,venom,goblin,thug} \
    && mkdir -p assets/effects/{explosion,web} \
    && mkdir -p assets/environment/{buildings,cars,road} \
    && mkdir -p assets/sounds \
    && mkdir -p assets/models

# Run the application
CMD ["python", "-m", "src.main"]
