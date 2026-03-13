# docker/Dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY . /app

# Install uv inside container
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && export PATH="/root/.local/bin:$PATH"

# Install dependencies via uv
RUN uv sync

EXPOSE 8000

# Start app via uv
CMD ["uv", "run", "python", "main.py"]