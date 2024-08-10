# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /trading_strategies

# Copy the current directory contents into the container at /app
COPY . /trading_strategies

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pydantic

# Install any additional dependencies your code might have (for example, api_connect, EMA_Cross, etc.)
# Assuming EMA_Cross and api_connect are part of the same directory or available in a package
RUN pip install --no-cache-dir -r /trading_strategies/requirements.txt

EXPOSE 80

# Define environment variable
CMD ["python", "main.py"]
