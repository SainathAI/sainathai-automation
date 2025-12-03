# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /usr/src/app
COPY . .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV PORT 8080

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
FROM python:3.9-slim

# Set environment variables to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED True

# Set the working directory in the container
WORKDIR /app

# Install system dependencies. ffmpeg is essential for video processing with moviepy.
# We also clean up the apt cache to reduce the final image size.
RUN apt-get update && apt-get install -y ffmpeg build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy the Python dependencies file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application script into the container
COPY app.py .

# Expose the port that Gunicorn will run on. Google Cloud Run will send requests to this port.
EXPOSE 8080

# Set the command to run the application using Gunicorn.
# This is a production-ready web server.
# --bind 0.0.0.0:$PORT tells Gunicorn to listen on the port provided by Cloud Run.
# --timeout 0 disables the request timeout, which is crucial because video rendering can be a long process.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app
