# Use an official Python runtime as the base image
# FROM python:3.9-slim

# FROM python:3.11-slim-bullseye 3.12-alpine⁠

FROM python:3.12-slim
# FROM python:latest

# Set the working directory
WORKDIR /usr/src/app

# Copy application and test files
COPY app/ ./app
COPY tests/ ./tests
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python application
CMD ["python", "app/main.py"]
