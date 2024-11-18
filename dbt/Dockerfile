FROM python:3.9-slim

WORKDIR /usr/app/dbt

# Install system dependencies all at once to reduce layers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Keep container running
CMD ["tail", "-f", "/dev/null"]
