# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /opt

# Install gcc and other necessary build tools
RUN apt-get update && apt-get install -y gcc build-essential

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port the app runs on
EXPOSE ${PORT:-5000}

# Command to run the application using Gunicorn
CMD ["./run_gunicorn.sh"]
