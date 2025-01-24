# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove any existing version of upload_to_s3.py
RUN rm -f /app/upload_to_s3.py

# Copy the rest of the application code into the container
COPY . .

# Command to run the script
CMD ["python", "upload_to_s3.py"]

# NOTE: Instructions to use this Dockerfile:
# docker build -t upload-to-s3 .
# docker run --rm -v {PATH_TO_S3_bucket_update/output_images}:/app/output_images upload-to-s3
# Example of {PATH_TO_S3_bucket_update/output_images}: /Users/cperez/Documents/climateverse/S3_bucket_update/output_images