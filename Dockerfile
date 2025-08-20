# Use Python 3.13.5 slim image as base
FROM python:3.13.5-slim

# Set working directory
WORKDIR /app

# Copy requirements file first for better Docker layer caching
COPY src/app/requirements.txt .

# Install Python dependencies without caching
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

# Copy the application source code (excluding .env via .dockerignore)
COPY src/app/ .

# HEALTHCHECK: give the app 120s to start, then check every 30s with 3s timeout
HEALTHCHECK --interval=30s --timeout=3s --start-period=120s --retries=3 \
    CMD ["python","-c","import socket; with socket.socket() as s: s.settimeout(3); s.connect(('127.0.0.1',8000))"]

# Expose the default Chainlit port
EXPOSE 8000

# Set the entry point to run the Chainlit app
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
