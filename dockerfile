# Use official slim Python 3.14 image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for uv
RUN apt-get update && \
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install uv inside container and sync dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv sync

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Expose the app port
EXPOSE 8000

# Default command: run main.py via uv
CMD ["uv", "run", "python", "main.py"]