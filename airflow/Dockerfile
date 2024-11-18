FROM apache/airflow:2.7.3

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libpq-dev \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install DBT
RUN pip install dbt-postgres

# Create base DBT directory
RUN mkdir -p /opt/airflow/dbt
