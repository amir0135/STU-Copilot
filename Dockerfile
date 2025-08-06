# Use Python 3.13.5 slim image as base
FROM python:3.13.5-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements file first for better Docker layer caching
COPY src/app/requirements.txt .

# Install Python dependencies without caching
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code (excluding .env via .dockerignore)
COPY src/app/ .

# Expose the default Chainlit port
EXPOSE 8000

# Set the entry point to run the Chainlit app
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
