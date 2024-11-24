# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Tkinter, bash, and other utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-tk \
        tk8.6 \
        libtk8.6 \
        libtcl8.6 \
        x11-apps \
        bash \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Set the DISPLAY environment variable for GUI applications
ENV DISPLAY=host.docker.internal:0.0

# Define the default command to run both Python scripts sequentially
CMD ["bash", "-c", "python import_csv_to_db.py && python report_generator.py"]
