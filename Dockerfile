# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc procps && \
    apt-get clean

# Install supervisord in addition to everything else
RUN apt-get update && apt-get install -y vim cron supervisor && rm -rf /var/lib/apt/lists/*

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files to the container
COPY . /app/
