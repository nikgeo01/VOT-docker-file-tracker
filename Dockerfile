# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Tkinter and other utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-tk \
        tk8.6 \
        libtk8.6 \
        libtcl8.6 \
        x11-apps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Set the DISPLAY environment variable for GUI applications
ENV DISPLAY=host.docker.internal:0.0

# Command to run the report generator
CMD ["python", "import_csv_to_db.py"]
CMD ["python", "report_generator.py"]
