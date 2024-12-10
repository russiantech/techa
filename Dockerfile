# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /web

# Copy the current directory contents into the container
COPY . /web

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside the container
EXPOSE 8000

# Run Gunicorn on app.py
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
