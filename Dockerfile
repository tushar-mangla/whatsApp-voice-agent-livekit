FROM python:3.9-slim-bullseye

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy and install requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install mcp_client
COPY mcp_client ./mcp_client/
RUN pip install -e ./mcp_client/

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8080
EXPOSE 8080



CMD ["python", "server.py"]