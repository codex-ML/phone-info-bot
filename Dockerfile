# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install apt-utils and system dependencies
RUN apt-get update && \
    apt-get install -y \
    apt-utils \
    ffmpeg \
    espeak \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents inhto the container at /app
COPY . .


# Run only the main.py file
CMD ["python3", "main.py"]
