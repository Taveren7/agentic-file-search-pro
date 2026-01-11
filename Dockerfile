FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies using uv
RUN uv pip install --system .

# Expose port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "fs_explorer.server:app", "--host", "0.0.0.0", "--port", "8000"]
